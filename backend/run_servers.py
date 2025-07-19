import os
import sys
import subprocess
import signal
import logging
import threading
import time
import argparse
import json
import socket

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
CONFIG_PATH = os.path.join(BASE_DIR, "server_config.json")
processes = []


def get_private_ip() -> str:
    """Attempt to determine the machine's LAN IP."""
    ip = "127.0.0.1"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
    except OSError:
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except OSError:
            pass
    return ip


def stream_output(proc: subprocess.Popen, name: str):
    for line in proc.stdout:
        logging.info(f"[{name}] {line.rstrip()}")


def start_script(name: str, script: str) -> subprocess.Popen:
    proc = subprocess.Popen(
        [sys.executable, os.path.join(SCRIPT_DIR, script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    threading.Thread(target=stream_output, args=(proc, name), daemon=True).start()
    logging.info(f"Started {name} (pid {proc.pid})")
    return proc


def stop_processes():
    for proc in processes:
        if proc.poll() is None:
            logging.info(f"Stopping pid {proc.pid}")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logging.warning(f"Pid {proc.pid} did not terminate, killing")
                proc.kill()


def handle_signal(signum, frame):
    logging.info("Received shutdown signal")
    stop_processes()
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Run Remote Control servers")
    parser.add_argument(
        "--whitelist",
        nargs="+",
        help="Space or comma separated list of IPs to allow",
    )
    args = parser.parse_args()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    config = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                logging.warning("Invalid JSON in config, starting with empty config")

    config["host"] = get_private_ip()
    if args.whitelist is not None:
        wl = []
        for item in args.whitelist:
            wl.extend(i.strip() for i in item.split(",") if i.strip())
        config["whitelist"] = wl

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

    http_proc = start_script("HTTP server", "http_server.py")
    remote_proc = start_script("Remote server", "remote_server.py")

    processes.extend([http_proc, remote_proc])

    try:
        while True:
            for proc in processes:
                ret = proc.poll()
                if ret is not None:
                    logging.error(f"Process pid {proc.pid} exited with code {ret}")
                    handle_signal(None, None)
            time.sleep(1)
    except KeyboardInterrupt:
        handle_signal(None, None)


if __name__ == "__main__":
    main()
