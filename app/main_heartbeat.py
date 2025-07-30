import asyncio
import aiohttp
import os
from datetime import datetime

# === Cấu hình môi trường ===
TASK_ID = os.getenv("TASK_ID", "null")
MONITORING_SERVICE_API = os.getenv("MONITORING_SERVICE_API", "http://35.198.209.90:10303/api/heartbeat")
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "60"))

if TASK_ID == "null":
    print("[X] TASK_ID environment variable is not set. Exiting.")
    exit(1)

# === Đường dẫn tuyệt đối đến các file cần kiểm tra (tính từ vị trí file này) ===
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../", TASK_ID))

train_file_path = os.path.join(BASE_PATH, "dataset/train.csv")
test_file_path = os.path.join(BASE_PATH, "dataset/test.csv")
preprocessing_logs_path = os.path.join(BASE_PATH, "preprocessing_data_logs.txt")
training_logs_path = os.path.join(BASE_PATH, "model/autogluon/training_logs.txt")
is_training_progress_bug = False

# === Gửi heartbeat với trạng thái dataset ===
async def send_heartbeat(session: aiohttp.ClientSession):
    dataset_status = "PENDING"

    train_exists = os.path.exists(train_file_path)
    test_exists = os.path.exists(test_file_path)
    pre_log_exists = os.path.exists(preprocessing_logs_path)

    if pre_log_exists:
        if not (train_exists and test_exists):
            dataset_status = "NOT_FOUND"
        else:
            dataset_status = "OK"

    payload = {
        "task_id": TASK_ID,
        "dataset_status": dataset_status,
        "is_training_progress_bug": is_training_progress_bug
    }

    try:
        async with session.post(MONITORING_SERVICE_API, json=payload) as response:
            if response.status == 200:
                print(f"[{datetime.now().isoformat()}] [✓] Heartbeat sent for {TASK_ID} (dataset_status={dataset_status})")
                if dataset_status == "NOT_FOUND":
                    print(f"[{datetime.now()}] Dataset NOT_FOUND for task {TASK_ID}")
                    exit(1)
                if is_training_progress_bug:
                    print(f"[{datetime.now()}] Training is not progressing..!")
                    exit(1)
            else:
                text = await response.text()
                print(f"[{datetime.now().isoformat()}] [!] Failed to send heartbeat: {response.status} - {text}")
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] [X] Exception sending heartbeat: {e}")


def count_lines(filepath):
    try:
        with open(filepath, 'r') as f:
            return sum(1 for _ in f)
    except FileNotFoundError:
        return -1  # File chưa tồn tại


# === Theo dõi log để phát hiện việc training bị dừng ===
async def monitor_log_file(filepath: str, task_id: str, interval_sec=180):
    print(f"🔍 Monitoring {filepath} every {interval_sec} seconds...")
    last_line_count = count_lines(filepath)
    while True:
        await asyncio.sleep(interval_sec)
        current_line_count = count_lines(filepath)
        if current_line_count == last_line_count:
            print(f"[⚠️] No new log lines detected. Restarting training for task {task_id}")
            is_training_progress_bug = True
        else:
            print(f"[✅] Log growing: {last_line_count} -> {current_line_count}")
        last_line_count = current_line_count


# === Vòng lặp gửi heartbeat ===
async def run_heartbeat_loop():
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        while True:
            await send_heartbeat(session)
            await asyncio.sleep(INTERVAL_SECONDS)

# === Entry point ===
async def main():
    heartbeat_task = asyncio.create_task(run_heartbeat_loop())
    monitor_task = asyncio.create_task(monitor_log_file(training_logs_path, TASK_ID, interval_sec=180))
    await asyncio.gather(heartbeat_task, monitor_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Heartbeat service stopped by user.")
