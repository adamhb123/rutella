from abc import ABC, abstractmethod

from enum import Enum
import random
import socket
import struct
from threading import Thread
from queue import Queue, Empty
from typing import Tuple
from uuid import uuid4

GNUTELLA_TTL = 7
# Servent guid
servent_guid = uuid4().bytes

gnutella_addr = ("127.0.0.1", random.randint(10000,12000))
direct_peers = []
gnutella_command_queue = Queue()
trigger_hc_request_flag = False
last_query_hits = None

class DescriptorType:
    Ping = b"\x00"
    Pong = b"\x01"
    Push = b"\x40"
    Query = b"\x80"
    QueryHits = b"\x81"

class DescriptorPayload(ABC):
    @abstractmethod
    def to_packet(self) -> bytes:
        """Convert descriptor payload to packet
        """
        ...

class PingDescriptorPayload(DescriptorPayload):
    def to_packet(self) -> bytes:
        """Ping descriptors have no payload"""
        return b""

class PongDescriptorPayload(DescriptorPayload):
    def __init__(self, port: int, ip_address: str, n_files_shared: int, n_kb_shared: int):
        self.port = port
        self.ip_address = ip_address
        self.n_files_shared = n_files_shared
        self.n_kb_shared = n_kb_shared

    def to_packet(self) -> bytes:
        return struct.pack("!H4sII", self.port, socket.inet_aton(self.ip_address), self.n_files_shared, self.n_kb_shared)
    
class QueryDescriptorPayload(DescriptorPayload):
    def __init__(self, minimum_speed: int, search_term: str):
        self.minimum_speed = minimum_speed
        self.search_term = search_term

    def to_packet(self) -> bytes:
        search_term_bytes_nul_terminated = self.search_term.encode('ascii') + b'\x00'
        return struct.pack(f"!H{len(search_term_bytes_nul_terminated)}s", self.minimum_speed, search_term_bytes_nul_terminated)
    
class ResultSetPayload(DescriptorPayload):
    def __init__(self, file_index: int, file_size: int, shared_file_name: str):
        self.file_index = file_index
        self.file_size = file_size
        self.shared_file_name = shared_file_name
    def to_packet(self) -> bytes:
        + b"\x00\x00"
class QueryHitsDescriptorPayload(DescriptorPayload):
    def __init__(self, number_of_hits: int, port: int, ip_address: str, speed: int, result_set: ResultSetPayload):
        self.number_of_hits = number_of_hits
        self.port = port
        self.ip_address = ip_address
        self.speed = speed
        self.result_set = result_set

    def to_packet(self) -> bytes:
        return struct.pack("!BH4sI", self.number_of_hits, self.port, socket.inet_aton(self.ip_address), self.speed) + self.result_set.to_packet() + struct.pack("!16s", servent_guid)
    
class Descriptor:
    def __init__(self, descriptor_type: DescriptorType, payload: DescriptorPayload, TTL=GNUTELLA_TTL) -> None:
        self.descriptor_id = uuid4().bytes
        self.descriptor_type = descriptor_type
        self.TTL = TTL
        self.hops = 0
        self.payload = payload
       # self.payload = 
    def to_packet(self):
        payload_packet = self.payload.to_packet()
        return struct.pack("!16sBBI", self.descriptor_id, self.TTL, self.hops, len(payload_packet)) + payload_packet
    
o = PongDescriptorPayload(12455, "192.168.4.4", 1, 36)
print(o)
packet = o.to_packet()
descriptor = Descriptor(DescriptorType.Pong, o)
descriptor_packet = descriptor.to_packet()
print(struct.unpack("!16sBBIH4sII", descriptor_packet))
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