import telethon, requests, io, base64
from .. import loader, utils
from telethon.tl.patched import Message
from telethon.tl import types


@loader.tds
class ShitQuotesMod(loader.Module):
    strings = {
        "name": "SQuotes"
    }

    async def client_ready(self, client, db):
        self.client: telethon.TelegramClient = client
        self.api_endpoint = "https://quotes.fl1yd.ml/generate"


    async def sqcmd(self, message: Message):
        """Использование: .sq <реплай>"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not (args or reply):
            return await message.edit("Нет аргументов или реплая")

        text, media, id, name, avatar, rank, reply_id, reply_name, reply_text, entities = await self.parse_messages(message, args, reply)
        payload = {
            "text": text,
            "media": media,
            "entities": entities,
            "author": {
                "id": id,
                "name": name,
                "avatar": avatar,
                "rank": rank
            },
            "reply": {
                "id": reply_id,
                "name": reply_name,
                "text": reply_text
            }
        }

        await message.edit("<b>[SQuotes]</b> Ожидание API...")
        r = await self._api_request(payload)
        if r.status_code != 200:
            return await message.edit("<b>[SQuotes]</b> Ошибка API")

        quote = io.BytesIO(r.content)
        quote.name = "SQuote.webp"

        await message.edit("<b>[SQuotes]</b> Отправка...")
        await message.respond(file=quote, reply_to=reply or message)
        await message.delete()


    async def parse_messages(self, message: Message, args, reply: Message):
        args_ = args.split()
        text = args

        await message.edit("<b>[SQuotes]</b> Обработка...")
        user = avatar = reply_id = reply_name = reply_text = entities = None
        user = message.sender
        if reply and reply.fwd_from:
            user_id = reply.fwd_from.from_id
            text = args or reply.raw_text
            if user_id:
                try:
                    user_id = user_id.channel_id
                except:
                    user_id = user_id.user_id
                name = telethon.utils.get_display_name((await self.client.get_entity(user_id)))
                name = name[:26] + '...' if len(name) > 25 else name

            if not user_id:
                user_id = message.chat_id
                name = reply.fwd_from.from_name

        else:
            if reply:
                if not args:
                    if r := await reply.get_reply_message():
                        reply_id = r.sender.id
                        reply_name = telethon.utils.get_display_name(r.sender)
                        reply_name = reply_name[:26] + '...' if len(reply_name) > 25 else reply_name
                        reply_text = (
                            "📷 Фото"
                            if r.photo
                            else "📊 Опрос"
                            if r.poll
                            else "📍 Местоположение"
                            if r.geo
                            else "👤 Контакт"
                            if r.contact
                            else "🖼 GIF"
                            if r.gif
                            else "🎧 Музыка"
                            if r.audio
                            else "📹 Видео"
                            if r.video
                            else "📹 Видеосообщение"
                            if r.video_note
                            else "🎵 Голосовое сообщение"
                            if r.voice
                            else r.file.emoji + " Стикер"
                            if r.sticker
                            else "💾 Файл"
                            if r.file
                            else r.raw_text or "Unsupported message media"
                        )
                        reply_text = reply_text[:26] + '...' if len(reply_text) > 25 else reply_text
                    entities = await self.convert_entities(reply.entities)
                user = reply.sender
                text = args or reply.raw_text
            else:
                try:
                    user = await self.client.get_entity(int(args_[0]) if args_[0].isdigit() else args_[0])
                    if len(args_) < 2:
                        user = await self.client.get_entity(int(args) if args.isdigit() else args)
                    else:
                        text = args.split(maxsplit=1)[1]
                except (ValueError, IndexError):
                    user = message.sender

            user_id = user.id

            name = telethon.utils.get_display_name(user)
            name = name[:26] + '...' if len(name) > 25 else name

            avatar = await self.client.download_profile_photo(user_id, bytes)
            avatar = base64.b64encode(avatar).decode() if avatar else None

        thumb = await self.download_thumb(reply)
        media = await self.client.download_media(thumb, bytes, thumb=-1)
        media = base64.b64encode(media).decode() if media else None

        rank = ""
        if not message.is_private:
            admins = await self.client.get_participants(message.chat_id, filter=types.ChannelParticipantsAdmins)
            if user in admins:
                admin = admins[admins.index((await self.client.get_entity(user_id)))].participant
                rank = admin.rank or "creator" if type(admin) == types.ChannelParticipantCreator else "admin"

        return text, media, user_id, name, avatar, rank, reply_id, reply_name, reply_text, entities


    async def download_thumb(self, reply: Message):
        data = None
        if reply and reply.media:
            data = reply.photo or reply.sticker or reply.video or reply.video_note or reply.gif or reply.web_preview
        return data


    async def convert_entities(self, entities):
        res = []
        if entities:
            for entity in entities:
                d_entity = entity.to_dict()
                d_entity['type'] = d_entity.pop("_").lstrip('MessageEntity').lower()
                res.append(d_entity)
        return res


    async def _api_request(self, data: dict):
        return requests.post(self.api_endpoint, json=data)