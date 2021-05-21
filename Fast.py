from .. import loader, utils
import requests
from telethon.tl.types import (ChatAdminRights, ChatBannedRights, PeerChannel)
from telethon.tl.functions.channels import (EditAdminRequest, EditBannedRequest)
from telethon.errors import (ChatAdminRequiredError, UserAdminInvalidError)

BANNED_RIGHTS = ChatBannedRights(until_date=None,
                                 view_messages=True,
                                 send_messages=True,
                                 send_media=True,
                                 send_stickers=True,
                                 send_gifs=True,
                                 send_games=True,
                                 send_inline=True,
                                 embed_links=True)

UNBAN_RIGHTS = ChatBannedRights(until_date=None,
                                view_messages=False,
                                send_messages=None,
                                send_media=None,
                                send_stickers=None,
                                send_gifs=None,
                                send_games=None,
                                send_inline=None,
                                embed_links=None)

@loader.tds
class FastBanMod(loader.Module):
    """Выдать быстрый бан в чате [PRIVATE] creator seen"""
    strings = {"name": "FastBan"}

    async def client_ready(self, message, db):
        self.db=db

    async def chatcmd(self, message):
        """Добавить чат в список"""
        args = utils.get_args_raw(message)
        chats = self.db.get("FastBan", "chats", [])
        try:
            if args:
                chatid = message.text.split(' ', 1)[1]
                if args.isnumeric(): chat = await message.client.get_entity(int(chatid))
                else: chat = await message.client.get_entity(chatid)
            else: chat = await message.client.get_entity(message.chat_id)
        except ValueError: return await message.edit("<b>Видимо такого чата нет.</b>")
        if str(chat.id) not in chats:
            chats.append(str(chat.id))
            self.db.set("FastBan", "chats", chats)
            await message.edit(f"<b>Чат {chat.title} добавлен в список.</b>")
        else:
            chats.remove(str(chat.id))
            self.db.set("FastBan", "chats", chats)
            await message.edit(f"<b>Чат {chat.title} удален из списка.</b>")

    async def chatscmd(self, message):
        """Посмотреть список чатов"""
        chats = self.db.get("FastBan", "chats", [])
        args = utils.get_args_raw(message)
        chat = ""
        if args == "clear":
            self.db.set("FastBan", "chats", [])
            return await message.edit("<b>• Список чатов очищен успешно.</b>")
        for _ in chats:
            chatid = await message.client.get_entity(int(_))
            chat += f"• <a href=\"tg://user?id={int(_)}\">{chatid.title}</a> <b>| ID: [</b><code>{_}</code><b>]</b>\n"
        await message.edit(f"<b>Список чатов:</b>\n\n{chat}")
        if len(chats) == 0:
            return await message.edit("<b>• Список чист.</b>")

    async def fbancmd(self, message):
        """Забанить @ или id или reply, во всех чатах из списка"""
        chats = self.db.get("FastBan", "chats", [])
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not args and not reply:
            return await message.edit("<b>Нет аргументов или реплая.</b>")
        try:
            if args:
                if args.isnumeric(): user = await message.client.get_entity(int(args))
                else: user = await message.client.get_entity(args)
            else: user = await message.client.get_entity(reply.sender_id)
        except ValueError: await message.edit("<b>Видимо такого пользователя не существует.</b>")
        try:
            for _ in chats:
                chatid = await message.client.get_entity(int(_))
                await message.client(EditBannedRequest(chatid.id, user.id, BANNED_RIGHTS))
            await message.edit(f"<b>{user.first_name} забанен во всех чатах из списка.</b>")
        except UserAdminInvalidError: return await message.edit("<b>У меня нет достаточных прав.</b>")


    async def unfbancmd(self, message):
        """Разбанить @ или id или reply, во всех чатах из списка"""
        chats = self.db.get("FastBan", "chats", [])
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not args and not reply:
            return await message.edit("<b>Нет аргументов или реплая.</b>")
        try:
            if args:
                if args.isnumeric(): user = await message.client.get_entity(int(args))
                else: user = await message.client.get_entity(args)
            else: user = await message.client.get_entity(reply.sender_id)
        except ValueError: await message.edit("<b>Видимо такого пользователя не существует.</b>")
        for _ in chats:
            chatid = await message.client.get_entity(int(_))
            await message.client(EditBannedRequest(chatid.id, user.id, UNBAN_RIGHTS))
        await message.edit(f"<b>{user.first_name} разбанен во всех чатах из списка.</b>")