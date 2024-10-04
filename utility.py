from itertools import cycle
import asyncio


async def update_spinner(spin, spin_text, spin_event):
    spinner_cycle = cycle(['-', '\\', '|', '/'])
    while not spin_event.is_set():
        spin.set_description(f"{spin_text} {next(spinner_cycle)}")
        spin.refresh()
        await asyncio.sleep(0.1)