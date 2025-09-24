import asyncio
import time


async def pretend_to_run():
    start = time.time()
    out = 0
    for i in range(100):
        out += i
        await asyncio.sleep(0)
    total_time = time.time() - start
    print(f"Time taken: {total_time:.6f} seconds")

async def pretend_to_run_infinitely():
    while True:
        await asyncio.sleep(0.01)

async def main():
    async with asyncio.timeout(1):
        await pretend_to_run()

    try:
        async with asyncio.timeout(1):
            await pretend_to_run_infinitely()
        print("This should not be printed!")
    except TimeoutError:
        print("Timed out, as expected!")


if __name__ == "__main__":
    asyncio.run(main())
