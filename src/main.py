# Standard library imports
import argparse
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Third-party imports
from colorama import Fore, Style

# Local imports
from load_test import run_load_test

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=f"{Fore.CYAN}Powerful Load Testing Tool{Style.RESET_ALL}"
    )
    parser.add_argument("url", help="Target URL for load testing")
    parser.add_argument("-n", "--num_requests", type=int, default=1000, help="Number of requests to send")
    parser.add_argument("-c", "--concurrency", type=int, default=100, help="Number of concurrent requests")
    parser.add_argument("-p", "--proxy_file", help="File containing list of proxies")
    parser.add_argument("-H", "--headers", action='append', help="Custom headers in the format 'Key:Value'")
    parser.add_argument("-X", "--method", default="GET", help="HTTP method to use (GET, POST, etc.)")
    parser.add_argument("-d", "--data", help="Data to send with the request (for POST, PUT, etc.)")

    args = parser.parse_args()

    headers = {}
    if args.headers:
        for header in args.headers:
            key_value = header.split(':', 1)
            if len(key_value) == 2:
                key, value = key_value
                headers[key.strip()] = value.strip()
            else:
                print(f"{Fore.RED}Invalid header format: {header}. Expected 'Key:Value'.{Style.RESET_ALL}")

    print(f"{Fore.CYAN}Starting load test...{Style.RESET_ALL}")
    with ThreadPoolExecutor() as executor:
        future = executor.submit(
            asyncio.run,
            run_load_test(args.url, args.num_requests, args.concurrency,
                          args.proxy_file, headers, args.method, args.data)
        )
        successful_requests, failed_requests, avg_response_time = future.result()

    print(f"\n{Fore.GREEN}Load test completed.{Style.RESET_ALL}")
