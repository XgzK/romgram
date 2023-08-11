import logging
import ssl
import aiohttp
import certifi

try:
    import ujson as json
except ImportError:
    import json
import os

API_URL = 'https://api.telegram.org/bot{0}/{1}'

logger = logging.getLogger('TeleBot')

proxy = None

FILE_URL = None

REQUEST_TIMEOUT = 300
MAX_RETRIES = 3

REQUEST_LIMIT = 50


class SessionManager:
    def __init__(self) -> None:
        self.session = None
        self.ssl = ssl.create_default_context(cafile=certifi.where())

    async def create_session(self):
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(
            limit=REQUEST_LIMIT,
            ssl=self.ssl
        ))
        return self.session

    async def get_session(self):
        if self.session is None:
            self.session = await self.create_session()
            return self.session

        if self.session.closed:
            self.session = await self.create_session()

        # noinspection PyProtectedMember
        if not self.session._loop.is_running():
            await self.session.close()
            self.session = await self.create_session()
        return self.session

    async def closes(self):
        await self.session.close()


session_manager = SessionManager()


async def _check_result(method_name, result: aiohttp.ClientResponse):
    """
    Checks whether `result` is a valid API response.
    A result is considered invalid if:
        - The server returned an HTTP response code other than 200
        - The content of the result is invalid JSON.
        - The method call was unsuccessful (The JSON 'ok' field equals False)

    :raises ApiException: if one of the above listed cases is applicable
    :param method_name: The name of the method called
    :param result: The returned result of the method request
    :return: The result parsed to a JSON dictionary.
    """
    result_json = await result.json(encoding="utf-8")
    return result_json


async def _process_request(token, url, method='get', params=None, files=None, **kwargs):
    # Let's resolve all timeout parameters.
    # getUpdates parameter may contain 2 parameters: request_timeout & timeout.
    # other methods may contain timeout parameter that should be applied to
    # ClientTimeout only.
    # timeout should be added to params for getUpdates. All other timeout's should be used
    # for request timeout.
    # here we got request_timeout, so this is getUpdates method.
    if 'request_timeout' in kwargs:
        request_timeout = kwargs.pop('request_timeout')

    else:
        # let's check for timeout in params
        request_timeout = params.pop('timeout', None) if params else None
        # we will apply default request_timeout if there is no timeout in params
        # otherwise, we will use timeout parameter applied for payload.

    request_timeout = REQUEST_TIMEOUT if request_timeout is None else request_timeout

    # Preparing data by adding all parameters and files to FormData
    params = _prepare_data(params, files)

    timeout = aiohttp.ClientTimeout(total=request_timeout)
    got_result = False
    current_try = 0
    session = await session_manager.get_session()
    while not got_result and current_try < MAX_RETRIES - 1:
        current_try += 1
        try:
            async with session.request(method=method, url=API_URL.format(token, url), data=params, timeout=timeout,
                                       proxy=proxy) as resp:
                got_result = True
                logger.debug(
                    "Request: method={0} url={1} params={2} files={3} request_timeout={4} current_try={5}".format(
                        method, url, params, files, request_timeout, current_try).replace(token, token.split(':')[
                        0] + ":{TOKEN}"))

                json_result = await _check_result(url, resp)
                if json_result:
                    return json_result['result']
        except Exception as e:
            logger.error('Aiohttp ClientError: {0}'.format(e.__class__.__name__))


def _prepare_file(obj):
    """
    Prepares file for upload.
    """
    name = getattr(obj, 'name', None)
    if name and isinstance(name, str) and name[0] != '<' and name[-1] != '>':
        return os.path.basename(name)


def _prepare_data(params=None, files=None):
    """
    Adds the parameters and files to the request.

    :param params:
    :param files:
    :return:
    """
    data = aiohttp.formdata.FormData(quote_fields=False)

    if params:
        for key, value in params.items():
            data.add_field(key, str(value))
    if files:
        for key, f in files.items():
            if isinstance(f, tuple):
                if len(f) == 2:
                    file_name, file = f
                else:
                    raise ValueError('Tuple must have exactly 2 elements: filename, fileobj')
            else:
                file_name, file = _prepare_file(f) or key, f

            data.add_field(key, file, filename=file_name)

    return data


# async def get_me(token):
#     method_url = r'getMe'
#     return await _process_request(token, method_url)


async def send_message(token, chat_id, text):
    method_name = 'sendMessage'
    params = {'chat_id': str(chat_id), 'text': text}
    return await _process_request(token, method_name, params=params)
