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

class AlmostAsyncSerial:
    def __init__(self, filename: str):
        self.filename = filename
        self._data_arrived_callbacks = []
        self._closed_callbacks = []
        self._is_running = False

    def run_async(self):
        asyncio.run(self.run())

    async def stop(self):
        self._is_running = False
        await self._read_task

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
        self._read_task = asyncio.create_task(self.read_file())
        try:
            await self._read_task
        except asyncio.CancelledError:
            logger.warning("Tasks were cancelled.")
        await self.stop()
        for callback in self._closed_callbacks:
            await callback()

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

# Create empty file or empty existing file
with open(THE_FILE, 'w') as file:
    pass

fake_serial = AlmostAsyncSerial(THE_FILE)
@fake_serial.on_data_arrived()
async def on_data_arrived(data):
    print(f"> Data arrived in callback: {data}")

@fake_serial.on_closed()
async def on_closed():
    print("> File writer closed.")
    await fake_serial.append_line("Last words from callback.")


async def fake_writer1():
    await fake_serial.append_line("dupa")
    await asyncio.sleep(3)
    await fake_serial.append_line("nosacz")
    logger.debug("Write fake data complete.")

async def fake_writer2():
    logger.warning("Writing fake data to file")
    for i in range(1, COUNT_TO+1):
        await fake_serial.append_line(f"This is line {i}.")
        await asyncio.sleep(WRITE_INTERVAL)
    logger.debug("Write fake data complete.")

async def async_main():
    task_writer1 = asyncio.create_task(fake_writer1())
    task_writer2 = asyncio.create_task(fake_writer2())
    task_serial = asyncio.create_task(fake_serial.run())

    await task_writer1
    await task_writer2
    await task_serial

asyncio.run(async_main())
