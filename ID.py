from .. import loader, utils

@loader.tds
class IDMod(loader.Module):
    """ауе"""
    strings = {"name": "ID"}

    async def idcmd(self, message):
        reply = await message.get_reply_message()
        user = await message.client.get_entity(reply.sender_id)
        await message.edit(f"<b>Китаец лучший</b>\n\n"
                           f"имя: <b>{user.first_name}</b>\n"
                           f"айди: <b>{user.id}</b>\n"
                           f"юзер: @{user.username}")