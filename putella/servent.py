import random
import socket
from threading import Thread

gnutella_addr = ("127.0.0.1", random.randint(10000,12000))
direct_peers = []

def parse_recv(data):
    print(data)
    data = data.split(b"\t")
    if data[0] == b"RESPONSE":
        print("Response:", data)
        for addr in data[1:]:
            addr = addr.split(b":")
            new_peer = (addr[0].decode(), int(addr[1]))
            if new_peer != gnutella_addr:
                direct_peers.append(new_peer)
    return data
def host_cache_thread():
    # Contact hostcache
    hc_addr = "127.0.0.1", 9878
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(f"REQUEST\t{gnutella_addr[0]}:{str(gnutella_addr[1])}".encode("ascii"), hc_addr)
    while True:
        data, addr = sock.recvfrom(1024)
        parse_recv(data)
        print("Peers: ", direct_peers)

Thread(target=host_cache_thread).start()