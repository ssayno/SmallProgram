import asyncio
from aiohttp import ClientSession

async def download_data(task_number):
    # 模拟下载过程，这里可以替换为您的实际下载函数
    print(f"Downloading task {task_number}")
    await asyncio.sleep(8 - task_number)
    return (task_number, f"Data for task {task_number}")

async def write_data(task_number, data):
    print(f"Writing task {task_number}: {data}")
    # 在这里将数据写入文件或其他存储介质

async def download_and_write(task_number, download_queue, write_queue):
    data = await download_data(task_number)
    print(f'Task {task_number} download finish')
    await download_queue.put(data)

    while True:
        current_task_number, current_data = await download_queue.get()

        if current_task_number == task_number:
            await write_queue.put((task_number, current_data))
            break
        else:
            await download_queue.put((current_task_number, current_data))

    while True:
        current_task_number, current_data = await write_queue.get()

        if current_task_number == task_number:
            await write_data(task_number, current_data)
            break
        else:
            await write_queue.put((current_task_number, current_data))

async def main():
    num_tasks = 5
    download_queue = asyncio.Queue()
    write_queue = asyncio.Queue()

    tasks = [download_and_write(i, download_queue, write_queue) for i in range(1, num_tasks + 1)]
    await asyncio.gather(*tasks)

asyncio.run(main())
