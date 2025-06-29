import asyncio
import aiohttp
import os
from datetime import datetime

TASK_ID = os.getenv("TASK_ID", "null")
MONITORING_SERVICE_API = os.getenv("MONITORING_SERVICE_API", "http://35.198.209.90:10303/api/heartbeat")
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "60"))

if TASK_ID == "null":
    print("[X] TASK_ID environment variable is not set. Exiting.")
    exit(1)

async def send_heartbeat(session: aiohttp.ClientSession):
    try:
        async with session.post(
            MONITORING_SERVICE_API, json={"task_id": TASK_ID}
        ) as response:
            if response.status == 200:
                print(f"[{datetime.now().isoformat()}] [✓] Heartbeat sent for {TASK_ID}")
            else:
                text = await response.text()
                print(f"[{datetime.now().isoformat()}] [!] Failed to send heartbeat: {response.status} - {text}")
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] [X] Exception sending heartbeat: {e}")


async def run_heartbeat_loop():
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        while True:
            await send_heartbeat(session)
            await asyncio.sleep(INTERVAL_SECONDS)


async def main():
    await asyncio.gather(run_heartbeat_loop())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Service stopped by user.")
