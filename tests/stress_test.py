import os
import asyncio
import aiohttp
import time


URL_JINA = "https://jinadev.keos.co/index.php/search/"
# URL_JINA = "http://34.125.201.168:8000/search/"
# URL_JINA = "http://34.125.201.168/index.php/search/"


async def request_api(session, n):
    url = URL_JINA
    headers = {"Content-Type": "application/json"}
    body = {
        "data": ["What is Neural Search?"],
        "parameters": {"business": "DEVAR", "origin": "chatbot"},
    }
    async with session.post(url, json=body, headers=headers) as response:
        try:
            print(response, n)
            if response.status != 200:
                raise Exception
        except Exception:
            print("Error fetching %s" % URL_JINA)
        else:
            html = await response.json()
            return dict(body=n)


async def request_aio(num_iterations):
    async with aiohttp.ClientSession() as session:
        tasks = [request_api(session, n) for n in range(num_iterations)]
        return await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    num_iterations = 5
    start_time = time.time()
    response = asyncio.run(request_aio(num_iterations))
    print("response", response)
    duration = time.time() - start_time
    print(f"Request {num_iterations} in {duration} seconds")
