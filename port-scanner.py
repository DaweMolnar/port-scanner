""" Port scanner """
import socket
import argparse
from contextlib import closing
import multiprocessing
import threading
import sys

PORTS_TO_CHECK = 10000
THREADS_PER_CPU_CORE = 100

thread_lock = threading.Lock()
checked_ports = 0
open_ports = []


def is_port_open(ip, port):
    """ Return if given port is open on given address """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(1)
        if sock.connect_ex((ip, port)) == 0:
            return True
    return False


def update_progress(progress):
    """ Update progress """
    sys.stdout.write('\rchecked ports: {0}/{1}'.format(progress, PORTS_TO_CHECK))
    sys.stdout.flush()


def check_port_subset_thread(ip, first, last):
    """ Check if any port on given interval is open """
    global checked_ports
    for i in range(int(first), int(last + 1)):
        if is_port_open(ip, i):
            with thread_lock:
                open_ports.append(i)
        with thread_lock:
            checked_ports += 1
            update_progress(checked_ports)


def main():
    """ Main function """
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", help="Check what ports are open on given ip address")
    args = parser.parse_args()
    thread_count = multiprocessing.cpu_count() * THREADS_PER_CPU_CORE
    port_num_per_thread = PORTS_TO_CHECK / thread_count
    threads = list()
    for i in range(thread_count):
        first_port = i * port_num_per_thread + 1
        last_port = (i + 1) * port_num_per_thread
        thread = threading.Thread(target=check_port_subset_thread, args=(args.ip, first_port, last_port))
        threads.append(thread)
        thread.start()
    for index, thread in enumerate(threads):
        thread.join()
    sys.stdout.write("\n")
    for port in open_ports:
        try:
            sys.stdout.write("Open port: {} ({}) \n".format(port, socket.getservbyport(port)))
        except OSError:
            sys.stdout.write("Open port: {} \n".format(port))


if __name__ == "__main__":
    main()
