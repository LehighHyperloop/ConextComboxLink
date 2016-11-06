from socket import *
s = socket(AF_INET, SOCK_DGRAM)
s.bind(('',53152))

while True:
    data, addr = s.recvfrom(1024)
    print "From: " + addr[0]
    print " ".join("{:02x}".format(ord(c)) for c in data)
    print data
