from itertools import cycle
import asyncio


async def update_spinner(spin, spin_text, spin_event):
    spinner_cycle = cycle(['-', '\\', '|', '/'])
    while not spin_event.is_set():
        spin.set_description(f"{spin_text} {next(spinner_cycle)}")
        spin.refresh()
        await asyncio.sleep(0.1)


async def get_ip_address():
    process = await asyncio.create_subprocess_shell(
        "hostname -I | awk '{print $1}'",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        return stdout.decode().strip()
    else:
        raise Exception(f"Error getting IP address: {stderr.decode().strip()}")