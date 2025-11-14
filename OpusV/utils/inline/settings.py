from typing import Union

from pyrogram.types import InlineKeyboardButton


def setting_markup(_):
    buttons = [
        [
            InlineKeyboardButton(text=_["ST_B_1"], callback_data="AU"),
            InlineKeyboardButton(text=_["ST_B_3"], callback_data="LG"),
        ],
        [
            InlineKeyboardButton(text=_["ST_B_2"], callback_data="PM"),
        ],
        [
            InlineKeyboardButton(text=_["ST_B_4"], callback_data="VM"),
        ],
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
        ],
    ]
    return buttons


def vote_mode_markup(_, current, mode: Union[bool, str] = None):
    buttons = [
        [
            InlineKeyboardButton(text="Vᴏᴛɪɴɢ ᴍᴏᴅᴇ ➜", callback_data="VOTEANSWER"),
            InlineKeyboardButton(
                text=_["ST_B_5"] if mode == True else _["ST_B_6"],
                callback_data="VOMODECHANGE",
            ),
        ],
        [
            InlineKeyboardButton(text="-2", callback_data="FERRARIUDTI M"),
            InlineKeyboardButton(
                text=f"ᴄᴜʀʀᴇɴᴛ : {current}",
                callback_data="ANSWERVOMODE",
            ),
            InlineKeyboardButton(text="+2", callback_data="FERRARIUDTI A"),
        ],
        [
            InlineKeyboardButton(
                text=_["BACK_BUTTON"],
                callback_data="settings_helper",
            ),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
        ],
    ]
    return buttons


def auth_users_markup(_, status: Union[bool, str] = None):
    buttons = [
        [
            InlineKeyboardButton(text=_["ST_B_7"], callback_data="AUTHANSWER"),
            InlineKeyboardButton(
                text=_["ST_B_8"] if status == True else _["ST_B_9"],
                callback_data="AUTH",
            ),
        ],
        [
            InlineKeyboardButton(text=_["ST_B_1"], callback_data="AUTHLIST"),
        ],
        [
            InlineKeyboardButton(
                text=_["BACK_BUTTON"],
                callback_data="settings_helper",
            ),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
        ],
    ]
    return buttons


def playmode_users_markup(
    _,
    Direct: Union[bool, str] = None,
    Group: Union[bool, str] = None,
    Playtype: Union[bool, str] = None,
):
    buttons = [
        [
            InlineKeyboardButton(text=_["ST_B_10"], callback_data="SEARCHANSWER"),
            InlineKeyboardButton(
                text=_["ST_B_11"] if Direct == True else _["ST_B_12"],
                callback_data="MODECHANGE",
            ),
        ],
        [
            InlineKeyboardButton(text=_["ST_B_13"], callback_data="AUTHANSWER"),
            InlineKeyboardButton(
                text=_["ST_B_8"] if Group == True else _["ST_B_9"],
                callback_data="CHANNELMODECHANGE",
            ),
        ],
        [
            InlineKeyboardButton(text=_["ST_B_14"], callback_data="PLAYTYPEANSWER"),
            InlineKeyboardButton(
                text=_["ST_B_8"] if Playtype == True else _["ST_B_9"],
                callback_data="PLAYTYPECHANGE",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["BACK_BUTTON"],
                callback_data="settings_helper",
            ),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
        ],
    ]
    return buttons

def audio_quality_markup(
    _,
    low: Union[bool, str] = None,
    medium: Union[bool, str] = None,
    high: Union[bool, str] = None,
):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["ST_B_8"].format("✅")
                if low == True
                else _["ST_B_8"].format(""),
                callback_data="PulseAudio",
            )
        ],
        [
            InlineKeyboardButton(
                text=_["ST_B_9"].format("✅")
                if medium == True
                else _["ST_B_9"].format(""),
                callback_data="TrueBass",
            )
        ],
        [
            InlineKeyboardButton(
                text=_["ST_B_10"].format("✅")
                if high == True
                else _["ST_B_10"].format(""),
                callback_data="Dolby",
            )
        ],
        [
            InlineKeyboardButton(
                text=_["BACK_BUTTON"],
                callback_data="settingsback_helper",
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"], callback_data="close"
            ),
        ],
    ]
    return buttons

def cleanmode_settings_markup(
    _,
    status: Union[bool, str] = None,
    dels: Union[bool, str] = None,
):
    buttons = [
        [
            InlineKeyboardButton(text=_["ST_B_7"], callback_data="CMANSWER"),
            InlineKeyboardButton(
                text=_["ST_B_19"] if status == True else _["ST_B_20"],
                callback_data="CLEANMODE",
            ),
        ],
        [
            InlineKeyboardButton(text=_["ST_B_31"], callback_data="COMMANDANSWER"),
            InlineKeyboardButton(
                text=_["ST_B_19"] if dels == True else _["ST_B_20"],
                callback_data="COMMANDELMODE",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["BACK_BUTTON"],
                callback_data="settingsback_helper",
            ),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
        ],
    ]
    return buttons

def video_quality_markup(
    _,
    low: Union[bool, str] = None,
    medium: Union[bool, str] = None,
    high: Union[bool, str] = None,
):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["ST_B_11"].format("✅")
                if low == True
                else _["ST_B_11"].format(""),
                callback_data="FHD-1K",
            )
        ],
        [
            InlineKeyboardButton(
                text=_["ST_B_12"].format("✅")
                if medium == True
                else _["ST_B_12"].format(""),
                callback_data="QuadHD-2K",
            )
        ],
        [
            InlineKeyboardButton(
                text=_["ST_B_13"].format("✅")
                if high == True
                else _["ST_B_13"].format(""),
                callback_data="UltraHD-4K",
            )
        ],
        [
            InlineKeyboardButton(
                text=_["BACK_BUTTON"],
                callback_data="settingsback_helper",
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"], callback_data="close"
            ),
        ],
    ]
    return buttons
