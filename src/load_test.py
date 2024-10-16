# Standard library imports
import asyncio
import random
import statistics

# Third-party imports
from colorama import Fore, Style
from tqdm import tqdm

# Local imports
from proxy import load_proxies, send_request


async def load_test(url, num_requests, concurrency, proxies, headers, method, data):
    semaphore = asyncio.Semaphore(concurrency)
    progress_bar = tqdm(total=num_requests, desc="Requests", unit="req")

    async def bounded_send_request(url):
        async with semaphore:
            proxy = random.choice(proxies) if proxies else None
            result = await send_request(url, proxy, headers=headers, method=method, data=data)
            progress_bar.update(1)
            return result

    tasks = [bounded_send_request(url) for _ in range(num_requests)]
    results = await asyncio.gather(*tasks)

    progress_bar.close()

    successful_requests = [r for r in results if isinstance(r[0], int)]
    failed_requests = [r for r in results if isinstance(r[0], str)]

    response_times = [r[1] for r in successful_requests if r[1] is not None]
    avg_response_time = statistics.mean(response_times) if response_times else 0
    median_response_time = statistics.median(response_times) if response_times else 0
    min_response_time = min(response_times) if response_times else 0
    max_response_time = max(response_times) if response_times else 0

    print(f"\n{Fore.CYAN}=== Load Test Results ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Target URL:{Style.RESET_ALL} {url}")
    print(f"{Fore.YELLOW}Total Requests:{Style.RESET_ALL} {num_requests}")
    print(f"{Fore.YELLOW}Concurrency:{Style.RESET_ALL} {concurrency}")
    print(f"{Fore.YELLOW}HTTP Method:{Style.RESET_ALL} {method}")
    print(f"\n{Fore.GREEN}Successful Requests:{Style.RESET_ALL} {
          len(successful_requests)} ({len(successful_requests) / num_requests * 100:.2f}%)")
    print(f"{Fore.RED}Failed Requests:{Style.RESET_ALL} {
          len(failed_requests)} ({len(failed_requests) / num_requests * 100:.2f}%)")
    print(f"\n{Fore.CYAN}Response Time Statistics:{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}Average:{Style.RESET_ALL} {avg_response_time:.3f} seconds")
    print(f"  {Fore.YELLOW}Median:{Style.RESET_ALL} {median_response_time:.3f} seconds")
    print(f"  {Fore.YELLOW}Min:{Style.RESET_ALL} {min_response_time:.3f} seconds")
    print(f"  {Fore.YELLOW}Max:{Style.RESET_ALL} {max_response_time:.3f} seconds")

    if failed_requests:
        print(f"\n{Fore.RED}Error Summary:{Style.RESET_ALL}")
        error_counts = {}
        for error, _ in failed_requests:
            error_counts[error] = error_counts.get(error, 0) + 1
        for error, count in error_counts.items():
            print(f"  {error}: {count} occurrences")

    return successful_requests, failed_requests, avg_response_time


async def run_load_test(url, num_requests, concurrency, proxy_file, headers, method, data):
    proxies = await load_proxies(proxy_file) if proxy_file else None
    if not proxies and proxy_file:
        print(f"{Fore.YELLOW}Warning: No proxies loaded. Proceeding without proxy.{Style.RESET_ALL}")
    elif proxies:
        print(f"{Fore.GREEN}Loaded {len(proxies)} proxies.{Style.RESET_ALL}")

    return await load_test(url, num_requests, concurrency, proxies, headers, method, data)
