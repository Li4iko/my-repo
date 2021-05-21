from .. import loader, utils
from telethon.tl.types import PeerChat as e
from telethon.tl.types import PeerUser as r

class SenderMod(loader.Module):
    """Отправить текст или медиа во все чаты """
    strings = {'name': 'Sender'}

    async def client_ready(self, client, db):
        self.db = db
        if self.db.get("Sender", "log") == None:
            self.db.set("Sender", "log", True)

    async def logcmd(self, message):
        """Используй: .log чтобы включить/отключить логирование после отправлений."""
        log = self.db.get("Sender", "log")
        if log == None or log == False:
            self.db.set("Sender", "log", True)
            await message.edit("<b>Логирование чатов изменено на:</b> <code>True</code>")
            return
        else:
            self.db.set("Sender", "log", False)
            await message.edit("<b>Логирование чатов изменено на:</b> <code>False</code>")
            return

    async def sendcmd(self, message):
        """Используй: .send «текст» чтобы запустить отправку во все чаты."""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        count = 0
        error = 0
        successful = ""
        if not args:
            return await message.edit("<b>Нет аргументов.</b>")
        if args:
            text = args
        await message.edit("<b>Отпраляю...</b>")
        chats = await message.client.get_dialogs()
        for i in chats:
            try:
                chat = i.entity.megagroup
            except:
                None
            if i.name.startswith("friendly-"):
                None
            elif type(i.message.to_id) == r:
                None
            elif chat or type(i.message.to_id) == e:
                await message.client.send_message(i.id, args)
                count += 1
                successful += f"\n{count} • <code>{i.name}</code>"
        log = self.db.get("Sender", "log")
        if log is True:
            return await message.respond(f"<b>Доставлено в {count} чатов:</b>\n{successful}")
        else:
            return await message.respond(f"<b>Доставлено в {count} чатов.</b>")

    async def cchatcmd(self, message):
        """Используй: .cchat «айди чата или ничего» чтобы добавить чат в список."""
        args = utils.get_args_raw(message)
        chats = self.db.get("Sender", "chats", [])
        try:
            if args:
                chatid = message.text.split(' ', 1)[1]
                if args.isnumeric(): chat = await message.client.get_entity(int(chatid))
                else: chat = await message.client.get_entity(chatid)
            else: chat = await message.client.get_entity(message.chat_id)
        except ValueError: return await message.edit("<b>Видимо такого чата нет.</b>")
        if str(chat.id) not in chats:
            chats.append(str(chat.id))
            self.db.set("Sender", "chats", chats)
            await message.edit(f"<b>Чат {chat.title} добавлен в Sender список.</b>")
        else:
            chats.remove(str(chat.id))
            self.db.set("Sender", "chats", chats)
            await message.edit(f"<b>Чат {chat.title} удален из Sender списка.</b>")

    async def cchatscmd(self, message):
        """Используй: .cchats чтобы посмотреть список чатов. Или аргумент «clear» (по желанию)"""
        chats = self.db.get("Sender", "chats", [])
        args = utils.get_args_raw(message)
        chat = ""
        if args == "clear":
            self.db.set("Sender", "chats", {})
            return await message.edit("<b>• Список Sender чатов очищен успешно.</b>")
        for _ in chats:
            chatid = await message.client.get_entity(int(_))
            chat += f"• <a href=\"tg://user?id={int(_)}\">{chatid.title}</a> <b>| ID: [</b><code>{_}</code><b>]</b>\n"
        return await message.edit(f"<b>Всего ( <i>{len(chats)}</i> ) чатов:</b>\n\n{chat}")
        if len(chats) == 0:
            return await message.edit("<b>• Список Sender чатов чист.</b>")

    async def csendcmd(self, message):
        """Используй: .csend «текст» чтобы запустить отправку в чаты из списка."""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        count = 0
        gochat = ""
        if not args:
            return await message.edit("<b>Нет аргументов.</b>")
        if args:
            text = args
        await message.edit("<b>Отпраляю...</b>")
        chats = self.db.get("Sender", "chats", [])
        for i in chats:
            chat = await message.client.get_entity(int(i))
            await message.client.send_message(chat.id, text)
            count += 1
            gochat += f"{count} • <code><a href=\"tg://user?id={int(i)}\">{chat.title}</a></code>\n"
        log = self.db.get("Sender", "log")
        if log is True:
            return await message.respond(f"<b>Доставлено в {count} чатов:</b>\n{gochat}")
        else:
            return await message.respond(f"<b>Доставлено в {count} чатов.</b>")