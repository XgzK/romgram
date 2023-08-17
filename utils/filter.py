import re

from pyrogram.filters import create
from pyrogram.types import Message

import conf


async def text_caption(message: Message) -> str:
    """
    获取文本
    :param message:
    :type message:
    :return:
    :rtype:
    """
    if message.text:
        return message.text
    elif message.caption:
        return message.caption
    return ""


async def text_cha_id(message: Message) -> bool:
    """
    屏蔽ID
    :param message:
    :type message:
    :return:
    :rtype:
    """
    if message.forward_from_chat:
        return bool(message.forward_from_chat.id in conf.shield)
    return bool(message.chat.id in conf.shield)


async def text_filter_url(_, __, message: Message):
    if await text_cha_id(message):
        return False
    if re.findall(r'(https://(?:[\w\-.]+isv.*?\.com|pro\.m\.jd\.com)+/[a-zA-Z0-9&?\.=_/-]*)', await text_caption(message)):
        return True
    return False


async def text_filter_url_token(_, __, message: Message):
    if await text_cha_id(message):
        return False
    if "https://u.jd.com/" in await text_caption(message):
        return True
    return False


async def text_filter_export(_, __, message: Message):
    if await text_cha_id(message):
        return False
    if "export" in await text_caption(message):
        return True
    return False


text_url = create(text_filter_url)
""" 获取消息的链接."""

text_url_token = create(text_filter_url_token)
""" 获取消息的链接的短链接"""

text_export = create(text_filter_export)
""" 获取消息中包含export的"""
