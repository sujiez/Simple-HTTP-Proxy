import threading
import time
import re
import socket
import logging
import sys


def test():
    logging.info('hahahahaha')


def main():
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    logging.info('This is info message')
    tester = threading.Thread(target=test)
    tester.start()





if __name__ == "__main__":
    main()