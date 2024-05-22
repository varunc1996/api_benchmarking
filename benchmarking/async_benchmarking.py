import argparse
import asyncio
import aiohttp
import random
import time
import statistics


async def worker(session, url, status_codes, total_latency, total_output_tokens, lock, semaphore):
    """
    Make an HTTP GET request to the specified URL and update shared statistics.

    Args:
        session (aiohttp.ClientSession): A session object for making HTTP requests.
        url (str): The URL to make the request to.
        status_codes (dict): A dictionary to store status codes and their counts.
        total_latency (list): A list to store total_latency of each request.
        total_output_tokens(list): A list that stores the total number of output tokens in the first element
        lock (asyncio.Lock): A lock to synchronize access to shared resources.
        semaphore (asyncio.Semaphore): A semaphore to limit concurrency.
    """

    async with semaphore:
        start_time = time.time()
        try:
            # print(f'Request: {url}')
            async with session.get(url) as response:
                status_code = response.status
                response_data = await response.json()
                output_tokens = response_data.get('output_tokens', 0)
        except aiohttp.ClientError:
            status_code = 500  # Internal Server Error
            output_tokens = 0
        end_time = time.time()
        
        async with lock:
            status_codes[status_code] = status_codes.get(status_code, 0) + 1
            total_latency.append(end_time - start_time)
            total_output_tokens[0] += output_tokens


async def single_benchmark(targets, num_requests, lock, semaphore):
    """
    Send parallel HTTP GET requests to random endpoints.

    Args:
        targets (list): A list of target URLs to randomly select from.
        num_requests (int): Total number of requests to execute.
        lock (asyncio.Lock): A lock to synchronize access to shared resources.
        semaphore (asyncio.Semaphore): A semaphore to limit concurrency.
    """

    status_codes = {}
    total_latency = []
    total_output_tokens = [0]

    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(num_requests):
            url = random.choice(targets)  # Pick one random target from the list
            task = asyncio.create_task(worker(session, url, status_codes, total_latency, total_output_tokens, lock, semaphore))
            tasks.append(task)

        await asyncio.gather(*tasks)

    end_time = time.time()
    display_results(status_codes, total_latency, end_time - start_time, total_output_tokens)


def display_results(status_codes, total_latency, total_time, total_output_tokens):
    """
    Display our benchmarking results

    Args:
        status_codes (dict): A dictionary to store status codes and their counts.
        total_latency (list): A list to store total_latency of each request.
        total_time (float): Total time taken for all requests in seconds
        total_output_tokens(list): A list that stores the total number of output tokens in the first element
    """
    print("*** Results ***")
    print("Status codes:")
    for code in dict(sorted(status_codes.items())):
        print(f"  {code}: {status_codes[code]} times")

    print(f"Success ratio: {((status_codes.get(200, 0) / len(total_latency)) * 100):.2f}%")

    print("--- - --- - ---")
    print(f"Total time: {total_time:.4f} seconds")
    print(f"Median latency: {statistics.median(total_latency):.4f}  |  Average latency: {(sum(total_latency) / len(total_latency)):.4f} seconds")
    print(f"Shortest request time: {min(total_latency):.4f} seconds  |  Longest request time: {max(total_latency):.4f} seconds")

    print("--- - --- - ---")
    print(f"Throughput: {len(total_latency) / total_time} requests per second")
    print(f"Avg Output Tokens: {(total_output_tokens[0] / len(total_latency)):.4f}  |  Output Token Throughput: {(total_output_tokens[0] / total_time):.4f} tokens per second")


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments
    """

    parser = argparse.ArgumentParser(description='Send parallel requests to random endpoints')
    parser.add_argument('--requests', type=int, default=10,
                        help='Total number of requests to execute')
    parser.add_argument('--concurrency', type=int, default=5,
                        help='Maximum number of parallel requests allowed')
    parser.add_argument('--targets', type=str, default='endpoints.txt',
                        help='Path to the file containing endpoints')
    return parser.parse_args()


def load_targets(file_path):
    """
    Load target URLs from a file.

    Args:
        file_path (str): Path to the file containing endpoints.

    Returns:
        list: List of target URLs
    """

    with open(file_path, 'r') as file:
        return file.read().splitlines()


def main():
    """
    Main function to parse arguments, load targets, run the async requests and display results.
    """

    args = parse_arguments()
    targets = load_targets(args.targets)
    lock = asyncio.Lock()
    semaphore = asyncio.Semaphore(args.concurrency)

    asyncio.run(single_benchmark(targets, args.requests, lock, semaphore))


if __name__ == "__main__":
    main()
