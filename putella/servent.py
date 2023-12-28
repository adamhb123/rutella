from abc import ABC, abstractmethod

from enum import Enum
import random
import socket
import struct
from threading import Thread
from queue import Queue, Empty
from typing import Tuple
from uuid import uuid4
import descriptor

GNUTELLA_TTL = 7
# Servent guid
servent_guid = uuid4().bytes

hc_addr = "127.0.0.1", 9878

gnutella_addr = ("127.0.0.1", random.randint(10000,12000))
direct_peers = []
gnutella_command_queue = Queue()
trigger_hc_request_flag = False
last_query_hits = None

hc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
packet = descriptor.PongDescriptorPayload(6969,"192.168.1.1",24,256).to_packet()
print(packet)
hc_sock.connect(hc_addr)
hc_sock.send(packet)
quit()
class GnutellaCommands(Enum):
    Connect=0
    Search=1
    QueryHits=2
    Download=3

def repl():
    global trigger_hc_request_flag
    _help_msg = """putella help
    {get_peers, g} - retrieve peers from the hostcache
    {connect, c} [IP_ADDRESS]:[PORT] - connect to network through given servent
    {search, query, s, q} [SEARCH_TERM] - search (query) network for files matching [SEARCH_TERM]
    {query_hits, qh} - Print last QueryHits result
    {download, d} [FILE_INDEX] [FILE_NAME]
"""
    while True:
        _input = input(">").strip().split()
        if _input[0].lower() in ["get_peers", "g"]:
            trigger_hc_request_flag = True
        elif _input[0].lower() in ["connect", "c"]:
            pass
        elif _input[0].lower() in ["search", "query", "s", "q"]:
            pass
        elif _input[0].lower() in ["query_hits", "qh"]:
            pass
        elif _input[0].lower() in ["download", "d"]:
            pass
        else:
            print(_help_msg)

def gnutella_thread():
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW)
    sock.setblocking(False)
    while True:
        data, addr = sock.recvfrom(1024)
        if data:
            print(data)
        try:
            command = gnutella_command_queue.get_nowait()
        except Empty as e:
            pass
        print("Peers: ", direct_peers)

def host_cache_thread():
    global trigger_hc_request_flag
    def parse_recv_host_cache(data):
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
    
    # Contact hostcache
    hc_addr = "127.0.0.1", 9878
    hc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hc_sock.sendto(f"REQUEST\t{gnutella_addr[0]}:{str(gnutella_addr[1])}".encode("ascii"), hc_addr)
    hc_sock.setblocking(False)
    while True:
        data, addr = hc_sock.recvfrom(1024)
        if data:
            if addr == hc_addr:
                parse_recv_host_cache(data)
            print("Host Cache Returned Peers: ", direct_peers)
        if trigger_hc_request_flag:
            hc_sock.sendto(f"REQUEST\t{gnutella_addr[0]}:{str(gnutella_addr[1])}".encode("ascii"), hc_addr)
            trigger_hc_request_flag = False

if __name__ == "__main__":
    Thread(target=host_cache_thread).start()
    Thread(target=gnutella_addr).start()
    repl()