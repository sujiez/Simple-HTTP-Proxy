import re
import threading
import socket
import datetime
import logging


class ProxyServer:
    """
    This module let user start and hold a HTTP proxy server which proxy HTTP requests.
    User can choose to run the server on the foreground or the background.
    HTTP requests implemented in this server are GET, HEAD, POST, PUT, DELETE, OPTION,
    TRACE, PATCH, and CONNECT.
    """

    def __init__(self, port : int):
        if not isinstance(port, int):
            raise ValueError("port given need to be a integer!")
        self.port = port  # the port which current proxy server run on
        # self.host = '127.0.0.1'  # the address of current proxy server
        self.host = '0.0.0.0'
        self.address = (self.host, self.port)

        # to lock
        #   1.threadPool
        #   2.threadNumberPool
        self.doneStateLock = threading.Lock()
        # to let the main thread accept new TCP connection
        self.nextRequestCV = threading.Condition(self.doneStateLock)

        # map from serial numbers of threads to list of sockets that threads (pair of threads) own
        self.threadPool = dict()
        self.threadNumberPool = list(range(0, 20))

        # the main TCP socket to accept requests
        self.TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.TCPsocket.bind(self.address)

        self.TCPserver = None

        # log thing to stderr
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
        pass


    def startServe(self, daemon=False):
        """
        Let the user start the http proxy server. User can let the server run in the
        background or foreground.

        :param daemon: a flag in boolean to indicate whether the server should
                        run in the background or foreground.
        :return:
        """
        timeHeader = self.giveTime()
        logging.info(timeHeader + "Proxy listening on " + self.host + ":" + str(self.port))

        if not daemon:
            self.startHelper()
        else:
            self.TCPserver = threading.Thread(target=self.startHelper)
            self.TCPserver.start()
        pass


    def startHelper(self):
        """
        Accept TCP connection and make a thread to process each request

        :return:
        """
        try:
            self.TCPsocket.listen(5) # listen on given port for connection
            while True:
                (clientSocket, clientAddress) = self.TCPsocket.accept()  # accept a client

                self.nextRequestCV.acquire()  # lock the doneState and other data structures
                # currently does not have available thread for data processing
                if len(self.threadNumberPool) == 0:
                    self.nextRequestCV.wait()
                    pass
                threadPointer = self.threadNumberPool.pop(0)  # get an available thread number
                # process data
                clientRequestServer = threading.Thread(target=self.processRequest,
                                                       args=[threadPointer, clientSocket])
                self.threadPool[threadPointer] = [clientSocket]

                clientRequestServer.start()
                if self.doneStateLock.locked():
                    self.nextRequestCV.release()
                    pass
        except socket.error as e:
            # logging.info("Main socket closed")
            # logging.info("*****error in line 95 " + str(e))
            pass
        finally:
            self.TCPsocket.close()
            if self.doneStateLock.locked():
                self.nextRequestCV.release()
                pass
            pass
        pass


    def stopServe(self):
        try:
            # self.TCPsocket.close()

            self.TCPsocket.shutdown(socket.SHUT_RDWR)

            self.nextRequestCV.acquire()
            for key in self.threadPool:
                socks = self.threadPool[key]
                for sock in socks:
                    # sock.close()

                    sock.shutdown(socket.SHUT_RDWR)

                    pass
                pass
            if self.doneStateLock.locked():
                self.nextRequestCV.release()
            # logging.info("All Quit!")
        except socket.error as e:
            # print("Error is " + str(e))
            # logging.info("*****Error in line 126 " + str(e))
            pass
        '''
        TODO:
            1. need join the server thread?
        '''
        # finally:
            # logging.info("All Quit!")

        # pass


    def processRequest(self, threadPointer, clientSocket):
        """
        For processing different kind of requests. There are two major one: the first is send http request
        and get http response, the second is connect server and client to make this proxy serve as a tunnel.

        :param threadPointer: the number that represent current thread
        :param clientSocket: the sub-socket that deal with current client
        :param clientAddress: the client's address (Ip, port)
        :return:
        """
        try:
            # separators between header and data

            clientSocket.settimeout(3)
            endLine = [b'\r\n\r\n', b'\r\n\n', b'\n\n', b'\n\r\n']
            result = ""  # the whole information (convert to str from byte) get
            data = b''  # the data part of http request
            end = False  # if find separator
            while True:
                while True:
                    words = clientSocket.recv(1024)  # one chunk of information
                    for line in endLine: # if any separator in current line
                        if line in words:
                            end = True
                            parts = words.split(line)
                            result += parts[0].decode()
                            data += line.join(parts[1:])
                            break
                        pass
                    if not end:  # found no separator
                        result += words.decode()
                    else:
                        break
                    if len(words) != 1024:
                        break
                    pass
                if end:
                    break
                if not result:
                    return
                pass

            header = result.split("\n")  # for processing the header and

            logTime = self.giveTime()
            logging.info(logTime + ">>> " + header[0])

            if "CONNECT" in header[0]:
                self.establishConnect(threadPointer, clientSocket, header, data)
            else:
                self.fetchData(threadPointer, clientSocket, header, data)
                pass
            pass

        except socket.error as e:
            # logging.info("thread hold socket number " + str(threadPointer) + "quit!")
            # logging.info("Error is " + str(e))
            # logging.info("*****error in line 196 " + str(e))
            pass
        finally:
            clientSocket.close()  # !!!!!!!!!!! remember
            self.nextRequestCV.acquire()

            self.threadPool[threadPointer] = []
            self.threadNumberPool.append(threadPointer)

            self.nextRequestCV.notify()
            self.nextRequestCV.release()
        pass


    def fetchData(self, threadPointer, clientSocket, header, data):
        """
        This function process the HTTP request and fetch HTTP resonpse from web server

        :param clientSocket: The socket to communicate with client
        :param clientAddress: Client address and port
        :param header:  header information of client as a list
        :param information:  HTTP data as a list
        :return:
        """
        hostIp, port, message = self.processMessage(header, data, True)

        webServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.nextRequestCV.acquire()
        self.threadPool[threadPointer].append(webServerSocket)
        self.nextRequestCV.release()

        webServerSocket.connect((hostIp, port))
        webServerSocket.sendall(message)

        messageReceiver = threading.Thread(target=self.openTunnel,
                                           args=[threadPointer, webServerSocket, clientSocket])
        messageReceiver.start()
        try:
            # while True:
            #     clientMessage = b''
            #     while True:
            #         addOn = clientSocket.recv(1024)
            #         clientMessage += addOn
            #         if len(addOn) != 1024:
            #             break
            #         pass
            #
            #     if not clientMessage:
            #         # logging.info("Done with receiving!")
            #         break
            #     webServerSocket.sendall(clientMessage)
            while True:
                quitFromRead = False
                while True:
                    clientMessage = clientSocket.recv(490)
                    if len(clientMessage) == 0:
                        quitFromRead = True
                        break
                    webServerSocket.sendall(clientMessage)
                    if len(clientMessage) != 490:
                        break
                    pass
                if quitFromRead:
                    break
                pass
        except socket.error as e:
            # logging.info("client message quit in fetch data with number " + str(threadPointer))
            # logging.info("error is : " + str(e))
            # logging.info("*****error in line 356 " + str(e))
            pass
        finally:

            # webServerSocket.close()
            # clientSocket.close()
            try:
                webServerSocket.shutdown(socket.SHUT_RDWR)
                clientSocket.shutdown(socket.SHUT_RDWR)
            except:
                pass
        pass


    def establishConnect(self, threadPointer, clientSocket, header, data):
        hostIp, port, message = self.processMessage(header, data, False) # get the ip and port

        webServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # connect to the web server
        try:
            webServerSocket.connect((hostIp, port)) # connect
        except socket.error as e:
            errorMessage = b"HTTP/1.1 502 Bad Gateway\r\n\r\n"
            clientSocket.sendall(errorMessage)
            return

        self.nextRequestCV.acquire()
        self.threadPool[threadPointer].append(webServerSocket)
        self.nextRequestCV.release()

        okMessage = b"HTTP/1.1 200 OK\r\n\r\n" # hahaha
        clientSocket.sendall(okMessage) # send ok message

        courier = threading.Thread(target=self.openTunnel, args=[threadPointer, webServerSocket, clientSocket])
        courier.start()

        try:
            # while True:
            #     clientMessage = b''
            #     while True:
            #         addOn = clientSocket.recv(1024)
            #         clientMessage += addOn
            #         if len(addOn) != 1024:
            #             break
            #         pass
            #
            #     if not clientMessage:
            #         break
            #     webServerSocket.sendall(clientMessage)
            while True:
                quitFromRead = False
                while True:
                    clientMessage = clientSocket.recv(490)
                    if len(clientMessage) == 0:
                        quitFromRead = True
                        break
                    webServerSocket.sendall(clientMessage)
                    if len(clientMessage) != 490:
                        break
                    pass
                if quitFromRead:
                    break
                pass

        except socket.error as e:
            pass
        finally:
            if self.doneStateLock.locked():
                self.nextRequestCV.release()
                pass

            # webServerSocket.close()
            # clientSocket.close()
            try:
                webServerSocket.shutdown(socket.SHUT_RDWR)
                clientSocket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            courier.join()
            pass
        pass



    def openTunnel(self, threadPointer, webServerSocket, clientSocket):
        """

        :param webServerSocket:
        :param isDone:
        :param checkDone:
        :return:
        """
        # file_target = open("server_output.txt", "a")
        try:
            webServerSocket.settimeout(3)
            while True:
                # print("In openTunnel 3")
                serverMessage = b''

                while True:
                    addOn = webServerSocket.recv(1024)
                    serverMessage += addOn
                    if len(addOn) != 1024:
                        break
                    pass

                if not serverMessage:
                    # print("Done with server -> client!") # 5
                    break
                clientSocket.sendall(serverMessage)
        except socket.error as e:

            pass
        finally:

            # webServerSocket.close()
            # clientSocket.close()
            try:
                webServerSocket.shutdown(socket.SHUT_RDWR)
                clientSocket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            # print("I am out in open tunnel 1")
            pass
        pass


    def processMessage(self, headerMessages, data, changeFlag):
        """
        This function is used to modify the HTTP header (block persistent connection) and
        fetch web server IP and port. Finally reform the HTTP request message

        :param headerMessages: the header information as a list
        :param information: the data as a list
        :return: (hostAddress, port, result)
                 hostAddress: the ip of web server
                 port: the port number of web server
                 result: the request information after modification
        """
        result = ""  # the final result
        # the first one represent host ip in string, the second one represent port in int
        hostAddress = [None, None]
        # the method line and host line of the http header
        firstAndSecond = []
        for term in headerMessages:  # loop through each line in header
            term = term.strip()  # now all header are without "\r"
            if "GET" in term or "HEAD" in term or "POST" in term or \
               "PUT" in term or "DELETE" in term or "OPTION" in term or \
               "TRACE" in term or "PATCH" in term or "CONNECT" in term:  # mean it is the first line
                if changeFlag and term[-3:] == "1.1":  # modify the communication version
                    term = term[:-3] + "1.0"
                    pass
                self.grabHostAddress(hostAddress, term)
                firstAndSecond.append(term)
            elif re.search("host", term, re.IGNORECASE):  # this line is host line
                self.grabHostAddress(hostAddress, term)
                firstAndSecond.append(term)
            elif changeFlag and re.search("Connection", term, re.IGNORECASE):  # current line is connect method line
                term = "Connection: close"
            elif changeFlag and re.search("Proxy-connection", term, re.IGNORECASE):
                term = "Proxy-connection: close"
                pass
            result += term + "\r\n"
            pass
        # if the port is still not found,  must be identified by the header
        for term in firstAndSecond:
            if not hostAddress[1]:
                if re.search("http://", term, re.IGNORECASE):
                    hostAddress[1] = 80
                elif re.search("https://", term, re.IGNORECASE):
                    hostAddress[1] = 443
                    pass
                pass
            pass

        result += "\r\n"
        # result = result[:-2]
        result = result.encode() + data
        return (hostAddress[0], hostAddress[1], result)


    def grabHostAddress(self, hostAddress, term):
        """
        This method grab the ip address and port of web server and stored in the given array

        :param hostAddress: the given array to store the ip and port [ip, port]
        :param term: one line to grab the address information
        :return:
        """
        urlPatternA = "([a-zA-Z0-9]+|([a-zA-Z0-9][a-zA-Z0-9|-]+[a-zA-Z0-9]))"
        urlPatternB = "(\.([a-zA-Z0-9]+|([a-zA-Z0-9][a-zA-Z0-9|-]+[a-zA-Z0-9]))){1,}"
        urlPatternD = "[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}"
        urlPatternC = ":[0-9]{2,5}"
        url = re.search(urlPatternA + urlPatternB, term)  # if there is url like portion
        ipv4 = re.search(urlPatternD, term) # if there is ip like string
        if url:  # find url like part
            # print("url found is " + str(url))
            if not hostAddress[0]:  # the ip is not currently stored
                urlStrip = url.group(0)
                # print("\n%%%%% striped url is " + urlStrip + "\n")
                hostAddress[0] = socket.gethostbyname_ex(urlStrip)[-1][0]   # store the ip
            if not hostAddress[1]:  # the port is not stored
                urlAndPort = re.search(urlPatternA + urlPatternB + urlPatternC, term)
                if urlAndPort:  # if such url is post append with port
                    hostAddress[1] = int(urlAndPort.group(0).split(":")[-1])
                    pass
                pass
        elif ipv4:  # find ip like string
            if not hostAddress[0]:  # the ip is not found so far
                hostAddress[0] = ipv4.group(0)  # store the ip
            if not hostAddress[1]:  # port is not found so far
                # to see if the ip is post append with port
                ipv4AndPort = re.search(urlPatternD + urlPatternC, term)
                if ipv4AndPort:  # store the port number
                    hostAddress[1] = int(ipv4AndPort.group(0).split(":")[-1])
                    pass
                pass
            pass
        pass



    def giveTime(self):
        currentTime = datetime.datetime.now()
        result = str(currentTime.day) + " " + str(currentTime.month) + " " + \
                 str(currentTime.hour) + ":" + str(currentTime.minute) + ":" + \
                 str(currentTime.second) + " - "
        return result
