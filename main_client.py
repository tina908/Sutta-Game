import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    msg = input("->")
    sock.sendto(msg.encode(),("127.0.0.1", 12345))
    recvmsg, addr = sock.recvfrom(2048)
    if recvmsg.decode()=="success":
        print("login success")
        break
    else : continue
