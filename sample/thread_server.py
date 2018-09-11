import socket
import threading
import time
# import struct
import re

HOST = 'localhost'
PORT = 8808


def process(sock, addr):
    # message = b''
    # while True:
    #     try:
    #         addOn = sock.recv(1024)
    try:
        print("in")
        sock.sendall(b'haha')
        while True:
            time.sleep(3)
            pass
        print("out")
    finally:
        print("hahahahaha finally closed!")
        sock.close()

def main():
    UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    UDPsocket.bind((HOST, PORT))
    UDPsocket.listen()
    while True:
        # print("step 1")
        (sock, addr) = UDPsocket.accept()
        # print("step 2")
        processor = threading.Thread(target=process, args=[sock, addr])
        # processor.setDaemon(True)
        # print("step 3")
        processor.start()
        # print("step 4")
        pass



if __name__ == '__main__':
    main()




# def receive(webSock):
#     # file_target = open("log.txt", 'w')
#     # file_target.write("")
#     # file_target.close()
#     file_target = open("log.txt", 'a')
#     while True:
#         try:
#             message = b''
#             while True:
#                 # print("I am here1 ")
#                 addOn = webSock.recv(1024)
#                 message += addOn
#                 if len(addOn) != 1024:
#                     break
#                 pass
#
#             if not message:
#                 break
#             # webSock.sendall(message)
#             # allMessage += message
#
#             file_target.write("Message in byte is ")
#             file_target.write(str(message))
#             file_target.write("\n\n")
#             file_target.write("Message in string is ")
#             try:
#                 file_target.write(message.decode())
#             except:
#                 file_target.write("such line cannot decode")
#             file_target.write("\n")
#         except socket.error as e:
#             file_target.write("socket error is " + str(e))
#             pass
#         pass
#
#
#     pass
#
#
# def process(sock, addr):
#     print("User connect in: " + str(addr))
#     print("User information type is " + str(type(addr)))
#     ipv4 = socket.gethostbyname_ex("www.cnn.com")[-1][0]
#     port = 80
#     webSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     webSock.connect((ipv4, port))
#
#     receiver = threading.Thread(target=receive, args=[webSock])
#     receiver.start()
#     allMessage = b''
#     loop_count = 0
#     while True:
#         try:
#             endLine = [b'\r\n\r\n', b'\r\n\n', b'\n\n', b'\n\r\n']
#             header = ""
#             result = b''
#             while True:
#                 # print("I am here1 ")
#                 addOn = sock.recv(1024)
#                 end = False  # if find separator
#                 for line in endLine:  # if any separator in current line
#                     if line in addOn and not result:
#                         print("Here 1")
#                         end = True
#                         parts = addOn.split(line)
#                         header += parts[0].decode()
#                         result += line.join(parts[1:])
#                         break
#                     pass
#                 if not end:  # found no separator
#                     if result:
#                         print("Here 2")
#                         result += addOn
#                     else:
#                         print("here 3")
#                         header += addOn.decode()
#                         pass
#                     pass
#                 if len(addOn) != 1024:
#                     break
#                 pass
#             allMessage += addOn
#             if not header:
#                 break
#
#             print("Got message ")
#             print(str(allMessage))
#             print("\n")
#             print("Got header ")
#             print(str(header))
#             print("Got header in byte ")
#             print(str(header.encode()))
#             print("\n\n")
#
#             header = header.split('\n')
#             print("Header list is ")
#             print(str(header))
#             headerMessage = ""
#             for term in header:
#                 term = term.strip()
#                 # if "GET" in term or "HEAD" in term or "POST" in term or \
#                 # "PUT" in term or "DELETE" in term or "OPTION" in term or \
#                 # "TRACE" in term or "PATCH" in term or "CONNECT" in term:
#                 #     if term[-3:] == "1.1":
#                 #         term = term[:-3] + "1.0"
#                 #         pass
#                 # elif re.search("Connection", term, re.IGNORECASE):  # current line is connect method line
#                 #     term = "Connection: close"
#                 # elif re.search("Proxy-connection", term, re.IGNORECASE):
#                 #     term = "Proxy-connection: close"
#                 #     pass
#                 headerMessage += term + "\r\n"
#                 pass
#             header = headerMessage + "\r\n"
#             # header = headerMessage[:-2]
#             print("Now header is ")
#             print(header)
#             print("Now header in byte is ")
#             header = header.encode()
#             print(str(header))
#             print("\n\n")
#             message = header + result
#             print("Now message in all is ")
#             print(message.decode())
#             print("Now message in all in byte is ")
#             print(str(message))
#
#
#
#             webSock.sendall(message)
#             allMessage += message
#             loop_count += 1
#             # print("Message in byte is ")
#             # print(str(allMessage))
#             # print("\n\n")
#             # print("Message in string is ")
#             # print(allMessage.decode())
#             # print("enter the loop " + str(loop_count))
#             # print("\n")
#
#         except socket.error as e:
#             print("socket error is " + str(e))
#             pass
#         pass
#     # print("Message in byte is ")
#     # print(str(allMessage))
#     # print("\n\n")
#     # print("Message in string is ")
#     # print(allMessage.decode())
#     # print("\n")









