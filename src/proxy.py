# Standard library imports
import asyncio
import logging
import ssl
import time
from urllib.parse import urlparse

# Third-party imports
import aiofiles
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector, ProxyType
from colorama import Fore, Style

logger = logging.getLogger(__name__)


async def load_proxies(file_path):
    try:
        async with aiofiles.open(file_path, mode='r') as file:
            return [line.strip() for line in await file.readlines() if line.strip()]
    except FileNotFoundError:
        logger.error(f"{Fore.RED}Proxy file {file_path} not found.{Style.RESET_ALL}")
        return []
    except Exception as e:
        logger.error(f"{Fore.RED}Error reading proxy file: {str(e)}{Style.RESET_ALL}")
        return []


def get_proxy_type(proxy_url):
    scheme = urlparse(proxy_url).scheme.lower()
    if scheme == 'http':
        return ProxyType.HTTP
    elif scheme == 'socks4':
        return ProxyType.SOCKS4
    elif scheme == 'socks5':
        return ProxyType.SOCKS5
    else:
        raise ValueError(f"Unsupported proxy type: {scheme}")


async def create_proxy_connector(proxy_url):
    if not proxy_url:
        return None
    proxy_type = get_proxy_type(proxy_url)
    return ProxyConnector(
        proxy_type=proxy_type,
        host=urlparse(proxy_url).hostname,
        port=urlparse(proxy_url).port,
        ssl=ssl.create_default_context()  # Use secure SSL context
    )


async def send_request(session, url, proxy=None, timeout=10, headers=None, method='GET', data=None):
    try:
        connector = await create_proxy_connector(proxy)
        async with ClientSession(connector=connector, headers=headers) as proxy_session:
            start_time = time.time()
            async with proxy_session.request(method, url, timeout=timeout, data=data) as response:
                await response.text()  # Ensure the full response is received
                elapsed_time = time.time() - start_time
                return response.status, elapsed_time
    except asyncio.TimeoutError:
        return "Timeout", None
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        return f"Error: {str(e)}", None
