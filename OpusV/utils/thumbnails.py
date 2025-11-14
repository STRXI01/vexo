import os
import re
import textwrap
import numpy as np
import aiofiles
import aiohttp
from PIL import (
    Image,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageFont,
)
from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    ratio = min(widthRatio, heightRatio)
    newWidth = int(image.size[0] * ratio)
    newHeight = int(image.size[1] * ratio)
    try:
        resample = Image.Resampling.LANCZOS
    except AttributeError:
        resample = Image.ANTIALIAS
    return image.resize((newWidth, newHeight), resample)


def get_dominant_color(image):
    image = image.convert('RGB').resize((50, 50))
    pixels = np.array(image).reshape(-1, 3)
    avg_color = tuple(pixels.mean(axis=0).astype(int))
    if sum(avg_color) < 200:
        return tuple(min(255, int(c * 1.5)) for c in avg_color)
    return avg_color

def get_contrasting_color(bg_color):
    luminance = (0.299 * bg_color[0] + 0.587 * bg_color[1] + 0.114 * bg_color[2])
    return (255, 255, 255) if luminance < 128 else (50, 50, 50)


async def get_thumb(videoid):
    final_path = f"cache/{videoid}.png"
    if os.path.isfile(final_path):
        return final_path

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        result_data = await results.next()
        if not result_data.get("result"):
            return YOUTUBE_IMG_URL

        result = result_data["result"][0]
        title = re.sub(r"\W+", " ", result.get("title", "Unknown Title")).title()
        duration = result.get("duration", "00:00")
        thumbnail_url = result["thumbnails"][0]["url"].split("?")[0]
        views = result.get("viewCount", {}).get("short", "0 views")
        channel = result.get("channel", {}).get("name", "Unknown Channel")

        os.makedirs("cache", exist_ok=True)
        thumb_path = f"cache/thumb{videoid}.png"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as resp:
                async with aiofiles.open(thumb_path, "wb") as f:
                    await f.write(await resp.read())

        try:
            youtube = Image.open(thumb_path)
        except:
            os.remove(thumb_path) if os.path.exists(thumb_path) else None
            return YOUTUBE_IMG_URL

        # Dominant color
        bar_color = get_dominant_color(youtube)
        contrast_color = get_contrasting_color(bar_color)

        # --- Background setup ---
        bg = changeImageSize(1280, 720, youtube.copy()).convert("RGBA")
        bg = bg.filter(ImageFilter.BoxBlur(22))  # stronger blur for deeper feel
        bg = ImageEnhance.Brightness(bg).enhance(0.55)  # darker overall tone
        bg = ImageEnhance.Color(bg).enhance(0.8)  # desaturate slightly for cinematic look

        # Black overlay to deepen the mix
        dark_overlay = Image.new("RGBA", bg.size, (0, 0, 0, 120))
        bg = Image.alpha_composite(bg, dark_overlay)

        # --- Bottom gradient (to keep lower text visible) ---
        gradient = Image.new("L", (1, bg.height))
        for y in range(bg.height):
            gradient.putpixel((0, y), int(255 * (y / bg.height)))
        alpha = gradient.resize(bg.size)
        overlay = Image.new("RGBA", bg.size, (0, 0, 0, 130))
        bg = Image.composite(overlay, bg, alpha)

        # --- Center thumbnail (v2 enhanced) ---
        center_thumb = changeImageSize(940, 420, youtube.copy()).convert("RGBA")
        thumb_pos = ((bg.width - center_thumb.width) // 2, 90)  # perfectly centered horizontally

        # Slight enhancement for crisp look
        enhancer_brightness = ImageEnhance.Brightness(center_thumb).enhance(1.15)
        enhancer_contrast = ImageEnhance.Contrast(enhancer_brightness).enhance(1.25)
        center_thumb = enhancer_contrast

        # --- Enhanced soft glow around thumbnail ---
        glow_layer = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        glow_size = (center_thumb.width + 90, center_thumb.height + 90)
        glow = Image.new("RGBA", glow_size, (255, 255, 255, 70))
        glow = glow.filter(ImageFilter.GaussianBlur(38))
        glow_pos = (thumb_pos[0] - 45, thumb_pos[1] - 45)
        glow_layer.paste(glow, glow_pos, glow)
        bg = Image.alpha_composite(bg, glow_layer)

        # --- Masked rounded rectangle for thumbnail ---
        mask = Image.new("L", center_thumb.size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle([0, 0, center_thumb.width, center_thumb.height], radius=40, fill=255)
        bg.paste(center_thumb, thumb_pos, mask)

        # --- Font loaders ---
        def safe_font(path, size):
            try:
                return ImageFont.truetype(path, size)
            except:
                return ImageFont.load_default()

        font_title = safe_font("OpusV/resources/font.ttf", 32)
        font_small = safe_font("OpusV/resources/font2.ttf", 28)
        font_brand = safe_font("OpusV/resources/font.ttf", 40)

        draw = ImageDraw.Draw(bg)

        # --- Vertical progress bar ---
        bar_width = 15
        bar_height = center_thumb.height
        bar_radius = 12
        bar_x = thumb_pos[0] - 60
        bar_y = thumb_pos[1]

        # Bar background
        draw.rounded_rectangle(
            [bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
            radius=bar_radius,
            fill=(100, 100, 100, 150)
        )

        # Played portion
        played_ratio = 0.25  # Example static
        fill_height = int(bar_height * played_ratio)
        draw.rounded_rectangle(
            [bar_x, bar_y + bar_height - fill_height, bar_x + bar_width, bar_y + bar_height],
            radius=bar_radius,
            fill=bar_color
        )

        # --- Duration texts (adjusted further apart) ---
        draw.text((bar_x - 50, bar_y - 40), duration[:23], fill="white", font=font_small)  # total duration higher
        draw.text((bar_x - 50, bar_y + bar_height + 10), "00:25", fill="white", font=font_small)  # ongoing lower

        # --- Text below thumbnail ---
        text_left = thumb_pos[0]
        text_top = thumb_pos[1] + center_thumb.height + 15
        title_short = textwrap.shorten(title, width=50, placeholder="...")
        draw.text((text_left, text_top), title_short, fill="white", font=font_title, stroke_width=1, stroke_fill="black")
        draw.text((text_left, text_top + 40), f"{channel} | {views[:23]}", fill="white", font=font_small, stroke_width=1, stroke_fill="black")

        # --- Branding (closer but not overlapping) ---
        rec_text = "Kawai Heals"
        rec_bbox = draw.textbbox((0, 0), rec_text, font=font_brand)
        rec_w = rec_bbox[2] - rec_bbox[0]
        rec_h = rec_bbox[3] - rec_bbox[1]
        rec_x = thumb_pos[0] + center_thumb.width + 35  # moved closer but safe gap
        rec_y = thumb_pos[1] + (center_thumb.height // 2) - (rec_h // 2)
        draw.text((rec_x, rec_y), rec_text, fill="white", font=font_brand)

        # Clean temp
        try:
            os.remove(thumb_path)
        except:
            pass

        bg.save(final_path, format="PNG")
        return final_path

    except Exception as e:
        print("Thumb error:", e)
        return YOUTUBE_IMG_URL
