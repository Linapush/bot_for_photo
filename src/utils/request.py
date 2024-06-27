from typing import Any, Dict, Optional

import aiohttp
from aiohttp import FormData
from aiohttp.typedefs import LooseHeaders
from multidict import CIMultiDict

from src.logger import correlation_id_ctx, logger
from src.middleware.auth import access_token_cxt

from conf.config import settings


class ClientSessionWithCorrId(aiohttp.ClientSession):
    def _prepare_headers(self, headers: Optional[LooseHeaders]) -> CIMultiDict[str]:
        headers = super()._prepare_headers(headers)

        correlation_id = correlation_id_ctx.get()
        headers['X-Correlation-Id'] = correlation_id

        return headers


async def do_request(
    url: str,
    json: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, Any]] = None,
    data: Optional[FormData] = None,
    method: str = 'POST',
) -> Any:
    try:
        headers_ = {'Authorization': f'Bearer {access_token_cxt.get()}'}
        logger.info(f"Токен доступа в заголовке запроса: {headers_['Authorization']}")
    except LookupError:
        headers_ = {}

    timeout = aiohttp.ClientTimeout(total=3)
    connector = aiohttp.TCPConnector()

    if headers is not None:
        headers_.update(headers)
        logger.info(f"Headers update: {headers_}")

    logger.info(f"URL запроса: {url}")

    final_exc = None
    async with ClientSessionWithCorrId(connector=connector, timeout=timeout) as session:
        for _ in range(settings.RETRY_COUNT):
            try:
                async with session.request(
                    method,
                    url,
                    headers=headers_,
                    data=data,
                    json=json,
                    params=params,
                ) as response:
                    response.raise_for_status()
                    response_json = await response.json()
                    logger.info(f"Response from {url}: {response_json}")
                    return response_json
            except aiohttp.ClientResponseError as exc:
                logger.exception('Http error')
                if exc.status == 404:
                    logger.error(f'Ошибка 404 Not Found: {exc}')

                final_exc = exc

    if final_exc is not None:
        raise final_exc

    raise RuntimeError('Unsupported')
