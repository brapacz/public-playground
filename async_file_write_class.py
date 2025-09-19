import asyncio
import logging
import aiofiles
import os
import time

THE_FILE = '/tmp/the_file.txt'
COUNT_TO = 20
WRITE_INTERVAL = 0.5  # seconds

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AsyncFileWriter:
    def __init__(self, filename: str):
        self.filename = filename
        self._data_arrived_callbacks = []
        self._closed_callbacks = []
        self._is_running = False

    def run_async(self):
        asyncio.run(self.run())

    async def stop(self):
        self._is_running = False
        for task in [self._write_task, self._read_task]:
            if not task.done():
                await task

    def on_data_arrived(self):
        def decorator(func):
            self._data_arrived_callbacks.append(func)
            return func
        return decorator

    def on_closed(self):
        def decorator(func):
            self._closed_callbacks.append(func)
            return func
        return decorator

    async def run(self):
        self._is_running = True

        self._write_task = asyncio.create_task(self.count_down_to_file())
        self._read_task = asyncio.create_task(self.read_file())
        try:
            await self._write_task
            self._is_running = False
            await self._read_task
        except asyncio.CancelledError:
            logger.warning("Tasks were cancelled.")
        await self.stop()
        for callback in self._closed_callbacks:
            await callback()


    async def count_down_to_file(self):
        logger.warning("Writing fake data to file")
        for i in range(1, COUNT_TO+1):
            if not self._is_running:
                break
            await self.append_line(f"This is line {i}.")
            logger.debug(f"Wrote line {i} to file.")
            await asyncio.sleep(WRITE_INTERVAL)
        logger.debug("Write fake data complete.")

    async def append_line(self, line: str):
        async with aiofiles.open(self.filename, 'a') as f:
            await f.write(f"{line}\n")

    async def read_file(self):
        f = await aiofiles.open(self.filename, 'r')
        await f.seek(0)
        while True:
            async for line in f:
                logger.debug(f"File contents read: {line.strip()}")
                for callback in self._data_arrived_callbacks:
                    await callback(line.strip())
            if not self._is_running:
                break
            await asyncio.sleep(0)
        await f.close()
        logger.info("Read complete.")


if os.path.exists(THE_FILE):
    os.remove(THE_FILE)

# Create empty file
with open(THE_FILE, 'w') as file:
    pass

writer = AsyncFileWriter(THE_FILE)
@writer.on_data_arrived()
async def on_data_arrived(data):
    print(f"> Data arrived in callback: {data}")

@writer.on_closed()
async def on_closed():
    print("> File writer closed.")
    await writer.append_line("Last words from callback.")

async def aaa():
    # writer.run()
    writer_task = asyncio.create_task(writer.run())

    await writer.append_line("dupa")
    await asyncio.sleep(3)
    await writer.append_line("nosacz")

    await writer.stop()
    await writer_task

asyncio.run(aaa())
