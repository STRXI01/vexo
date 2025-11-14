import time
from pyrogram.types import InlineKeyboardButton
from OpusV.utils.formatters import time_to_seconds

LAST_UPDATE_TIME = {}


def track_markup(_, videoid, user_id, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ]
    ]


def should_update_progress(chat_id):
    now = time.time()
    last = LAST_UPDATE_TIME.get(chat_id, 0)
    if now - last >= 6:
        LAST_UPDATE_TIME[chat_id] = now
        return True
    return False


def generate_progress_bar(played_sec, duration_sec):
    if duration_sec == 0:
        return "•။‌||၊|။|၊|၊|•"

    percentage = min((played_sec / duration_sec) * 100, 100)
    bar_length = 12
    filled = int(round(bar_length * percentage / 100))  # Fixed: use 100 instead of 70
    
    base_pattern = "•၊||၊|၊|၊|၊•"
    progress_bar = ""
    for i in range(len(base_pattern)):
        if i < filled:
            progress_bar += "°"
        else:
            progress_bar += base_pattern[i]
    
    return progress_bar


def control_buttons(_, chat_id):
    return [[
        InlineKeyboardButton(text="▶", callback_data=f"ADMIN Resume|{chat_id}"),
        InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
        InlineKeyboardButton(text="⇄", callback_data=f"ADMIN Replay|{chat_id}"),
        InlineKeyboardButton(text="⏭", callback_data=f"ADMIN Skip|{chat_id}"),
        InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
    ]]


def stream_markup_timer(_, chat_id, played, dur):
    if not should_update_progress(chat_id):
        return None

    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    bar = generate_progress_bar(played_sec, duration_sec)

    return (
        [[InlineKeyboardButton(text=f"{played} {bar} {dur}", callback_data="GetTimer")]] +
        control_buttons(_, chat_id)
    )


def stream_markup(_, chat_id):
    return control_buttons(_, chat_id)


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"OpusPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}"
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"OpusPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}"
            ),
        ]
    ]
    return buttons


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
            )
        ]
    ]


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    short_query = query[:20]
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=f"slider B|{query_type}|{short_query}|{user_id}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=f"slider F|{query_type}|{short_query}|{user_id}|{channel}|{fplay}",
            ),
        ],
    ]
