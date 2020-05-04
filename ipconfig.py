#!/usr/bin/env python3

from __future__ import print_function
from threading import Timer
import socket
import os
import sys
import psutil
from psutil._common import bytes2human


af_map = {
    socket.AF_INET: 'IPv4',
    socket.AF_INET6: 'IPv6',
    psutil.AF_LINK: 'MAC',
}

duplex_map = {
    psutil.NIC_DUPLEX_FULL: "full",
    psutil.NIC_DUPLEX_HALF: "half",
    psutil.NIC_DUPLEX_UNKNOWN: "?",
}

def setInterval(timer, task):
    isStop = task()
    if not isStop:
        Timer(timer, setInterval, [timer, task]).start()

def main():
    stats = psutil.net_if_stats()
    io_counters = psutil.net_io_counters(pernic=True)
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    logger = os.path.join(script_dir, 'logger.txt')
    
    for nic, addrs in psutil.net_if_addrs().items():
        print("%s:" % (nic))
        f = open(logger, "a")
        f.write("____ %s: ____\n" % (nic))
        f.close()
        if nic in stats:
            st = stats[nic]
            print("    stats          : ", end='')
            print("speed=%sMB, duplex=%s, mtu=%s, up=%s" % (
                st.speed, duplex_map[st.duplex], st.mtu,
                "yes" if st.isup else "no"))
        if nic in io_counters:
            io = io_counters[nic]
            print("    incoming       : ", end='')
            print("bytes=%s, pkts=%s, errs=%s, drops=%s" % (
                bytes2human(io.bytes_recv), io.packets_recv, io.errin,
                io.dropin))
            f = open(logger, "a")
            f.write("incoming: \n")
            f.write("bytes=%s, pkts=%s, errs=%s, drops=%s \n"  % (
                bytes2human(io.bytes_recv), io.packets_recv, io.errin,
                io.dropin))
            
            print("    outgoing       : ", end='')
            print("bytes=%s, pkts=%s, errs=%s, drops=%s" % (
                bytes2human(io.bytes_sent), io.packets_sent, io.errout,
                io.dropout))
            f.write("outgoing: \n")
            f.write("bytes=%s, pkts=%s, errs=%s, drops=%s \n \n \n" % (
                bytes2human(io.bytes_sent), io.packets_sent, io.errout,
                io.dropout))
            f.close()
        for addr in addrs:
            print("    %-4s" % af_map.get(addr.family, addr.family), end="")
            print(" address   : %s" % addr.address)
            if addr.broadcast:
                print("         broadcast : %s" % addr.broadcast)
            if addr.netmask:
                print("         netmask   : %s" % addr.netmask)
            if addr.ptp:
                print("      p2p       : %s" % addr.ptp)
        print("")
        
if __name__ == '__main__':
    setInterval(2.0, main)