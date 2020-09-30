#!/usr/bin/env python3
import subprocess
import asyncio
import random
# try running with PYTHONUNBUFFERED=1

async def job(t):
    print(f"job({t}) start")
    await asyncio.sleep(t)
    result = random.random()
    if result < 0.4:
        raise TypeError
    # print(f"job({t}) complete")
    return True

def schedule_job(t):
    return asyncio.create_task(job(t), name=f"job({t})")

async def main():
    print("main")
    all_tasks = [
            schedule_job(0.5),
            schedule_job(1),
            schedule_job(1.5),
            schedule_job(3),
            schedule_job(4),
            schedule_job(5),
            ]
    active_tasks = all_tasks[:]
    success = []
    cancelled = []
    errored = []

    # saboteur!
    sabotage_victim = random.randint(0,len(all_tasks)-1)
    print(f"sabotaging all_tasks[{sabotage_victim}]")
    all_tasks[sabotage_victim].cancel()

    for task in asyncio.as_completed(all_tasks):
        if task.done():
            # print(f"task {task.get_name()} over")
            try:
                task.result()
                success.append(task)
                print(f"{task.get_name()} succeeded")
            except asyncio.CancelledError:
                cancelled.append(task)
                print(f"{task.get_name()} was cancelled")
            except Exception as e:
                errored.append(task)
                print(f"{task.get_name()} hit an error")
            # active_tasks.remove(task)
    await asyncio.gather(*tasks)
    print("main done")
    print(f"success: {[t.get_name() for t in success]}")
    print(f"cancelled: {[t.get_name() for t in cancelled]}")
    print(f"errored: {[t.get_name() for t in errored]}")


if __name__ == '__main__':
    asyncio.run(main(), debug=True)
