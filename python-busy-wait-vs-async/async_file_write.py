import asyncio
from importlib.resources import contents
import aiofiles
import os

THE_FILE = '/tmp/the_file.txt'
COUNT_TO = 20
KEEP_READING = True

async def count_down_to_file():
    for i in range(1, COUNT_TO+1):
        async with aiofiles.open(THE_FILE, 'a') as f:
            await f.write(f"This is line {i}.\n")
        print(f"Wrote line {i} to file.")
        await asyncio.sleep(0)
    print("Write complete.")

async def read_file():
    f = await aiofiles.open(THE_FILE, 'r')
    await f.seek(0)
    while True:
        async for line in f:
            print(f"File contents read: {line.strip()}")
        if not KEEP_READING:
            break
        await asyncio.sleep(0)
    await f.close()
    print("Read complete.")


if os.path.exists(THE_FILE):
    os.remove(THE_FILE)

# Create empty file
with open(THE_FILE, 'w') as file:
    pass

# asyncio.run(count_down_to_file())
# asyncio.run(count_down_to_file())

async def main():
    global KEEP_READING
    write_task = asyncio.create_task(count_down_to_file())
    read_task = asyncio.create_task(read_file())
    await write_task
    KEEP_READING = False
    await read_task

asyncio.run(main())
