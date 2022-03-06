from __future__ import print_function
from pyrad.client import Client
from pyrad.dictionary import Dictionary
import socket
import sys
import pyrad.packet
import poll

poll.install()
srv = Client(server="10.99.0.2", secret=b"w8waLW3GExg925j3", dict=Dictionary("dictionary.txt"))

req = srv.CreateAuthPacket(code=pyrad.packet.AccessRequest, User_Name="wichert")

req["User-Name"] = "58:cb:52:0e:dd:24"
req["User-Password"] = "58:cb:52:0e:dd:24"
req["Message-Authenticator"] = "0x00"

try:
    print("Sending authentication request")
    reply = srv.SendPacket(req)
except pyrad.client.Timeout:
    print("RADIUS server does not reply")
    sys.exit(1)
except socket.error as error:
    print("Network error: " + error[1])
    sys.exit(1)

if reply.code == pyrad.packet.AccessAccept:
    print("Access accepted")
else:
    print("Access denied")

print("Attributes returned by server:")
for i in reply.keys():
    print("%s: %s" % (i, reply[i]))