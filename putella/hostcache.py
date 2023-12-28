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


cache = [("127.0.0.1", 9879)]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(hc_addr)
sock.listen()
conn, addr = sock.accept()

def occasional_shuffle(interval: int = 10):
    while True:
        random.shuffle(cache)
        time.sleep(interval)


Thread(target=occasional_shuffle).start()

while True:
    data = conn.recv(1024)
    if data:
        print(data)