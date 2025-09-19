import asyncio
import logging
import os
import aiofiles


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

    @property
    def running(self):
        return self._is_running

    async def stop(self):
        self._is_running = False

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
            logger.warning("Read task has been cancelled.")
        await self.stop()
        for callback in self._closed_callbacks:
            await callback()

    async def append_line(self, line: str):
        async with aiofiles.open(self.filename, 'a') as f:
            await f.write(f"{line}\n")

    async def read_file(self):
        f = await aiofiles.open(self.filename, 'r')
        while self._is_running:
            async for line in f:
                logger.debug(f"File contents read: {line.strip()}")
                for callback in self._data_arrived_callbacks:
                    await callback(line.strip())
            if not self._is_running:
                break
            await asyncio.sleep(0)
        await f.close()
        logger.info("Read complete.")


COUNT_TO = 4
WRITE_INTERVAL = 0.5  # seconds
THE_FILE = os.getenv('THE_FILE')
if not THE_FILE:
    logger.fatal("Environment variable THE_FILE is not set. Exiting.")
    exit(1)

# Create empty file or empty existing file
with open(THE_FILE, 'w') as file:
    pass

fake_serial = AlmostAsyncSerial(THE_FILE)
@fake_serial.on_data_arrived()
async def on_data_arrived(data):
    print(f"> Data arrived in callback: {data}")

@fake_serial.on_data_arrived()
async def stop_when_stop(data):
    if data == "stop":
        print("> Stopping serial reader.")
        await fake_serial.stop()

@fake_serial.on_closed()
async def on_closed():
    print("> File writer closed.")
    await fake_serial.append_line("Last words from callback.")


async def fake_writer1():
    await fake_serial.append_line("first")
    for _ in range(30):
        await asyncio.sleep(0.1)
        if not fake_serial.running:
            logger.warning("Serial reader stopped, stopping fake writer 1.")
            return
    await fake_serial.append_line("last")
    logger.debug("Write fake data complete.")

async def fake_writer2():
    logger.warning("Writing countdown to file")
    for i in range(COUNT_TO, 0, -1):
        if not fake_serial.running:
            logger.warning("Serial reader stopped, stopping fake writer 2.")
            return
        await fake_serial.append_line(f"This is line {i}.")
        await asyncio.sleep(WRITE_INTERVAL)
    logger.debug("Writing countdown complete.")

async def async_main():
    task_serial = asyncio.create_task(fake_serial.run())
    task_writer1 = asyncio.create_task(fake_writer1())
    task_writer2 = asyncio.create_task(fake_writer2())

    await task_serial
    await task_writer1
    await task_writer2


asyncio.run(async_main())
