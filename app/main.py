import asyncio
import aiohttp
from config import MONITORING_SERVICE_URL, COMPUTE_ID, INTERVAL_SECONDS


async def send_heartbeat(session: aiohttp.ClientSession):
    try:
        async with session.post(
            MONITORING_SERVICE_URL, json={"compute_id": COMPUTE_ID}
        ) as response:
            if response.status == 200:
                print(f"[✓] Heartbeat sent for {COMPUTE_ID}")
            else:
                text = await response.text()
                print(f"[!] Failed to send heartbeat: {response.status} - {text}")
    except Exception as e:
        print(f"[X] Exception sending heartbeat: {e}")


async def run_heartbeat_loop():
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        while True:
            await send_heartbeat(session)
            await asyncio.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    print(
        f"[~] Starting async heartbeat loop for {COMPUTE_ID} every {INTERVAL_SECONDS}s"
    )
    try:
        asyncio.run(run_heartbeat_loop())
    except KeyboardInterrupt:
        print("\n[!] Heartbeat service stopped by user.")
