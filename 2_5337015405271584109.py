from .. import loader, utils
from telethon.errors import UserAdminInvalidError
from telethon.tl.types import ChannelParticipantsAdmins
from telethon.tl.types import ChatBannedRights
from telethon.tl.functions.channels import EditBannedRequest

BANNED_RIGHTS = ChatBannedRights(until_date=None,
                                 view_messages=True,
                                 send_messages=True,
                                 send_media=True,
                                 send_stickers=True,
                                 send_gifs=True,
                                 send_games=True,
                                 send_inline=True,
                                 embed_links=True)

@loader.tds
class AdminMod(loader.Module):
    
    strings = {"name": "Users"}

    async def client_ready(self, message, db):
        self.db=db

    async def getadminscmd(self, message):
        """Импортировать всех юзеров из чата."""
        await message.edit("Считаю")
        self.db.set("Users", "list", [])
        me = await message.client.get_me()
        admins = await message.client.get_participants(message.chat_id)
        spisok = self.db.get("Users", "list", [])
        for user in admins:
            if not user.bot and not user.deleted:
                admin = admins[admins.index((await message.client.get_entity(user.id)))].participant
                if user.id == me.id:
                    continue
                spisok.append(str(user.id))
        await message.edit("Все пользователи с этого чата успешно импортированы.")

    async def getadmcmd(self, message):
        """Последний импорт"""
        await message.edit("Считаю")
        spisok = self.db.get("Users", "list", [])
        users = ""
        try:
            for i in spisok:
                user = await message.client.get_entity(int(i))
                users += f"• {user.first_name}\n"
            await message.edit(f"Последний импорт:\n\n{users}")
        except: return await message.edit("Список пуст.")

    async def sbancmd(self, message):
        """
        Выдать бан всем импортированым людям.
        .sban «айди чата где нужно забанить»
        """
        await message.edit("Баню всех нахуй!1!!")
        spisok = self.db.get("Users", "list", [])
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit("Нет аргументов.")
        try:
            chat = await message.client.get_entity(int(args))
        except ValueError: return await message.edit("Такой чат не найден.")
        try:
            for i in spisok:
                user = await message.client.get_entity(int(i))
                await message.client(EditBannedRequest(chat.id, user.id, BANNED_RIGHTS))
            await message.edit(f"{len(i)} людей было забанено в чате {chat.title}")
        except UserAdminInvalidError: return await message.edit("Не хватает прав.")