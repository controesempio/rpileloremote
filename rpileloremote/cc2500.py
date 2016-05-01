# python class to manipulate CC2500 with a RaspberryPi

# Copyright (c) 2013 lucha@paranoici.org

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].

# RPi.GPIO requires root privileges!

import spidev
import RPi.GPIO as GPIO
from time import sleep

class CC2500(object):

    def __init__(self,bus=0,device=0, gdo0=17,gdo2=22):
        spi = spidev.SpiDev(bus,device)
        spi.mode = 0
        spi.max_speed_hz = 31250
        self.spi = spi
        self.last_status = None

        self._gdo_config = [
            [ 0x00, 0x29],      # IOCFG2      GDO2 used as CHIP_RDYn
            [ 0x02, 0x06],      # IOCFG0      GDO0 used as sync
        ]

        self.gdo0 = gdo0
        self.gdo2 = gdo2
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(gdo0, GPIO.IN)
        GPIO.setup(gdo2, GPIO.IN)

        while not self.ready():
            sleep(0.1)
        self.reset()
        while not self.ready():
            sleep(0.1)

        for [addr,value] in self._gdo_config:
            cc.reg_write(addr,value)

        self.patable_write([0xFB]*8)
        self.flushtxfifo(force=True)
        self.flushrxfifo(force=True)
        self.idle()

    def command(self, cmd):
        self.last_status = self.spi.xfer([cmd])[0]

    def reset(self):
        self.command(0x30)

    def rxmode(self):
        self.command(0x34)

    def txmode(self):
        self.command(0x35)

    def idle(self):
        self.command(0x36)

    def nop(self):
        self.command(0x3D)

    def wake_on_radio(self):
        self.command(0x38)

    def flushrxfifo(self,force=False):
        state = self.state()
        if (state == 0) or (state == 6) or force:
            self.command(0x3A)

    def flushtxfifo(self,force=False):
        state = self.state()
        if (state == 0) or (state == 7) or force:
            self.command(0x3B)

    def state(self):
        self.nop() # used to update the status byte
        return (self.last_status & 0x38) >> 4

    def fifo_available(self):
        return self.last_status & 0xF

    def ready(self):
        self.nop() # used to update the status byte
        return (self.last_status & 0x80 == 0)

    def ready2(self):
        return GPIO.input(self.gdo2) == GPIO.LOW

    def status(self):
        """Return a human-readable version of the status byte."""
        _statestr = [ "IDLE", "RX", "TX", "FSTXON", "CALIBRATE", "SETTLING", "RXFIFO_OVERFLOW", "TXFIFO_UNDERFLOW" ]
        state = _statestr[self.state()]
        return "State: %s - Ready: %s - FIFO available bytes: %d" % (state, self.ready(), self.fifo_available())

    def reg_read(self, addr, length=1):
        reply = []
        if (length == 1):
            # we are reading from one single register
            reply = self.spi.xfer([0x80|addr,0])
        else:
            # burst access
            reply = self.spi.xfer([0xC0|addr] + [0]*length)

        self.last_status = reply[0]
        return reply[1:]

    def reg_write(self, addr, data):
        reply = []
        if isinstance(data,int):
            # we are writing one single register
            reply = self.spi.xfer([addr,data])
        else:
            # burst access
            reply = self.spi.xfer([0x40|addr] + data)

        self.last_status = reply[-1]

    def status_read(self, addr):
        reply = self.spi.xfer([addr|0xC0,0])
        self.last_status = reply[0]
        return reply[1]

    def patable_read(self):
        return self.reg_read(0x3E,8)

    def patable_write(self, data):
        self.reg_write(0x3E, data)

    def txbytes(self):
        return self.status_read(0x3A) & 0x7F

    def rxbytes(self):
        return self.status_read(0x3B) & 0x7F

    def txfifo(self, data):
        self.reg_write(0x3F,data)

    def rxfifo(self, length=1):
        return self.reg_read(0x3F,length)

    def send_packet(self,packet):
        self.idle()
        self.flushtxfifo()
        self.txfifo(packet)
        self.txmode()

    def recv_packet(self):
        self.idle()
        self.flushrxfifo()
        self.packet = []
        GPIO.remove_event_detect(self.gdo0)
        GPIO.add_event_detect(self.gdo0,GPIO.FALLING, callback=self.recv_cb)
        self.rxmode()

    def recv_cb(self, chan):
        print(self.state())
        print(self.rxbytes())
        print(self.reg_read(0x0A))

        n = self.rxbytes()
        if (n > 0):
            self.packet = self.rxfifo(n)
            self.idle()
            self.flushrxfifo()
            GPIO.remove_event_detect(self.gdo0)

    def chip_id(self):
        return [self.status_read(0x30), self.status_read(0x31)]

    def pkstatus(self):
        return self.status_read(0x38)

    def marcstate(self):
        return self.status_read(0x35) & 0x1f

    def lqi(self):
        return self.status_read(0x33) & 0x7f

    def rssi(self):
        r = self.status_read(0x34)
        if r >= 0x80:
            return (r - 256)/2 - 71
        else:
            return r/2 - 71
