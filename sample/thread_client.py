import socket
import struct
import time
import threading

HOST = 'localhost'
PORT = 8808
# PORT = 46108

# message = b'CONNECT 127.0.0.1:8808 HTTP/1.1\r\n' \
#     b'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:56.0) Gecko/20100101 Firefox/56.0\r\n' \
#     b'Proxy-Connection: keep-alive\r\nConnection: keep-alive\r\n' \
#     b'Host: 127.0.0.1:8808\r\n\r\n'

def test(sock):
    try:
        while True:
            messsage = b''
            while True:
                print("Line 1")
                addOn = sock.recv(1024)
                print("Line 2")
                messsage += addOn
                if len(addOn) != 1024:
                    break

                pass
            print("Line 4")
            if not messsage:
                print("Line 5")
                break

            print("Receive message in bytes ")
            print(str(messsage))

    except socket.error as e:
        print("meet error is " + str(e))
    finally:
        print("socket close 1")
        sock.close()
        print("socket close 2")
        pass



def termi(sock):
    while True:
        try:
            line = input()
            if line == 'q':
                termhelper(sock)
                break

        except EOFError:
            # should terminate
            termhelper(sock)
            break
        pass
    pass

def termhelper(sock):
    print("help to closing")
    # sock.setblocking(0)
    # sock.close()
    try:
        sock.shutdown(socket.SHUT_RDWR)
        sock.shutdown(socket.SHUT_RDWR)
    except:
        pass
    # sock.settimeout(1)
    print("closed")


def main():
    # message = ""
    # with open("test.txt", 'r') as lines:
    #     for line in lines:
    #         message += line
    #         pass
    #     pass

    # messageA = "hahah"
    # messageB = "hehehehehehehe"
    # message = "haha"

    TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TCPsocket.connect((HOST, PORT))

    # TCPsocket.settimeout(3)

    sender = threading.Thread(target=test, args=[TCPsocket])
    sender.start()

    terminator = threading.Thread(target=termi, args=[TCPsocket])
    terminator.start()

    # TCPsocket.sendall(messageA.encode())
    # try:
    #     while True:
    #         TCPsocket.sendall(message.encode())
    #         time.sleep(1)
    # except socket.error as e:
    #     print("haha")


    # time.sleep(3)


    # message = ""
    # while not message:
    #     addOn = TCPsocket.recv(1024).decode()
    #     while len(addOn) == 1024:
    #         message += addOn
    #         addOn = TCPsocket.recv(1024).decode()
    #         pass
    #     message += addOn
    #     print("message empty " + str(message))
    #     pass
    # print("finally we got message " + message)

    # TCPsocket.sendall(messageB.encode())
    # while True:
    #     try:
    #         line = input() + "\r\n"
    #         # message = line.strip() + "\r\n"
    #         message = line.encode()
    #         # length = struct.pack('>I', len(line))
    #         # TCPsocket.sendall(length)
    #         # TCPsocket.sendall(("\r\n").encode())
    #         TCPsocket.sendall(message)
    #     except EOFError:
    #         break
    #
    #     pass


    # time1 = time.time()
    # TCPsocket.close()
    # time2 = time.time()
    # TCPsocket.close()
    # time3 = time.time()
    # print("Step 1 take " + str(time2 - time1))
    # print("Step 2 take " + str(time3 - time2))


if __name__ == '__main__':
    main()

