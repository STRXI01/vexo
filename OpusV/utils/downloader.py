import asyncio
import httpx
import aiofiles
import os
import re
from typing import Optional, Dict, Union, List
from yt_dlp import YoutubeDL

cookies_file = "OpusV/resources/cookies.txt"
download_folder = "downloads"
os.makedirs(download_folder, exist_ok=True)


def extract_video_id(link: str) -> str:
    if "v=" in link:
        return link.split("v=")[-1].split("&")[0]
    return link.split("/")[-1].split("?")[0]


def safe_filename(name: str) -> str:
    return re.sub(r"[\\/*?\"<>|]", "_", name).strip()[:100]


def file_exists(video_id: str, file_type: str = "audio") -> Optional[str]:
    extensions = ["mp3"] if file_type == "audio" else ["mp4", "mkv", "webm"]

    for ext in extensions:
        path = f"{download_folder}/{video_id}.{ext}"
        if os.path.exists(path):
            return path

        for file in os.listdir(download_folder):
            if file.startswith(video_id) and file.endswith(f".{ext}"):
                return f"{download_folder}/{file}"

    return None


async def api_download(link: str, file_type: str = "audio") -> Optional[str]:
    if "youtube.com" not in link and "youtu.be" not in link:
        video_id = extract_video_id(link)
        link = f"https://www.youtube.com/watch?v={video_id}"
    video_id = extract_video_id(link)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/129.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/html, */*; q=0.01",
        "Referer": "https://www.clipto.com/",
        "Origin": "https://www.clipto.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }

    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True, headers=headers) as client:
            # Pick API based on type
            if file_type == "audio":
                api_url = f"https://alphaytapi.vercel.app/api/dl?url={link}"
                resp = await client.get(api_url, follow_redirects=True)
                if resp.status_code != 200:
                    print(f"[API ERROR] Audio API failed ({resp.status_code}): {resp.text}")
                    return None
                data = resp.json()
                download_url = data.get("link")
                if not download_url:
                    print("[API ERROR] Audio API: missing 'link' in response")
                    return None
                ext = "mp3"
            else:
                api_url = f"https://apex.srvopus.workers.dev/arytmp?direct&id={video_id}&format=mp4"
                resp = await client.get(api_url, follow_redirects=True)
                if resp.status_code != 200:
                    print(f"[API ERROR] Video API failed ({resp.status_code}): {resp.text}")
                    return None
                data = resp.json()
                if data.get("status") != "success":
                    print(f"[API ERROR] Video API: non-success response {data}")
                    return None
                download_url = data.get("download_url")
                if not download_url:
                    print("[API ERROR] Video API: missing 'download_url' in response")
                    return None
                ext = "mp4"

            path = f"{download_folder}/{video_id}.{ext}"

            try:
                # Streamed download with redirect support
                async with client.stream("GET", download_url, headers=headers, follow_redirects=True) as file_resp:
                    if file_resp.status_code != 200:
                        print(f"[API ERROR] Stream failed ({file_resp.status_code}): {file_resp.text}")
                        return None
                    async with aiofiles.open(path, "wb") as f:
                        async for chunk in file_resp.aiter_bytes(chunk_size=8192):
                            await f.write(chunk)
            except Exception:
                # Fallback: direct GET with redirect follow
                file_resp = await client.get(download_url, headers=headers, follow_redirects=True)
                if file_resp.status_code != 200:
                    print(f"[API ERROR] Fallback full download failed ({file_resp.status_code}): {file_resp.text}")
                    return None
                async with aiofiles.open(path, "wb") as f:
                    await f.write(file_resp.content)

            # Validate output file
            if not os.path.exists(path) or os.path.getsize(path) < 1024 * 100:
                if os.path.exists(path):
                    os.remove(path)
                print(f"[API ERROR] Invalid or too small file: {path}")
                return None

            return path

    except Exception as e:
        print(f"[API ERROR] Exception: {str(e)}")
        return None


def _download_ytdlp(link: str, opts: Dict) -> Union[None, str, List[str]]:
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(link, download=False)
            if "entries" in info:
                results = []
                ydl.download([link])
                for entry in info["entries"]:
                    vid = entry.get("id")
                    if not vid:
                        continue
                    for file in os.listdir(download_folder):
                        if file.startswith(vid):
                            results.append(f"{download_folder}/{file}")
                return results

            vid = info.get("id")
            ext = "mp3" if "postprocessors" in opts else "mp4"
            expected_filename = f"{download_folder}/{vid}.{ext}"
            ydl.download([link])

            if os.path.exists(expected_filename):
                return expected_filename

            for file in os.listdir(download_folder):
                if file.startswith(vid):
                    return f"{download_folder}/{file}"

            return None
    except Exception:
        return None


async def yt_dlp_download(link: str, type: str, format_id: str = None) -> Union[None, str, List[str]]:
    loop = asyncio.get_running_loop()

    def is_restricted() -> bool:
        return os.path.exists(cookies_file)

    common_opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": False,
        "geo_bypass": True,
        "geo_bypass_country": "IN",
        "concurrent_fragment_downloads": 32,
    }

    if type in ["audio", "song_audio"]:
        opts = {
            **common_opts,
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "cookiefile": cookies_file if is_restricted() else None,
            "outtmpl": f"{download_folder}/%(id)s.%(ext)s",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }
    else:
        format_str = "best[height<=720]/bestvideo[height<=720]+bestaudio/best[height<=720]"
        if format_id:
            format_str = format_id
        opts = {
            **common_opts,
            "format": format_str,
            "cookiefile": cookies_file if is_restricted() else None,
            "outtmpl": f"{download_folder}/%(id)s.%(ext)s",
            "merge_output_format": "mp4",
            "prefer_ffmpeg": True,
        }

    return await loop.run_in_executor(None, _download_ytdlp, link, opts)


async def download_audio_concurrent(link: str) -> Union[None, str, List[str]]:
    existing = file_exists(extract_video_id(link), "audio")
    if existing:
        return existing

    try:
        api_result = await asyncio.wait_for(api_download(link, file_type="audio"), timeout=40)
        if api_result:
            return api_result
    except Exception:
        pass

    try:
        yt_result = await asyncio.wait_for(yt_dlp_download(link, type="audio"), timeout=60)
        return yt_result
    except Exception:
        return None


async def download_video_concurrent(link: str) -> Union[None, str, List[str]]:
    existing = file_exists(extract_video_id(link), "video")
    if existing:
        return existing

    try:
        api_result = await asyncio.wait_for(api_download(link, file_type="video"), timeout=30)
        if api_result:
            return api_result
    except Exception:
        pass

    try:
        yt_result = await asyncio.wait_for(yt_dlp_download(link, type="video"), timeout=60)
        return yt_result
    except Exception:
        return None
