import asyncio
import aiofiles
import os

THE_FILE = '/tmp/the_file.txt'
COUNT_TO = 20
WRITE_INTERVAL = 0.5  # seconds

class AsyncFileWriter:
    def __init__(self, filename: str):
        self.filename = filename
        self._data_arrived_callbacks = []
        self._closed_callbacks = []
        self._is_running = False

    def run(self):
        asyncio.run(self.async_run())

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

    async def async_run(self):
        self._is_running = True

        write_task = asyncio.create_task(self.count_down_to_file())
        read_task = asyncio.create_task(self.read_file())
        try:
            await write_task
            self._is_running = False
            await read_task
        except asyncio.CancelledError:
            
            print()
            print("Tasks were cancelled.")
            self._is_running = False
            if not write_task.done():
                await write_task
            await read_task
        finally:
            for callback in self._closed_callbacks:
                await callback()


    async def count_down_to_file(self):
        for i in range(1, COUNT_TO+1):
            if not self._is_running:
                break
            async with aiofiles.open(self.filename, 'a') as f:
                await f.write(f"This is line {i}.\n")
            print(f"Wrote line {i} to file.")
            await asyncio.sleep(WRITE_INTERVAL)
        print("Write complete.")

    async def read_file(self):
        f = await aiofiles.open(self.filename, 'r')
        await f.seek(0)
        while True:
            async for line in f:
                print(f"File contents read: {line.strip()}")
                for callback in self._data_arrived_callbacks:
                    await callback(line.strip())
            if not self._is_running:
                break
            await asyncio.sleep(0)
        await f.close()
        print("Read complete.")


if os.path.exists(THE_FILE):
    os.remove(THE_FILE)

# Create empty file
with open(THE_FILE, 'w') as file:
    pass

writer = AsyncFileWriter(THE_FILE)
@writer.on_data_arrived()
async def on_data_arrived(data):
    print(f"Data arrived in callback: {data}")

@writer.on_closed()
async def on_closed():
    print("File writer closed.")

writer.run()
