#!/usr/bin/env python3

"""
Send/receive UDP multicast packets.
Requires that your OS kernel supports IP multicast.

Usage:
  mcast -s (sender, IPv4)
  mcast -s -6 (sender, IPv6)
  mcast    (receivers, IPv4)
  mcast  -6  (receivers, IPv6)
"""

MYPORT = 8123
MYGROUP_4 = '225.0.0.250'
MYGROUP_6 = 'ff15:7079:7468:6f6e:6465:6d6f:6d63:6173'
MYTTL = 1 # Increase to reach other networks

agiza time
agiza struct
agiza socket
agiza sys

eleza main():
    group = MYGROUP_6 ikiwa "-6" kwenye sys.argv[1:] isipokua MYGROUP_4

    ikiwa "-s" kwenye sys.argv[1:]:
        sender(group)
    isipokua:
        receiver(group)


eleza sender(group):
    addrinfo = socket.getaddrinfo(group, Tupu)[0]

    s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)

    # Set Time-to-live (optional)
    ttl_bin = struct.pack('@i', MYTTL)
    ikiwa addrinfo[0] == socket.AF_INET: # IPv4
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
    isipokua:
        s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, ttl_bin)

    wakati Kweli:
        data = repr(time.time()).encode('utf-8') + b'\0'
        s.sendto(data, (addrinfo[4][0], MYPORT))
        time.sleep(1)


eleza receiver(group):
    # Look up multicast group address kwenye name server na find out IP version
    addrinfo = socket.getaddrinfo(group, Tupu)[0]

    # Create a socket
    s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)

    # Allow multiple copies of this program on one machine
    # (sio strictly needed)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind it to the port
    s.bind(('', MYPORT))

    group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
    # Join group
    ikiwa addrinfo[0] == socket.AF_INET: # IPv4
        mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    isipokua:
        mreq = group_bin + struct.pack('@I', 0)
        s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)

    # Loop, printing any data we receive
    wakati Kweli:
        data, sender = s.recvfrom(1500)
        wakati data[-1:] == '\0': data = data[:-1] # Strip trailing \0's
        andika(str(sender) + '  ' + repr(data))


ikiwa __name__ == '__main__':
    main()
