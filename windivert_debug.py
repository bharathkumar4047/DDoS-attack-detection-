from pydivert import WinDivert

print("Waiting for packets... Open a browser now.")

with WinDivert("true") as w:
    for packet in w:
        print("PACKET:", packet.src_addr, "→", packet.dst_addr)
        break
