# coding=utf-8
import logging
from blueman.Functions import open_rfcomm
import tty
import termios
import os
import subprocess
from gi.repository import GObject
from gi.repository import GLib
import errno
import re

pppd_errors = {
    1: "An immediately fatal error of some kind  occurred, such as an essential system call failing, "
       "or running out of virtual memory.",
    2: "An  error  was detected in processing the options given, such as two mutually exclusive options being used.",
    3: "Pppd is not setuid-root and the invoking user is not root.",
    4: "The kernel does not support PPP, for example, the  PPP kernel driver is not included or cannot be loaded.",
    5: "Pppd terminated because it was sent a SIGINT, SIGTERM or SIGHUP signal.",
    6: "The serial port could not be locked.",
    7: "The serial port could not be opened.",
    8: "The connect script failed (returned a non-zero exit status).",
    9: "The command specified as the argument to the  pty  option  could not be run.",
    10: "The PPP negotiation failed, that is, it didn't reach the point where at least one network protocol "
        "(e.g. IP) was running.",
    11: "The peer system failed (or refused) to authenticate itself.",
    12: "The link was established successfully and terminated because  it was idle.",
    13: "The link was established successfully and terminated because the connect time limit was reached.",
    14: "Callback was negotiated  and  an  incoming  call  should  arrive shortly.",
    15: "The link was terminated because the peer is not responding to echo requests.",
    16: "The link was terminated by the modem hanging up.",
    17: "The PPP negotiation failed because serial loopback was detected.",
    18: "The init script failed (returned a non-zero exit status).",
    19: "We failed to authenticate ourselves to the peer."
}


class PPPException(Exception):
    pass


class PPPConnection(GObject.GObject):
    __gsignals__ = {  # arg: interface name eg. ppp0
        'connected': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        'error-occurred': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,))
    }

    def __init__(self, port, number="*99#", apn="", user="", pwd=""):
        super().__init__()

        self.apn = apn
        self.number = number
        self.user = user
        self.pwd = pwd
        self.port = port
        self.interface = None

        self.pppd = None
        self.file = None

        self.commands = [
            ("ATZ E0 V1 X4 &C1 +FCLASS=0", self.simple_callback),
            ("ATE0", self.simple_callback),
            ("AT+GCAP", self.simple_callback),
            (
                "ATD%s" % self.number,
                self.connect_callback,
                ["CONNECT", "NO CARRIER", "BUSY", "NO ANSWER", "NO DIALTONE", "OK", "ERROR"]
            )
        ]
        if self.apn != "":
            self.commands.insert(-1, ('AT+CGDCONT=1,"IP","%s"' % self.apn, self.simple_callback))

    def cleanup(self):
        os.close(self.file)
        self.file = None

    def simple_callback(self, response):
        pass

    def connect_callback(self, response):
        if "CONNECT" in response:
            logging.info("Starting pppd")
            self.pppd = subprocess.Popen(
                ["/usr/sbin/pppd", "%s" % self.port, "115200", "defaultroute", "updetach", "usepeerdns"], bufsize=1,
                stdout=subprocess.PIPE)
            GLib.io_add_watch(self.pppd.stdout, GLib.IO_IN | GLib.IO_ERR | GLib.IO_HUP, self.on_pppd_stdout)
            GLib.timeout_add(1000, self.check_pppd)

            self.cleanup()
        else:
            self.cleanup()
            raise PPPException("Bad modem response %s, expected CONNECT" % response[0])

    def __cmd_response_cb(self, response, exception, item_id):
        if exception:
            self.emit("error-occurred", str(exception))
        else:
            try:
                self.commands[item_id][1](response)
            except PPPException as e:
                self.emit("error-occurred", str(e))
                return

            self.send_commands(item_id + 1)

    def send_commands(self, i=0):
        try:
            item = self.commands[i]
        except IndexError:
            return

        if len(item) == 3:
            (command, callback, terminators) = item
        else:
            (command, callback) = item
            terminators = ["OK", "ERROR"]

        self.send_command(command)
        self.wait_for_reply(self.__cmd_response_cb, terminators, i)

    def connect_rfcomm(self):

        self.file = open_rfcomm(self.port, os.O_RDWR)

        tty.setraw(self.file)

        attrs = termios.tcgetattr(self.file)

        attrs[0] &= ~(termios.IGNCR | termios.ICRNL | termios.IUCLC | termios.INPCK | termios.IXON | termios.IXANY |
                      termios.IGNPAR)
        attrs[1] &= ~(termios.OPOST | termios.OLCUC | termios.OCRNL | termios.ONLCR | termios.ONLRET)
        attrs[3] &= ~(termios.ICANON | getattr(termios, 'XCASE', 4) | termios.ECHO | termios.ECHOE | termios.ECHONL)
        attrs[3] &= ~(termios.ECHO | termios.ECHOE)
        attrs[6][termios.VMIN] = 1
        attrs[6][termios.VTIME] = 0
        attrs[6][termios.VEOF] = 1

        attrs[2] &= ~(termios.CBAUD | termios.CSIZE | termios.CSTOPB | termios.CLOCAL | termios.PARENB)
        attrs[2] |= (termios.B9600 | termios.CS8 | termios.CREAD | termios.PARENB)

        termios.tcsetattr(self.file, termios.TCSANOW, attrs)

        termios.tcflush(self.file, termios.TCIOFLUSH)

        self.send_commands()

    def on_pppd_stdout(self, source, cond):
        if cond & GLib.IO_ERR or cond & GLib.IO_HUP:
            return False

        line = source.readline().decode('utf-8')
        m = re.match(r'Using interface (ppp[0-9]*)', line)
        if m:
            self.interface = m.groups(1)[0]

        logging.info(line)

        return True

    def check_pppd(self):
        status = self.pppd.poll()
        if status is not None:
            if status == 0:
                self.emit("connected", self.interface)
            else:
                try:
                    msg = "pppd exited: " + pppd_errors[int(status)]
                except KeyError:
                    msg = "pppd exited with unknown error"

                self.emit("error-occurred", msg)

            logging.warning("pppd exited with status %d" % status)
            return False
        return True

    def send_command(self, command):
        logging.info("--> %s" % command)
        out = "%s\r\n" % command
        os.write(self.file, out.encode("UTF-8"))
        termios.tcdrain(self.file)

    def on_data_ready(self, source, condition, terminators, on_done):
        if condition & GLib.IO_ERR or condition & GLib.IO_HUP:
            on_done(None, PPPException("Socket error"))
            self.cleanup()
            return False
        try:
            self.buffer += os.read(self.file, 1).decode('utf-8')
        except OSError as e:
            if e.errno == errno.EAGAIN:
                logging.error("Got EAGAIN")
                return True
            else:
                on_done(None, PPPException("Socket error"))
                logging.exception(e)
                self.cleanup()
                return False

        lines = self.buffer.split("\r\n")
        found = False
        for line in lines:
            if line == "":
                pass
            else:
                for t in terminators:
                    if t in line:
                        found = True

        if found:
            lines = filter(lambda x: x != "", lines)
            lines = [x.strip("\r\n") for x in lines]
            logging.info("<-- %s" % lines)

            on_done(lines, None)
            return False

        return True

    def wait_for_reply(self, callback, terminators=("OK", "ERROR"), *user_data):
        def on_timeout():
            GLib.source_remove(self.io_watch)
            callback(None, PPPException("Modem initialization timed out"), *user_data)
            self.cleanup()
            return False

        def on_done(ret, exception):
            GLib.source_remove(self.timeout)
            callback(ret, exception, *user_data)

        self.buffer = ""
        self.term_found = False

        self.io_watch = GLib.io_add_watch(self.file, GLib.IO_IN | GLib.IO_ERR | GLib.IO_HUP, self.on_data_ready,
                                          terminators, on_done)
        self.timeout = GLib.timeout_add(15000, on_timeout)
