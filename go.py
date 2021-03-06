#!/usr/bin/env python3
import subprocess
import asyncio
import random
import curses
import textwrap
# try running with PYTHONUNBUFFERED=1

stdscr = None
status_window = None
log_window = None

async def job(t):
    log_window.addstr(f"job({t}) start\n")
    await asyncio.sleep(t)
    result = random.random()
    if result < 0.4:
        raise TypeError
    # log_window.addstr(f"job({t}) complete")
    return True

async def download(url):
    result = random.random()
    if result < 0.2:
        await asyncio.sleep(result * 50)
        raise TypeError
    proc = await asyncio.create_subprocess_exec(
            'youtube-dl', str(url),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    await proc.wait()
    if proc.returncode != 0:
        log_window.addstr(f"{stderr.decode()}")
        raise ValueError(proc.returncode)
    else:
        return True


def schedule_fake_job(t):
    return asyncio.create_task(job(t), name=f"job({t})")

def schedule_real_job(url):
    return asyncio.create_task(download(url), name=f"download({url})")

async def main():
    log_window.addstr("main\n")
    log_window.refresh()
    with open("short-sweet.txt") as f:
        video_urls = [line.strip() for line in f.readlines()]
    all_tasks = [
            schedule_real_job(url) for url in video_urls
            ]
    active_tasks = all_tasks[:]
    success = []
    cancelled = []
    errored = []

    for index, task in enumerate(all_tasks):
        status_window.addstr(index, 0, f"{task.get_name()}\n")
        msg = "..."
        status_window.insstr(index, curses.COLS - 3 - len(msg), msg)
        # status_window.addstr(f"\n")
    status_window.refresh()

    # saboteur!
    sabotage_victim = random.randint(0,len(all_tasks)-1)
    log_window.addstr(f"sabotaging all_tasks[{sabotage_victim}]\n")
    log_window.refresh()
    all_tasks[sabotage_victim].cancel()

    log_window.nodelay(True)
    # log_window.timeout(10000)
    # import pydevd_pycharm
    # pydevd_pycharm.settrace('localhost', port=31337, stdoutToServer=True, stderrToServer=True)
    while True:
        # consume the whole input stream; if any is 'q', exit
        while (key := log_window.getch()) != -1:
            if key in (ord('q'), ord('Q')):
                exit(0)

        # if the input routine could be awaitable, you might be able to do:
        #   for outcome in asyncio.as_completed((sleep(1), read_input()))
        # or something... the intention is that finding input shouldn't be blocked by sleep
        await asyncio.sleep(1)
        log_window.refresh()
        for task in active_tasks[:]:
            if task.done():
                index = all_tasks.index(task)  # poor scaling, but effective
                try:
                    task.result()
                    success.append(task)
                    log_window.addstr(f"{task.get_name()} succeeded\n")
                    status_window.addstr(index, 0, f"{task.get_name()}\n")
                    msg = "cool"
                    status_window.insstr(index, curses.COLS - 3 - len(msg), msg)
                except asyncio.CancelledError:
                    cancelled.append(task)
                    log_window.addstr(f"{task.get_name()} was cancelled\n")
                    status_window.addstr(index, 0, f"{task.get_name()}\n")
                    msg = "killed by chaos monkey"
                    status_window.insstr(index, curses.COLS - 3 - len(msg), msg)
                except Exception as e:
                    errored.append(task)
                    log_window.addstr(f"{task.get_name()} hit an error\n")
                    status_window.addstr(index, 0, f"{task.get_name()}\n")
                    msg = "whoops"
                    status_window.insstr(index, curses.COLS - 3 - len(msg), msg)
                status_window.refresh()
                active_tasks.remove(task)
        if not active_tasks:
            # it's been whittled down to an empty list
            break
    # await asyncio.gather(*tasks)
    log_window.addstr("main done\n")
    log_window.addstr(f"success: {[t.get_name() for t in success]}\n")
    log_window.addstr(f"cancelled: {[t.get_name() for t in cancelled]}\n")
    log_window.addstr(f"errored: {[t.get_name() for t in errored]}\n")
    log_window.addstr(f"errored: {errored}\n")
    log_window.refresh()
    log_window.addstr("Press any key to exit\n")
    log_window.nodelay(False)
    log_window.getch()


def lets_a_go(curses_scr):
    global stdscr, status_window, log_window
    stdscr = curses_scr
    status_window_outer = curses.newwin(
            18, curses.COLS - 1,
            0, 0)
    status_window_outer.clear()
    status_window_outer.border(0, 0, 0, 0, 0, 0, 0, 0)
    status_window_outer.refresh()
    import time
    # time.sleep(1)
    status_window = curses.newwin(
            18-2, curses.COLS - 3,
            1, 1)
    status_window.clear()
    log_window_outer = curses.newwin(
            10, curses.COLS - 1,
            curses.LINES - 10, 0
            # curses.COLS - 1, curses.LINES - 1
    )
    log_window_outer.clear()
    log_window_outer.border(0, 0, 0, 0, 0, 0, 0, 0)
    log_window_outer.refresh()
    log_window = log_window_outer.derwin(
            8, curses.COLS - 3,
            1, 1
            )
    log_window.scrollok(True)
    # curses.noecho()
    # curses.cbreak()
    curses.curs_set(False)  # don't show the cursor
    stdscr.clear()
    log_window.addstr("hello, world!\n")
    # log_window.refresh()

    asyncio.run(main(), debug=False)
    # stdscr.refresh()

if __name__ == '__main__':
    curses.wrapper(lets_a_go)
