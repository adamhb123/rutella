from abc import ABC, abstractmethod
import socket
import struct
from typing import List
from uuid import uuid4

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
    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.to_packet()}"

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
    
class ResultPayload(DescriptorPayload):
    def __init__(self, file_index: int, file_size: int, shared_file_name: str):
        self.file_index = file_index
        self.file_size = file_size
        self.shared_file_name = shared_file_name

    def to_packet(self) -> bytes:
        return struct.pack(f"!II{len(self.shared_file_name)}sxx",self.file_index, self.file_size, self.shared_file_name.encode("ascii"))

class QueryHitsDescriptorPayload(DescriptorPayload):
    def __init__(self, port: int, ip_address: str, speed: int, result_set: List[ResultPayload], servent_guid: bytes):
        self.number_of_hits = len(result_set)
        self.port = port
        self.ip_address = ip_address
        self.speed = speed
        self.result_set = result_set
        self.servent_guid = servent_guid

    def result_set_to_packet(self) -> bytes:
        return b''.join(map(lambda res: res.to_packet(), self.result_set))

    def to_packet(self) -> bytes:
        return struct.pack("!BH4sI", self.number_of_hits, self.port, socket.inet_aton(self.ip_address), self.speed) + self.result_set_to_packet() + struct.pack("!16s", self.servent_guid)
    
class Descriptor:
    def __init__(self, descriptor_type: DescriptorType, payload: DescriptorPayload, TTL: int) -> None:
        self.descriptor_id = uuid4().bytes
        self.descriptor_type = descriptor_type
        self.payload = payload
        self.TTL = TTL
        self.hops = 0
       # self.payload = 
    def to_packet(self):
        payload_packet = self.payload.to_packet()
        return struct.pack("!16sBBI", self.descriptor_id, self.TTL, self.hops, len(payload_packet)) + payload_packet
    
def tests():
    ping = PingDescriptorPayload()
    pong = PongDescriptorPayload(12455, "192.168.4.4", 1, 36)
    query = QueryDescriptorPayload(256, "Bananas")
    result_set = [ResultPayload(123, 123, "Swaggedout.mp3")]
    query_hits = QueryHitsDescriptorPayload(12455, "192.168.4.4", 256, result_set, uuid4().bytes.replace(b"-",b""))
    print(ping)
    print(pong)
    print(query)
    print(result_set)
    print(query_hits)

if __name__=="__main__":
    tests()