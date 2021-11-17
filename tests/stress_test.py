import os
import asyncio
import aiohttp
import time


URL_JINA = "https://jinadev.keos.co/index.php/search/"


async def request_api(session, n):
    url = URL_JINA
    headers = {"Content-Type": "application/json"}
    body = {
        "data": ["What is Neural Search?"],
        "parameters": {"business": "DEVAR", "origin": "chatbot"},
    }
    async with session.post(url, json=body, headers=headers) as response:
        try:
            # print(n)
            if response.status != 200:
                raise Exception
        except Exception:
            print("Error fetching %s" % URL_JINA)
        else:
            html = await response.json()
            return dict(body=n)


async def on_request_start(session, trace_config_ctx, params):
    trace_config_ctx.start = asyncio.get_event_loop().time()


async def on_request_end(session, trace_config_ctx, params):
    elapsed = asyncio.get_event_loop().time() - trace_config_ctx.start
    print("Request took {} seconds".format(elapsed))


async def request_aio(num_iterations, trace_config):
    async with aiohttp.ClientSession(trace_configs=[trace_config]) as session:
        tasks = [request_api(session, n) for n in range(num_iterations)]
        return await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    num_iterations = 100
    start_time = time.time()

    trace_config = aiohttp.TraceConfig()
    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_end.append(on_request_end)

    response = asyncio.run(request_aio(num_iterations, trace_config))
    print()
    print("Response: ", response)
    duration = time.time() - start_time
    print(f"Request: {num_iterations} in {duration} seconds")
