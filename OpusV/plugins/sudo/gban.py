import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from OpusV import app
from OpusV.misc import SUDOERS
from OpusV.utils import get_readable_time
from OpusV.utils.database import (
    add_banned_user,
    get_banned_count,
    get_banned_users,
    get_served_chats,
    is_banned_user,
    remove_banned_user,
)
from OpusV.utils.decorators.language import language
from OpusV.utils.extraction import extract_user
from config import BANNED_USERS


@app.on_message(filters.command(["gban", "globalban"]) & SUDOERS)
@language
async def global_ban(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
    user = await extract_user(message)
    if user.id == message.from_user.id:
        return await message.reply_text(_["gban_1"])
    elif user.id == app.id:
        return await message.reply_text(_["gban_2"])
    elif user.id in SUDOERS:
        return await message.reply_text(_["gban_3"])
    is_gbanned = await is_banned_user(user.id)
    if is_gbanned:
        return await message.reply_text(_["gban_4"].format(user.mention))
    if user.id not in BANNED_USERS:
        BANNED_USERS.add(user.id)
    served_chats = []
    chats = await get_served_chats()
    for chat in chats:
        served_chats.append(int(chat["chat_id"]))
    time_expected = get_readable_time(len(served_chats))
    mystic = await message.reply_text(_["gban_5"].format(user.mention, time_expected))
    number_of_chats = 0
    for chat_id in served_chats:
        try:
            await app.ban_chat_member(chat_id, user.id)
            number_of_chats += 1
        except FloodWait as fw:
            await asyncio.sleep(int(fw.value))
        except:
            continue
    await add_banned_user(user.id)
    await message.reply_text(
        _["gban_6"].format(
            app.mention,
            message.chat.title,
            message.chat.id,
            user.mention,
            user.id,
            message.from_user.mention,
            number_of_chats,
        )
    )
    await mystic.delete()


@app.on_message(filters.command(["ungban"]) & SUDOERS)
@language
async def global_un(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
    user = await extract_user(message)
    is_gbanned = await is_banned_user(user.id)
    if not is_gbanned:
        return await message.reply_text(_["gban_7"].format(user.mention))
    if user.id in BANNED_USERS:
        BANNED_USERS.remove(user.id)
    served_chats = []
    chats = await get_served_chats()
    for chat in chats:
        served_chats.append(int(chat["chat_id"]))
    time_expected = get_readable_time(len(served_chats))
    mystic = await message.reply_text(_["gban_8"].format(user.mention, time_expected))
    number_of_chats = 0
    for chat_id in served_chats:
        try:
            await app.unban_chat_member(chat_id, user.id)
            number_of_chats += 1
        except FloodWait as fw:
            await asyncio.sleep(int(fw.value))
        except:
            continue
    await remove_banned_user(user.id)
    await message.reply_text(_["gban_9"].format(user.mention, number_of_chats))
    await mystic.delete()


@app.on_message(filters.command(["gbannedusers", "gbanlist"]) & SUDOERS)
@language
async def gbanned_list(client, message: Message, _):
    counts = await get_banned_count()
    if counts == 0:
        return await message.reply_text(_["gban_10"])
    mystic = await message.reply_text(_["gban_11"])
    msg = _["gban_12"]
    count = 0
    users = await get_banned_users()
    for user_id in users:
        count += 1
        try:
            user = await app.get_users(user_id)
            user = user.first_name if not user.mention else user.mention
            msg += f"{count}➤ {user}\n"
        except Exception:
            msg += f"{count}➤ {user_id}\n"
            continue
    if count == 0:
        return await mystic.edit_text(_["gban_10"])
    else:
        return await mystic.edit_text(msg)


@app.on_message(filters.command(["ungbanall"]) & SUDOERS)
@language
async def global_unban_all(client, message: Message, _):
    # Get all banned users
    banned_users_list = await get_banned_users()
    if not banned_users_list:
        return await message.reply_text("❌ No users are currently globally banned.")
    
    # Get served chats
    served_chats = []
    chats = await get_served_chats()
    for chat in chats:
        served_chats.append(int(chat["chat_id"]))
    
    total_banned_users = len(banned_users_list)
    time_expected = get_readable_time(len(served_chats) * total_banned_users)
    
    mystic = await message.reply_text(
        f"🔄 Starting mass unban process...\n"
        f"👥 Users to unban: {total_banned_users}\n"
        f"Chats to process: {len(served_chats)}\n"
        f"Estimated time: {time_expected}"
    )
    
    total_unbanned = 0
    failed_unbans = 0
    
    for user_id in banned_users_list:
        # Remove from BANNED_USERS set
        if user_id in BANNED_USERS:
            BANNED_USERS.remove(user_id)
        
        # Remove from database
        await remove_banned_user(user_id)
        
        # Unban from all served chats
        user_unbanned_count = 0
        for chat_id in served_chats:
            try:
                await app.unban_chat_member(chat_id, user_id)
                user_unbanned_count += 1
            except FloodWait as fw:
                await asyncio.sleep(int(fw.value))
            except:
                failed_unbans += 1
                continue
        
        if user_unbanned_count > 0:
            total_unbanned += 1
        
        # Update progress every 10 users
        if total_unbanned % 10 == 0:
            try:
                await mystic.edit_text(
                    f"🔄 Progress: {total_unbanned}/{total_banned_users} users processed...\n"
                    f"⏱️Estimated remaining: {get_readable_time((total_banned_users - total_unbanned) * len(served_chats) // 10)}"
                )
            except:
                pass
    
    # Final summary
    summary_text = (
        f"Mass Unban Complete\n\n"
        f"👥 Total users processed: {total_banned_users}\n"
        f"✅ Successfully unbanned: {total_unbanned}\n"
        f"Failed operations: {failed_unbans}\n"
        f"Chats processed: {len(served_chats)}\n"
        f"Requested by: {message.from_user.mention}"
    )
    
    await mystic.edit_text(summary_text)
