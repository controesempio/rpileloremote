# Python library for emulating the Lelo vibrator remote.
# Requires a CC2500 radio attached via SPI.

# author: lucha@paranoici.org
# original Arduino code and reverse engineering by
# Micah Elizabeth Scott <beth@scanlime.org>

import threading
from Queue import Empty
from sys import stdout

import cc2500
from json2iter import JSON2Iters
    
class LeloRemote(threading.Thread):
    def __init__(self, queue, timeout=0.01):
        threading.Thread.__init__(self)
        self.deamon = True
        self.queue = queue
        self.timeout = timeout
        self.signal = JSON2Iters('0')
        self.strength = 0
        self._radio_init()        

    def put(self, value):
        self.queue.put_nowait(value)

    @staticmethod
    def normalize(val):
        if (val < 0):
            return 0
        if (val > 128):
            return 128
        return val
        
    def run(self):
        while True:
            # let us check if we have a new signal to send
            try:
                self.signal = iter(self.queue.get(timeout=self.timeout))
                self.queue.task_done()
                print "updated!"
            except TypeError, Empty:
                pass
            # let us send the signal
            try:
                self.strength = self.normalize(self.signal.next())
                stdout.write("packet [%X]: %d \r" % (self.ident, self.strength))
                self.power(self.strength)
            except StopIteration:
                return
    
    def _radio_init(self):
        cc = cc2500.CC2500()

        config = [
            [ 0x0B, [0x0A, 0x00]] ,       # FSCTRL
            [ 0x0D, [0x5D, 0x13, 0xB1]],  # FREQ = 0x5d13b1 = 2420 MHz
            [ 0x0A, 0x01],                # CHANNR      Channel number 1
            [ 0x06, 0x09],                # PKTLEN      Using 9-byte packet
            [ 0x07, [0x0A, 0x04]],        # PKTCTRL     Addr check, broadcast, CRC autoflush,  No whitening, normal TX/RX mode, CRC on
            [ 0x09, 0x01],                # ADDR        Device address 0x01
            [ 0x17, [0x30, 0x18]]         # MCSM        TXOFF_MODE = IDLE, RXOFF_MODE = RX, CCA_MODE = RSSI unless receiving,  
                                          #             Auto calibrate, Poweron timeout
        ]
        default_config = [
            [ 0x10, [0x2D, 0x3B, 0x73, 0x22, 0xF8]],      # MDMCFG
            [ 0x15, 0x00],                                # DEVIATN    
            [ 0x19, 0x1D],                                # FOCCFG
            [ 0x1A, 0x1C],                                # BSCFG
            [ 0x1B, [0xC7, 0x00, 0xB0]],                  # AGCTRL
            [ 0x21, [0xB6, 0x10]],                        # FREND
            [ 0x23, [0xEA, 0x0A, 0x00, 0x11]],            # FSCAL
            [ 0x29, 0x59],                                # FSTEST
            [ 0x2C, [0x88,0x31,0x0B]]                     # TEST
        ]
        for [addr,value] in default_config + config:
            cc.reg_write(addr,value)
        
        cc.patable_write([0xFB]*8)
        cc.flushtxfifo(force=True)
        cc.flushrxfifo(force=True)
        cc.idle()
        self.cc = cc
        
    def power(self, strength=0x10):
        packet = [ 0x01, 0x00, 0xA5, strength, strength, 0x00, 0x00, 0x00, 0x05 ]
        self.cc.send_packet(packet)

