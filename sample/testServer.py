import re
import socket
import threading


HOST = 'localhost'
PORT = 46102


def changeData(webSocket, clientSocket, starter):
    # webSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # try:
    #     webSocket.connect((serverHost, serverPort))
    # except ConnectionRefusedError as e:
    #     print("^^^^^^^^^^connection refused")
    webSocket.sendall(starter)
    while True:
        try:
            responseMessage = b''
            addOn = webSocket.recv(1024)
            while len(addOn) == 1024:
                responseMessage += addOn
                addOn = webSocket.recv(1024)
                pass

            if addOn:
                responseMessage += addOn
                pass
            else:
                print("Done with receiving from server!")
                break
            print("data got from server ")
            print(responseMessage.decode())
            clientSocket.sendall(responseMessage)
        except socket.error as exc:
            print("Caught web server : %s" % exc)
            pass



def runTest(sock, addr):
    message = b''
    addOn = sock.recv(1024)
    while len(addOn) == 1024:
        message += addOn
        addOn = sock.recv(1024)
        pass
    message += addOn
    # print("Got information in bytes:")
    # print(str(message))
    # print("\n")
    # print("Got information in string:")
    # print(message.decode())
    # print("\n\n")
    # sock.close()
    serverHost, serverPort, info = processData(message.decode())
    print("get server host: " + str(serverHost))
    print("get server Port: " + str(serverPort))
    webSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        webSocket.connect((serverHost, serverPort))
    except ConnectionRefusedError as e:
        print("^^^^^^^^^^connection refused")
        pass


    connector = threading.Thread(target=changeData,
                                 args=[webSocket, sock, message])
    connector.start()
    # webSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # webSocket.connect((serverHost, serverPort))
    # webSocket.sendall(info.encode())

    while True:
        try:
            responseMessage = b''
            addOn = sock.recv(1024)
            while len(addOn) == 1024:
                responseMessage += addOn
                addOn = sock.recv(1024)
                pass

            if addOn:
                responseMessage += addOn
                pass
            else:
                print("Done with receiving from client!")
                break
            print("data got from client ")
            print(responseMessage.decode())
            webSocket.sendall(responseMessage)
        except socket.error as exc:
            print("Caught web server : %s" % exc)
            pass
    # result = b''
    # while not result:
    #     addOn = webSocket.recv(1024)
    #     while len(addOn) == 1024:
    #         result += addOn
    #         addOn = webSocket.recv(1024)
    #         pass
    #     result += addOn
    #     # print("result is " + result.decode())
    #     # print("result length is " + str(len(result)))
    # print("\n\n")
    # print("Got server information in bytes: " + str(result))
    # print("\n")
    # print("Got server information in string: " + result.decode())
    # sock.close()
    # webSocket.close()
    pass

def processData(message):
    # print("************message is ")
    # print(str(message))
    # print("*********message type is ")
    # print(type(message))
    result = ""
    message = message.split("\n")
    if "" not in message:  # check whether "" or "\r" is separator
        separator = message.index("\r")
    elif "\r" not in message:
        separator = message.index("")
    elif message.index("") > message.index("\r"):
        separator = message.index("\r")
    else:
        separator = message.index("")
        pass
    header = message[:separator]
    information = message[separator:]
    hostAddress = [None, None]
    firstAndSecond = []
    for term in header:
        term = term.strip()
        if "GET" in term or "HEAD" in term or "POST" in term or \
                        "PUT" in term or "DELETE" in term or "OPTION" in term or \
                        "TRACE" in term or "PATCH" in term or "CONNECT" in term:  # mean it is the first line
            grabAddress(hostAddress, term, 1)
            firstAndSecond.append(term)
            # term = re.sub("CONNECT", "GET", term, re.IGNORECASE)
        elif re.search("host", term, re.IGNORECASE):
            grabAddress(hostAddress, term, 2)
            firstAndSecond.append(term)
            pass
        result += term + "\r\n"
        pass
    for term in firstAndSecond:
        if not hostAddress[1]:
            if re.search("http://", term, re.IGNORECASE):
                hostAddress[1] = 80
            elif re.search("https://", term, re.IGNORECASE):
                hostAddress[1] = 443
                pass
            pass
        pass
    for info in information:
        result += info + "\r\n"
        pass
    result = result[-1]
    return (hostAddress[0], hostAddress[1], result)
    pass


def grabAddress(hostAddress, term, case):
    urlPatternA = "([a-zA-Z0-9]+|([a-zA-Z0-9][a-zA-Z0-9|-]+[a-zA-Z0-9]))"
    urlPatternB = "(\.([a-zA-Z0-9]+|([a-zA-Z0-9][a-zA-Z0-9|-]+[a-zA-Z0-9]))){1,}"
    urlPatternC = ":[0-9]{2,5}"
    url = re.search(urlPatternA + urlPatternB, term)  # if there is url like portion
    ipv4 = re.search("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}", term)  # if there is ip like string
    if url:  # find url like part
        if not hostAddress[0]:  # the ip is not currently stored

            urlStrip = url[0]
            # print("*****url strip1 is " + urlStrip)
            hostAddress[0] = socket.gethostbyname_ex(urlStrip)[-1][0]  # store the ip
        if not hostAddress[1]:  # the port is not stored
            urlAndPort = re.search(urlPatternA + urlPatternB + urlPatternC, term)
            if urlAndPort:  # if such url is post append with port
                # print("*****url and port is " + str(urlAndPort[0]))
                hostAddress[1] = int(urlAndPort[0].split(":")[-1])
                # print("******got host port " + str(hostAddress[1]))
                pass
            pass
    elif ipv4:  # find ip like string
        if not hostAddress[0]:  # the ip is not found so far
            hostAddress[0] = ipv4[0]  # store the ip
            # print("*****Got ipv4 " + str(ipv4[0]))
        if not hostAddress[1]:  # port is not found so far
            # to see if the ip is post append with port
            ipv4AndPort = re.search("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{2,5}", term)
            if ipv4AndPort:  # store the port number

                hostAddress[1] = int(ipv4AndPort[0].split(":")[-1])
                # print("*****got port " + str(hostAddress[1]))
                pass
            pass
        pass
    pass


def main():
    TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TCPsocket.bind((HOST, PORT))
    TCPsocket.listen()
    while True:
        (sock, addr) = TCPsocket.accept()
        tester = threading.Thread(target=runTest, args=[sock, addr])
        tester.start()
        pass
    # runTest(sock, addr)

if __name__ == '__main__':
    main()
