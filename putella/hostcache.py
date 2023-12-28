from threading import Thread
import random
import socket
import time
from typing import Tuple
"""
NOTE: This implementation is incorrect. Host caches should, themselves, respond to gnutella PING requests
with multiple PONG descriptors, as per 3.2.2:
Pong descriptors are ONLY sent in response to an incoming Ping descriptor. Multiple Pong descriptors MAY be sent in response to a single Ping descriptor. This enables host caches to send cached servent address information in response to a Ping request."""
hc_addr = "127.0.0.1", 9878

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind(hc_addr)

cache = [("127.0.0.1", 9879)]

def occasional_shuffle(interval: int = 10):
    while True:
        random.shuffle(cache)
        time.sleep(interval)

def get_cache_response_bstr(req_addr: Tuple[str, int], n: int=5):
    # Type checks
    req_addr = (str(req_addr[0]) if req_addr[0] != str else req_addr[0], int(req_addr[1]) if req_addr[1] else req_addr[1])
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