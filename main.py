import re
from shlex import join

from pyrogram import Client

import conf
from utils.filter import text_url, text_url_token, text_export, text_caption
from utils.asyncio_helper import send_message

app = Client("anan", api_id=conf.api_id, api_hash=conf.api_hash)


@app.on_message(text_url_token)
async def token(client, message):
    pass


# text1 = await text_caption(message)
# print("token ", text1)
# await send(text1)


@app.on_message(text_url)
async def url(client, message):
    text1 = await text_caption(message)
    url1 = re.findall(r'(https://[\w\-.]+(?:isv|jd).*?\.com/[a-zA-Z0-9&?=_/-].*)', text1)
    await send_message(token=conf.tokens, chat_id=conf.chat_id,
                       text=("\n" + join(url1) + f"\n{message.chat.id} {message.chat.title} url"))


@app.on_message(text_export)
async def export(client, message):
    text1 = f"\n{message.chat.id} {message.chat.title} export\n"
    text1 += await text_caption(message)
    await send_message(token=conf.tokens, chat_id=conf.chat_id, text=text1)


# @app.on_message()
# async def text(client, message):
#     print("text ", await text_caption(message))
#     print(message.text)
# await send(message.text)

if __name__ == '__main__':
    app.run()
