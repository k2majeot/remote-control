import os
import sys
import subprocess
import signal
import logging
import threading
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

processes = []

def stream_output(proc: subprocess.Popen, name: str):
    for line in proc.stdout:
        logging.info(f"[{name}] {line.rstrip()}")


def start_script(name: str, script: str) -> subprocess.Popen:
    proc = subprocess.Popen(
        [sys.executable, script],
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
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    http_proc = start_script("HTTP server", os.path.join("src", "http_server.py"))
    remote_proc = start_script("Remote server", os.path.join("src", "remote_server.py"))

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
