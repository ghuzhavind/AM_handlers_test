import asyncio
import time
import json
import aiohttp


async def make_request(session, url, payload):
    """Make a request to url and print result

    Keyword arguments:
    session -- The session, created in run_test
    url -- The url string to make the request
    payload -- The payload dictionary (by default is empty)

    """
    headers = {'Content-Type': 'application/json'}
    async with session.post(url, data=json.dumps(payload), headers=headers) as response:
        response_data = await response.text()
        num = payload["number"]
        print(f"[{num}] - {response_data}")


async def send_requests(session, url, payload, rate_limit, max_requests):
    """Create tasks to send requests and wait for gather complete

    Keyword arguments:
    session -- The session, created in run_test (aiohttp.ClientSession)
    url -- The url string to make the request (string)
    payload -- The payload dictionary (by default is empty)
    rate_limit -- The rate limit requests per second (integer)
    max_requests -- The maximum number of requests (integer)
    """
    print('[~] Start sending requests...')
    requests_sent = 0
    tasks = []
    start_time = time.time()
    while requests_sent < max_requests:
        requests_number = requests_sent + 1
        current_payload = payload.copy()
        current_payload["number"] = requests_number
        current_time = time.time()
        elapsed_time = current_time - start_time

        if elapsed_time < 1.0 / rate_limit:
            await asyncio.sleep((1.0 / rate_limit) - elapsed_time)
        task = asyncio.create_task(make_request(
            session, url, current_payload))
        tasks.append(task)
        requests_sent += 1
    await asyncio.gather(*tasks)  # Ожидаем завершения всех задач


async def make_request_keeper(session, url):
    """Send request to '/keepalive' web-handler to keep alive connection (not used)

    Keyword arguments:
    session -- The session, created in run_test (aiohttp.ClientSession)
    url -- The url string to make the request (string)
    """
    headers = {'Content-Type': 'application/json'}
    async with session.post(url, headers=headers) as response:
        response_data = await response.text()
        print(response_data)


async def run_keeper(session):
    """Create task to make request to '/keepalive' web-handler to keep alive connection (not used)

    Keyword arguments:
    session -- The session, created in run_test (aiohttp.ClientSession)
    """
    print('[~] Running keeper...')
    url = 'http://AMXX.domain.com/app/appId/keepalive'
    task = asyncio.create_task(make_request_keeper(session, url))

    print("[~] Waiting...")
    await asyncio.gather(task)


async def run_test(url, payload, max_requests, rate_limit, limit_per_host):
    """Run tests endpoint. Create session, send requests and note the time

    Keyword arguments:
    url -- The url string to make the request (string)
    payload -- The payload dictionary (by default is empty)
    max_requests -- The maximum number of requests (integer)
    rate_limit -- The rate limit requests per second (integer)
    limit_per_host --- Number of requests per host (integer)
    """

    start_time = time.time()
    connector = aiohttp.TCPConnector(limit_per_host=limit_per_host)

    async with aiohttp.ClientSession(connector=connector) as session:
        # await run_keeper(session)
        await send_requests(session, url, payload, rate_limit, max_requests)

        end_time = time.time()

        elapsed_time = end_time - start_time    # Total time taken
        print(f"Done! Total time: %.2f" % elapsed_time)

        # avg_time_per_request = elapsed_time / \
        #     max_requests      # Average time per request
        # print(f"Average time per request: %.2f" % avg_time_per_request)


async def main():
    url = 'http://AMXX.domain.com/app/appId/test'
    payload = {}

    max_requests = 100      # Максимальное количество запросов
    rate_limit = 4          # Количество запросов в секунду
    limit_per_host = 2      # Количество запросов за раз

    await run_test(url, payload, max_requests, rate_limit, limit_per_host)

if __name__ == '__main__':
    asyncio.run(main())
