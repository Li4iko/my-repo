from .. import loader, utils

class MafiaMod(loader.Module):
    """Модуль регистрации на подарки в True Mafia News. """
    strings = {'name': 'Mafia'}

    async def client_ready(self, client, db):
        self.db = db
        self.db.set("Mafia", "status", True)

    async def mdcmd(self, message):
        """Используй: .md чтобы включить ловлю розыгрышей от Мафии."""
        status = self.db.get("Mafia", "status")
        if status is not True:
            await message.edit("<b>Ловля подарков:</b> <code>Включена</code>")
            self.db.set("Mafia", "status", True)
        else:
            await message.edit("<b>Ловля подарков:</b> <code>Отключена</code>")
            self.db.set("Mafia", "status", False)

    async def watcher(self, message):
        status = self.db.get("Mafia", "status")
        me = (await message.client.get_me()).id
        if status:
            if message.chat_id == -1001169391811:
                click = (await message.click(0)).message
                await message.client.send_message(me, f"Словлен подарок:\n\n{click}")