# Standard library imports
import argparse
import asyncio
import logging
import random
import ssl
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

# Third-party imports
import aiofiles
import aiohttp
from aiohttp_socks import ProxyConnector, ProxyType
from colorama import Fore, Style, init
from tqdm import tqdm

init(autoreset=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def load_proxies(file_path):
    try:
        async with aiofiles.open(file_path, mode='r') as file:
            return [line.strip() for line in await file.readlines() if line.strip()]
    except FileNotFoundError:
        logger.error(f"{Fore.RED}Proxy file {
                     file_path} not found.{Style.RESET_ALL}")
        return []
    except Exception as e:
        logger.error(f"{Fore.RED}Error reading proxy file: {
                     str(e)}{Style.RESET_ALL}")
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
        async with aiohttp.ClientSession(connector=connector, headers=headers) as proxy_session:
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


async def load_test(url, num_requests, concurrency, proxies, headers, method, data):
    connector = aiohttp.TCPConnector(
        ssl=ssl.create_default_context(), limit=concurrency)

    async with aiohttp.ClientSession(connector=connector, trust_env=True) as session:
        semaphore = asyncio.Semaphore(concurrency)
        progress_bar = tqdm(total=num_requests, desc="Requests", unit="req",
                            bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET))

        async def bounded_send_request(url):
            async with semaphore:
                proxy = random.choice(proxies) if proxies else None
                result = await send_request(session, url, proxy, headers=headers, method=method, data=data)
                progress_bar.update(1)
                return result

        tasks = [bounded_send_request(url) for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)

    progress_bar.close()

    successful_requests = [r for r in results if isinstance(r[0], int)]
    failed_requests = [r for r in results if isinstance(r[0], str)]

    response_times = [r[1] for r in successful_requests if r[1] is not None]
    avg_response_time = statistics.mean(
        response_times) if response_times else 0
    median_response_time = statistics.median(
        response_times) if response_times else 0
    min_response_time = min(response_times) if response_times else 0
    max_response_time = max(response_times) if response_times else 0

    print(f"\n{Fore.CYAN}=== Load Test Results ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Target URL:{Style.RESET_ALL} {url}")
    print(f"{Fore.YELLOW}Total Requests:{Style.RESET_ALL} {num_requests}")
    print(f"{Fore.YELLOW}Concurrency:{Style.RESET_ALL} {concurrency}")
    print(f"{Fore.YELLOW}HTTP Method:{Style.RESET_ALL} {method}")
    print(f"\n{Fore.GREEN}Successful Requests:{Style.RESET_ALL} {
          len(successful_requests)} ({len(successful_requests)/num_requests*100:.2f}%)")
    print(f"{Fore.RED}Failed Requests:{Style.RESET_ALL} {
          len(failed_requests)} ({len(failed_requests)/num_requests*100:.2f}%)")
    print(f"\n{Fore.CYAN}Response Time Statistics:{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}Average:{Style.RESET_ALL} {
          avg_response_time:.3f} seconds")
    print(f"  {Fore.YELLOW}Median:{Style.RESET_ALL} {
          median_response_time:.3f} seconds")
    print(f"  {Fore.YELLOW}Min:{Style.RESET_ALL} {
          min_response_time:.3f} seconds")
    print(f"  {Fore.YELLOW}Max:{Style.RESET_ALL} {
          max_response_time:.3f} seconds")

    if failed_requests:
        print(f"\n{Fore.RED}Error Summary:{Style.RESET_ALL}")
        error_counts = {}
        for error, _ in failed_requests:
            error_counts[error] = error_counts.get(error, 0) + 1
        for error, count in error_counts.items():
            print(f"  {error}: {count} occurrences")

    return successful_requests, failed_requests, avg_response_time


async def run_load_test(url, num_requests, concurrency, proxy_file, headers, method, data):
    proxies = await load_proxies(proxy_file) if proxy_file else []
    if not proxies and proxy_file:
        print(f"{Fore.YELLOW}Warning: No proxies loaded. Proceeding without proxy.{
              Style.RESET_ALL}")
    elif proxies:
        print(f"{Fore.GREEN}Loaded {len(proxies)} proxies.{Style.RESET_ALL}")

    return await load_test(url, num_requests, concurrency, proxies, headers, method, data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=f"{Fore.CYAN}Powerful Load Testing Tool{Style.RESET_ALL}")
    parser.add_argument("url", help="Target URL for load testing")
    parser.add_argument("-n", "--num_requests", type=int,
                        default=1000, help="Number of requests to send")
    parser.add_argument("-c", "--concurrency", type=int,
                        default=100, help="Number of concurrent requests")
    parser.add_argument("-p", "--proxy_file",
                        help="File containing list of proxies")
    parser.add_argument("-H", "--headers", action='append',
                        help="Custom headers in the format 'Key:Value'")
    parser.add_argument("-X", "--method", default="GET",
                        help="HTTP method to use (GET, POST, etc.)")
    parser.add_argument(
        "-d", "--data", help="Data to send with the request (for POST, PUT, etc.)")

    args = parser.parse_args()

    headers = {}
    if args.headers:
        for header in args.headers:
            key_value = header.split(':', 1)
            if len(key_value) == 2:
                key, value = key_value
                headers[key.strip()] = value.strip()
            else:
                logger.warning(f"Invalid header format: {
                               header}. Expected 'Key:Value'.")

    print(f"{Fore.CYAN}Starting load test...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Target URL:{Style.RESET_ALL} {args.url}")
    print(f"{Fore.YELLOW}Number of requests:{
          Style.RESET_ALL} {args.num_requests}")
    print(f"{Fore.YELLOW}Concurrency:{Style.RESET_ALL} {args.concurrency}")
    print(f"{Fore.YELLOW}HTTP Method:{Style.RESET_ALL} {args.method}")
    if args.proxy_file:
        print(f"{Fore.YELLOW}Proxy file:{Style.RESET_ALL} {args.proxy_file}")
    if headers:
        print(f"{Fore.YELLOW}Custom headers:{Style.RESET_ALL}")
        for key, value in headers.items():
            print(f"  {key}: {value}")
    if args.data:
        print(f"{Fore.YELLOW}Request data:{Style.RESET_ALL} {args.data}")

    with ThreadPoolExecutor() as executor:
        future = executor.submit(
            asyncio.run,
            run_load_test(args.url, args.num_requests, args.concurrency,
                          args.proxy_file, headers, args.method, args.data)
        )
        successful_requests, failed_requests, avg_response_time = future.result()

    print(f"\n{Fore.GREEN}Load test completed.{Style.RESET_ALL}")
