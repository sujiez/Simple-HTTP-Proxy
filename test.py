#!/usr/bin/env python3

import sys
from testHTTPProxy import ProxyServer


def print_usage():
    print("To run this program, type:")
    print("./run portNumber")
    print("This program run a http proxy server")


def main():
    if len(sys.argv) != 2:
        print_usage()
        pass
    proxyServer = ProxyServer(int(sys.argv[1]))
    while True:
        try:
            line = input()
            if line == 's':
                proxyServer.startServe(True)
            elif line == 'q':
                proxyServer.stopServe()
                break
        except EOFError:
            proxyServer.stopServe()
            break
        pass
    pass


if __name__ == '__main__':
    main()