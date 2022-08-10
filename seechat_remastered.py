from .. import loader, utils
from datetime import datetime, date, time
from asyncio import sleep
import os, io, asyncio, pytz, requests

@loader.tds
class SeeChatReMod(loader.Module):
    """Логирует все переписки."""
    strings={"name": "SeeChat Remastered"}

    async def client_ready(self, message, db):
        self.db=db
        self.db.set("SeeChat", "seechat", True)
        di = "SeeChat/"
        if os.path.exists(di):
            pass
        else:
            os.mkdir(di)

    async def seechatcmd(self, message):
        """Используй: .seechat | чтобы включить слежку во всех лс чатах."""
        me = await message.client.get_me()
        seechat = self.db.get("SeeChat", "seechat")
        if seechat is not True:
            await message.edit("[SeeChat] Включен успешно.")
            self.db.set("SeeChat", "seechat", True)
        else:
            await message.edit("[SeeChat] Выключен успешно.")
            self.db.set("SeeChat", "seechat", False)

    async def setchatcmd(self, message):
        """Используй: .setchat | чтобы установить этот чат как чат логов."""
        di = "SeeChat/"
        if os.path.exists(di):
            pass
        else:
            os.mkdir(di)
        chat = await message.client.get_entity(message.to_id)
        self.db.set("SeeChat", "log", str(chat.id))
        await message.edit(f"<b>Этот чат был установлен как чат для логов.</b>")

    async def seechatscmd(self, message):
        """Используй: .seechats | чтобы посмотреть список людей в логах."""
        me = await message.client.get_me()
        await message.edit("ща покажу")
        chats = ""
        number = 0
        for _ in os.listdir("SeeChat/"):
            number += 1
            try:
                user = await message.client.get_entity(int(_[:-4]))
            except: pass
            if not user.deleted:
                chats += f"{number} • <a href=tg://user?id={user.id}>{user.first_name}</a> ID: [<code>{user.id}</code>]\n"
            else:
                chats += f"{number} • Удалённый аккаунт ID: [<code>{user.id}</code>]\n"
        await message.edit("<b>Пользователи которые есть в логах:</b>\n\n" + chats)

    async def gseecmd(self, message):
        """Используй: .gsee «айди» | чтобы достать файл логов."""
        me = await message.client.get_me()
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit("<b>Где аргументы дыбил.</b>")
        try:
            user = await message.client.get_entity(int(args))
            await message.edit(f"<b>Файл переписки с: <code>{user.first_name}</code></b>")
            await message.client.send_file(message.to_id, f"SeeChat/{args}.txt")
        except ValueError: return await message.edit("<b>Файл не найден.</b>")

    async def delseecmd(self, message):
        """Используй: .delsee «айди» | чтобы удалить файл логов."""
        me = await message.client.get_me()
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit("<b>Где аргументы дыбил.</b>")
        if args == "all":
            os.system("rm -rf SeeChat/*")
            await message.edit("<b>Все файлы переписок были успешно удалены.</b>")
        else:
            try:
                user = await message.client.get_entity(int(args))
                await message.edit(f"<b>Был удален файл переписки с: <code>{user.first_name}</code></b>")
                os.remove(f"SeeChat/{args}.txt")
            except ValueError: return await message.edit("<b>Файл не найден.</b>")


    async def excseecmd(self, message):
        """Используй: .excsee «айди» | чтобы добавить/исключить пользователя в исключение логов."""
        me = await message.client.get_me()
        exception = self.db.get("SeeChat", "exception", [])
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit("<b>Где аргументы дыбил.</b>")
        if args == "clear":
            self.db.set("SeeChat", "exception", [])
            return await message.edit("<b>Список исключений успешно очищен.</b>")
        user = await message.client.get_entity(int(args))
        if str(user.id) not in exception:
            exception.append(str(user.id))
            await message.edit(f"<b>{user.first_name}, был добавлен в список исключений.</b>")
            os.remove(f"SeeChat/{user.id}.txt")
        else:
            exception.remove(str(user.id))
            await message.edit(f"<b>{user.first_name}, был удален из списка исключений.</b>")
        self.db.set("SeeChat", "exception", exception)
    
    async def exclistcmd(self, message):
        """Используй: .exclist | чтобы посмотреть список исключений."""
        me = await message.client.get_me()
        exception = self.db.get("SeeChat", "exception", [])
        number = 0
        users = "" 
        for _ in exception:
            user = await message.client.get_entity(int(_))
            number += 1
            users += f"{number} • <a href=tg://user?id={user.id}>{user.first_name}</a> ID: [<code>{user.id}</code>]\n"
        await message.edit("<b>Список исключений:</b>\n\n" + users)

    async def watcher(self, message):
        me = await message.client.get_me()
        seechat = self.db.get("SeeChat", "seechat")
        exception = self.db.get("SeeChat", "exception", [])
        log = self.db.get("SeeChat", "log", str(me.id))
        chat = await message.client.get_entity(int(log))
        timezone = "Europe/Kiev"
        vremya = datetime.now(pytz.timezone(timezone)).strftime("[%Y-%m-%d %H:%M:%S]")
        user = await message.client.get_entity(message.chat_id)
        userid = str(user.id)
        di = "SeeChat/"
        if os.path.exists(di):
            pass
        else:
            os.mkdir(di)
        if message.is_private:
            if seechat is not False:
                if userid not in exception:
                    if not user.bot and not user.verified:
                        if message.text.lower():
                            file = open(f"SeeChat/{user.id}.txt", "a", encoding='utf-8')
                            if message.sender_id != me.id: file.write(f"{user.first_name} >> {message.text} << {vremya}\n\n")
                            else: file.write(f"{me.first_name} >> {message.text} << {vremya}\n\n")
                        if message.photo:
                            if message.sender_id == me.id:
                                return
                            else:
                                file = io.BytesIO()
                                file.name = message.file.name or f"SeeChat{message.file.ext}"
                                await message.client.download_file(message, file)
                                file.seek(0)
                                await message.client.send_message(chat.id, f"<b>Картинка от</b> <code>{user.first_name}</code>:")
                                await message.client.send_file(chat.id, file, force_document=False)
                        if message.voice:
                            if message.sender_id == me.id:
                                return
                            await message.forward_to(chat.id)
                        elif message.video_note:
                            if message.sender_id == me.id:
                                return
                            await message.forward_to(chat.id)
                        elif message.video:
                            if message.sender_id == me.id:
                                return
                            with open(f'seechat{user.from_id}.avi', "wb") as out_file:
                                out_file.write(await message.client.download_file(message,bytes))
                            await message.client.send_file(chat.id, f'seechat{user.from_id}.avi')
                            os.remove(f'seechat{user.from_id}.avi')
