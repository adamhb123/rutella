# rutella gameplan
The project will first be prototyped in Python 3 ( see putella/ ) to ensure understanding of the spec, and then implemented in Rust. The Python version will be called putella. Smart fella? fart smella...
## Host Cache
The host cache will be a UDP server that nodes can contact to get a few partners through which it can communicate.

Asymmetric key encryption may be added later for integrity.

The REQUEST packet will  be a UDP packet, effectively a ping, with the following format:
    
    REQUEST\t<IP Address>:<Port Number>

Where \<IP Address> and \<Port Number> are the servent's Gnutella address info

The server will take the requestor's information and save it into the cache, as well.

The RESPONSE packet (from the host cache server) will be formatted as follows:
      
    RESPONSE\t<IP Address>:<Port Number>\t<IP Address>:<Port Number>\t...

So, it's just tab separated addresses. Very complex stuff!

The third type of packet, DEAD, will be sent by the Requestor if it cannot communicate with one of the received servents.

It will be formatted as follows:

    DEAD\t<IP Address>:<Port Number>\t<IP Address>:<Port Number>\t

It is identical to the RESPONSE packet, asides from the identifier at the beginning.
