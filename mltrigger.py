import socket
import time

TARGET_IP = "127.0.0.1"
TARGET_PORT = 5555

PACKET_SIZE = 1400
PACKETS_PER_SEC = 3000
DURATION = 10

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
payload = b"A" * PACKET_SIZE

interval = 1.0 / PACKETS_PER_SEC
end = time.time() + DURATION
sent = 0

print("[*] Starting ML-aligned traffic")

while time.time() < end:
    sock.sendto(payload, (TARGET_IP, TARGET_PORT))
    sent += 1
    time.sleep(interval)

print(f"[+] Sent {sent} packets")
