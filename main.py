import re
from shlex import join

from pyrogram import Client

import conf
from utils.filter import text_url, text_url_token, text_export, text_caption
from utils.asyncio_helper import send_messages

app = Client("anan", api_id=conf.api_id, api_hash=conf.api_hash)


@app.on_message(text_url_token)
async def token(client, message):
    pass


# text1 = await text_caption(message)
# print("token ", text1)
# await send(text1)


@app.on_message(text_url)
async def url(client, message):
    url1 = re.findall(r'(https://(?:[\w\-.]+isv.*?\.com|pro\.m\.jd\.com)+/[a-zA-Z0-9&?\.=_/-]*)', await text_caption(message))
    await send_messages(token=conf.tokens, chat_ids=conf.chat_ids,
                        text= "\n".join(set(url1)))


@app.on_message(text_export)
async def export(client, message):
    await send_messages(token=conf.tokens, chat_ids=conf.chat_ids, text=await text_caption(message))


# @app.on_message()
# async def text(client, message):
#     print("text ", await text_caption(message))
#     print(message.text)
# await send(message.text)

if __name__ == '__main__':
    app.run()
