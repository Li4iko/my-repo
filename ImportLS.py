from .. import loader, utils


@loader.tds
class importLSMod(loader.Module):
    """Импортировать личные сообщения в файл"""
    strings = {
        "name": "ImportLS"
    }
    async def importcmd(self, message):
        if not message.is_private:
            return await message.edit("Это не личные сообщения!")

        await message.edit("Обработка...")

        msgs = await message.client.get_messages(message.chat_id, reverse=True)
        text = ""
        async for msg in message.client.iter_messages(message.chat_id, reverse=True):
            text += (
                f">>> Кто: {msg.sender.first_name} | {msg.sender.id}\n"
                f">>> Сообщение [{msg.date.day}.{msg.date.month}.{msg.date.year} в {msg.date.hour}:{msg.date.minute}] — {msg.message}\n\n"
            )
        file = open(f"ls_{message.chat_id}.txt", "w")
        file.write(text)

        await message.respond(file=f"ls_{message.chat_id}.txt")
        return await message.delete()