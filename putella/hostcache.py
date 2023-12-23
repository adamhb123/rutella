from threading import Thread
import random
import socket
import time
from typing import Tuple

hc_addr = "127.0.0.1", 9878

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind(hc_addr)

cache = [("127.0.0.1", 9879)]

def occasional_shuffle(interval: int = 10):
    while True:
        random.shuffle(cache)
        time.sleep(interval)

def get_cache_response_bstr(req_addr: Tuple[str, int], n: int=5):
    filtered = filter(lambda entry: entry != req_addr, cache[:n])
    return ("RESPONSE\t" + "\t".join(map(lambda entry: f"{str(entry[0])}:{str(entry[1])}", filtered))).encode("ascii")


Thread(target=occasional_shuffle).start()

while True:
    data, addr = sock.recvfrom(1024)
    data = data.split(b"\t")
    gnutella_addr = data[1].split(b":")
    print("GNU")
    print(gnutella_addr)
    gnutella_addr = gnutella_addr[0].decode("ascii"), int(gnutella_addr[1])
    if data[0] == b"REQUEST":
        cache.append(gnutella_addr)
        sock.sendto(get_cache_response_bstr(gnutella_addr), addr)