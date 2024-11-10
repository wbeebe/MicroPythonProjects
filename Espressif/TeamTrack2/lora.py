"""
 This is the class for LoRa functionality, from the simplest to the most complex.
 Instantiate this class and then call its methods based on the comments below.

 Note: Instantiating the class turns on the LoRa radio.
"""

from network import LoRa
from machine import RTC
import socket
import machine
import time
import binascii
import struct
import messages as msgs
import config
import re
import _thread

class LoRaTTrk:
    SSID = None
    LOG = None
    get_alarm = None
    set_alarm = None
    get_battery_percentage_value = None
    get_coords = None
    lora = None
    macaddr = None
    lora_socket = None
    group_members = None
    mesh_members = None
    rtc = None
    lora_rec_stats = None
    bandwidth = 0
    power_mode = None
    coding_rate = None
    preamble = 0
    regex = None

    # ------------------------------------------------------------------------
    """
    Turn on the LoRa radio.
    Note that the region is hard-coded for US915.
    If you attempt to set the region when reflashing a new version of the
    firmware using Pycom Firmware Update, whatever you define directly on the
    FiPy will be ignored.
    """
    def __init__(self, data, logging_function,
        get_alarm_func, set_alarm_func, get_battery_percentage_value_func,
        get_coords_func):

        self.rtc = RTC()
        self.SSID = data
        self.LOG = logging_function
        self.get_alarm = get_alarm_func
        self.set_alarm = set_alarm_func
        self.get_battery_percentage_value = get_battery_percentage_value_func
        self.get_coords = get_coords_func
        self.group_members = dict()
        self.group_members_lock = _thread.allocate_lock()
        self.mesh_members = dict()
        #
        # Set up to filter for proper nodes in our network. If they're not
        # proper we reject them and log them as rejected.
        #
        self.regex = re.compile(config.ID_BASENAME + config.REG_STR)
        #
        # Enable the LoRa radio and set up for asynchronous message reception.
        #
        self.bandwidth = LoRa.BW_125KHZ
        self.power_mode = LoRa.ALWAYS_ON
        self.lora = LoRa(mode=LoRa.LORA, region=LoRa.US915, bandwidth=self.bandwidth, power_mode=self.power_mode, sf=7, public=False)
        self.coding_rate = self.lora.coding_rate()
        self.preamble = self.lora.preamble()
        self.lora_rec_stats = self.lora.stats()
        self.macaddr = binascii.hexlify(self.lora.mac()).decode('ascii')
        self.lora_socket = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        self.lora_socket.setblocking(False)
        self.lora.callback(trigger=(LoRa.RX_PACKET_EVENT), handler=self.receive_lora_message_callback)
        self.send_lock = _thread.allocate_lock()

    # ------------------------------------------------------------------------
    # Basic utilities.
    #
    # Look in the timeouts dictionary to see all the nodes that this node is a
    # part of. This means that if any nodes are out-of-comms, they won't be
    # in the list. Add this node's name so that the list has at least one member.
    #
    def list_group_nodes(self):
        nodes = [k for k,v in self.group_members.items() if v > 0]
        nodes.append(self.SSID)
        nodes.sort()
        return 'Nodes,{}'.format(','.join(nodes))

    def count_group_nodes(self):
        return len(self.group_members)

    def clear_all_group_nodes(self):
        self.group_members.clear()

    def list_oocom(self):
        with self.group_members_lock:
            nodes = [k for k,v in self.group_members.items() if v <= 0]
        if len(nodes) > 0:
            nodes.sort()
        return nodes
    #
    # Return a common who-am-I query. Can be used anywhere.
    #
    def who_am_i(self):
        text = 'WhoAmI,{},{}'.format(self.SSID, config.VERSION)
        return text

    # ------------------------------------------------------------------------
    """
    Receive all LoRa messages on this callback. Every message is checked as to
    its type and handled accordingly. For heart beat messages, keep a dictionary
    of them for later processing and determining if they've fallen out of
    comms in relation to this node.

    BEST PRACTICES DISCOVERED HERE:
    1. Never set socket blocking True, only False.
    2. Use 256 bytes at a minimum when receiving data.
    """
    def receive_lora_message_callback(self, lora_obj):
        events = lora_obj.events()
        if events & LoRa.RX_PACKET_EVENT:
            received_data = self.lora_socket.recv(512)
            self.lora_rec_stats = self.lora.stats()
            if len(received_data) > 0:
                self.decode_message(received_data)
            else:
                self.LOG('LORA_RECV_ERROR: NO DATA RECEIVED')

    # ------------------------------------------------------------------------
    # Decode all incoming messages here.
    #
    def decode_message(self, data):
        message_type = chr(data[0])
        #
        # There's a huge try/except wrap around this code so that if anything
        # happens, it's caught and logged. The exceptions can get a bit cryptic,
        # but at least the entire decoder doesn't just stop working because of
        # an issue in one spot.
        #
        try:
            if data[0] == msgs.THIRD_PARTY:
                self.LOG('ThirdParty,{}'.format(data[5:].decode('ascii').strip()))

            elif message_type == msgs.HEARTBEAT:
                msg_type, nod, alarm, pwr, rssi = struct.unpack('s8sbbb', data)
                node = nod.decode('ascii')
                if self.regex.match(node) != None:
                    with self.group_members_lock:
                        self.group_members.update({node : config.GROUP_COUNTDOWN})
                    self.LOG('Heartbeat,{},{},{},{}'.format(
                        node, config.decode_alarm_state(alarm), pwr, rssi), True)
                else:
                    self.LOG('BOGUS_HEARTBEAT: ' + node)

            elif message_type == msgs.HEARTBEAT_LOC:
                msg_type, nod, alarm, pwr, rssi, lat, lon, tim = struct.unpack('s8sbbbffI', data)
                node = nod.decode('ascii')
                tip = time.localtime(tim)
                loc_ts = "{},{},{}/{:02}/{:02}-{:02}:{:02}:{:02}_UTC".format(
                    lat, lon, tip[0], tip[1], tip[2], tip[3], tip[4], tip[5])

                if self.regex.match(node) != None and node != self.SSID:
                    with self.group_members_lock:
                        if node in self.group_members:
                            if self.group_members[node] <= 0:
                                self.LOG('InComms,{},{}'.format(node, self.group_members[node]))
                                self.send_in_comm_msg(node)
                                #self.LOG('InComms,' + node)
                        self.group_members.update({node : config.GROUP_COUNTDOWN})
                        self.LOG('Heartbeat,{},{},{},{},{}'.format(
                            node,
                            config.decode_alarm_state(alarm), pwr, rssi,
                            loc_ts), True)
                    #
                    # If we're routing a message, all we need to do is just
                    # change the message type byte, not reconstruct the message.
                    #
                    if node in self.mesh_members:
                        time.sleep(0.5)
                        self.route_message(msgs.HEARTBEAT_LOC_MESH, data)
                        self.LOG('SendMeshHeartBeat,{},{},{},{},{}'.format(
                            node,
                            config.decode_alarm_state(alarm), pwr, rssi,
                            loc_ts), True)
                else:
                    self.LOG('BOGUS_HEARTBEAT_LOC: ' + node)

            elif message_type == msgs.OUT_OF_COMM:
                msg_type, nod, sndr = struct.unpack('s8s8s', data)
                node = nod.decode('ascii')
                sender = sndr.decode('ascii')
                self.mesh_members.update({ node : 1 })
                self.LOG(('RemoteOutOfComm,' + node + ',' + sender), True)

            elif message_type == msgs.IN_COMM:
                msg_type, nod, sndr = struct.unpack('s8s8s', data)
                node = nod.decode('ascii')
                sender = sndr.decode('ascii')
                if node in self.mesh_members:
                    del self.mesh_members[node]
                self.LOG(('RemoteInComm,' + node + ',' + sender), True)

            elif message_type == msgs.HEARTBEAT_LOC_MESH:
                msg_type, nod, alarm, pwr, rssi, lat, lon, tim = struct.unpack('s8sbbbffI', data)
                node = nod.decode('ascii')
                if node != self.SSID:
                    logToDashboard = False
                    tip = time.localtime(tim)
                    loc_ts = "{},{},{}/{:02}/{:02}-{:02}:{:02}:{:02}_UTC".format(
                        lat, lon, tip[0], tip[1], tip[2], tip[3], tip[4], tip[5])
                    #
                    # MESH
                    #
                    if node in self.group_members:
                        msg_type = 'Heartbeat'
                        if self.group_members[node] <= 0:
                            msg_type = 'MeshHeartbeat'
                            logToDashboard = True
                        self.LOG('{},{},{},{},{},{}'.format(
                        msg_type,
                        node,
                        config.decode_alarm_state(alarm), pwr, rssi,
                        loc_ts), logToDashboard)

            elif message_type == msgs.ALARM:
                msg_type, nod = struct.unpack('s8s', data)
                node = nod.decode('ascii')
                self.LOG('Alarm,Received,{}'.format(node), True)

            elif message_type == msgs.CONFIRM_ALARM:
                msg_type, nod, tgt = struct.unpack('s8s8s', data)
                sender = nod.decode('ascii')
                target = tgt.decode('ascii')
                if sender == target:
                    self.LOG('ConfirmAlarm', True)
                elif target == self.SSID:
                    if self.get_alarm() == config.ALARM:
                        self.LOG('ConfirmAlarm,{}'.format(target), True)
                        self.set_alarm(config.CONFIRM_ALARM)
                    else:
                        self.LOG('ConfirmAlarm,Unknown', True)

            elif message_type == msgs.CLEAR_ALARM:
                msg_type, nod, tgt = struct.unpack('s8s8s', data)
                sender = nod.decode('ascii')
                target = tgt.decode('ascii')
                my_alarm = self.get_alarm()
                if sender == target:
                    self.LOG('ClearAlarm,SenderIsTargetBlocked', True)
                elif target == self.SSID:
                    if my_alarm == config.ALARM or my_alarm == config.CONFIRM_ALARM:
                        self.LOG('ClearAlarm,{}'.format(target))
                        self.set_alarm(config.CLEAR_ALARM)
                    else:
                        self.LOG('ClearAlarm,TargetNotInAlarm', True)

            elif message_type == msgs.RESET_ALL:
                msg_type, nod = struct.unpack('s8s', data)
                node = nod.decode('ascii')
                self.LOG('ResetAll', True)
                self.set_alarm(config.NO_ALARM)

            else:
                #self.LOG('LORA_RECV: UNKNOWN TYPE {}'.format(binascii.hexlify(message_type).decode('ascii')))
                self.LOG('LORA_RECV: UNKNOWN TYPE {} - LEN: {} - DATA: {}'.format(
                    binascii.hexlify(message_type).decode('ascii'),
                    len(data),
                    binascii.hexlify(data).decode('ascii')))

        except Exception as exc:
            self.LOG('LORA_RECV: EXCEPTION: LEN: {} - DATA: {}'.format(len(data), data))
            self.LOG('LORA_RECV: EXCEPTION: {}'.format(exc))

    # ------------------------------------------------------------------------
    """
    LoRa send heartbeat data. This function sends out the
    heartbeat message to all listeners in a given group.
    It also checks if any group members it knows of are no longer sending out
    a message, or "out of comms".

    This function should ONLY be called on a thread.
    """
    def send_lora_heartbeat(self, get_coords):
        self.LOG('LORA_SEND: SEND_LORA_HEARTBEAT: START')

        while True:
            #
            # Determine if we send a heartbeat message with or without
            # location data.
            #
            coords = get_coords()

            if coords[0] == None:
                message = struct.pack('s8sbbbI',
                    msgs.HEARTBEAT[0],
                    bytes(self.SSID, 'ascii'),
                    self.get_alarm(),
                    self.get_battery_percentage_value(),
                    self.lora_rec_stats.rssi)
                self.LOG("Heartbeat,{},{},{},{}".format(
                    self.SSID,
                    config.decode_alarm_state(self.get_alarm()),
                    self.get_battery_percentage_value(),
                    self.lora_rec_stats.rssi), True)
            else:
                ti = time.time()
                message = struct.pack('s8sbbbffI',
                    msgs.HEARTBEAT_LOC[0], bytes(self.SSID, 'ascii'),
                    self.get_alarm(),
                    self.get_battery_percentage_value(),
                    self.lora_rec_stats.rssi, coords[0], coords[1], ti)
                #tip = time.localtime(ti)
                #self.LOG("Heartbeat,{},{},{},{},{:.6f},{:.6f},{}/{:02}/{:02}-{:02}:{:02}:{:02}_UTC".format(
                #    self.SSID,
                #    config.decode_alarm_state(self.get_alarm()),
                #    self.get_battery_percentage_value(),
                #    self.lora_rec_stats.rssi,
                #    coords[0], coords[1],
                #    tip[0], tip[1], tip[2], tip[3], tip[4], tip[5]), True)

                self.LOG("Heartbeat,{},{},{},{},{:.6f},{:.6f},{}".format(
                    self.SSID,
                    config.decode_alarm_state(self.get_alarm()),
                    self.get_battery_percentage_value(),
                    self.lora_rec_stats.rssi,
                    coords[0], coords[1], config.decode_datetime(ti), True))

            self.send_message(message)
            #
            # Look to see if we've not heard from anyone we know about.
            # Decrement all counters. When we decrement to 0 we start sending
            # out OutOfComm messages for the node. If it comes back into range
            # the node counter is reset.
            #
            # Note that if the counter is less than zero then if we
            # recieve a relay message with that node, we send it up as if we
            # recieved it directly, as if the node is in direct range.
            #
            with self.group_members_lock:
                for key, value in self.group_members.items():
                    if value > 0:
                        value -= 1
                        self.group_members.update({key : value})
                    else:
                        self.send_out_of_comm_msg(key)
                        self.LOG("OutOfComm,{}".format(key), True)
            #
            # Sleep a random amount of time between LORA_MIN_TIMEOUT and
            # LORA_MIN_TIME + LORA_RND_TIMEOUT.
            #
            time.sleep((machine.rng() & config.LORA_RND_TIMEOUT) + config.LORA_MIN_TIMEOUT)

    # ------------------------------------------------------------------------
    # Single point to send a LoRa message via LoRa socket. This is similar to
    # the single point to recieve LoRa messages. Critical errors can be handled
    # in one location.
    #
    def send_message(self, message):
            #
            # This is a very intermediate error that will crop up when least
            # expected. I've trapped it here and call this function where a
            # socket send would be used.
            #
            # Further documentation:
            # https://github.com/pycom/pycom-micropython-sigfox/blob/5bed5e9a84bb1abfc4d59476f3f62b38920c5eda/py/mperrno.h
            # https://github.com/pycom/pycom-micropython-sigfox/blob/master/esp32/mods/modlora.c#L2082
            #
            try:
                with self.send_lock:
                    self.lora_socket.send(message)
            except OSError as ose:
                self.LOG('LORA_OSError_1 {}'.format(ose.args[0]))
                #
                # I've been forced to create an auto-reset section.
                # Once this error occurs the entire LoRa hardware stack
                # is truly and thoroughly fucked and cannot be recovered by any
                # other method. Thus the use of machine.reset()
                #
                # I am very unhappy with the overall quality of the Pycom FiPy,
                # as this error seems to be scattered around a number of Pycom
                # boards.
                #
                machine.reset()


    # ------------------------------------------------------------------------
    # The purpose of writing all of these message send functions is to
    # 'corral' every use of lora_socket.send. Every instance used is in the
    # following section except for one, and that one is just above in the
    # heartbeat send thread.
    #
    # This also locates every message's binary struction in one convenient
    # location.
    #
    # Before someone gets the idea of spreading these out for whatever reason,
    # that it was that way originally, and it was hell to maintain.

    def route_message(self, rmsg_type, msg):
        dataArray = bytearray(msg)
        dataArray[0] = rmsg_type.encode('utf-8')[0]
        self.send_message(bytes(dataArray))

    def send_out_of_comm_msg(self, node):
        message = struct.pack('s8s8s', msgs.OUT_OF_COMM[0], node, self.SSID)
        self.send_message(message)

    def send_in_comm_msg(self, node):
        message = struct.pack('s8s8s', msgs.IN_COMM[0], node, self.SSID)
        self.send_message(message)

    def reset_all(self):
        message = struct.pack('s8s', msgs.RESET_ALL[0], self.SSID)
        self.send_message(message)

    def send_emergency(self):
        message = struct.pack('s8s', msgs.ALARM[0], self.SSID)
        self.send_message(message)

    def confirm_emergency(self, node):
        message = struct.pack('s8s8s', msgs.CONFIRM_ALARM[0], self.SSID, node)
        self.send_message(message)

    def clear_alarm(self, node):
        message = struct.pack('s8s8s', msgs.CLEAR_ALARM[0], self.SSID, node)
        self.send_message(message)

    # ------------------------------------------------------------------------
    # Process all inbound text-based commands. Compile them into equivalent
    # LoRa binary messages and then send them out.
    #
    def process_command(self, cmd_data):
        command = cmd_data.strip()

        if len(command) == 0:
            return

        args = command.split(',')
        self.LOG('>>> GotCommand:{}'.format(command))

        if args[0] == 'SendAlarm':
            self.set_alarm(config.ALARM)
            self.send_emergency()
            self.LOG(command, True)

        elif args[0] == 'ConfirmAlarm':
            self.confirm_emergency(args[1])
            self.LOG(command, True)

        elif args[0] == 'ClearAlarm':
            self.clear_alarm(args[1])
            self.LOG(command, True)

        elif args[0] == 'Nodes':
            nodes = self.list_group_nodes()
            self.LOG(nodes, True)

        elif args[0] == 'OOCOM':
            nodes = self.list_oocom()
            if len(nodes) == 0:
                self.LOG('OOCOM,NONE', True)
            else:
                self.LOG('OOCOM,{}'.format(','.join(nodes)), True)

        elif args[0] == 'ClearNodes':
            self.clear_all_group_nodes()
            self.LOG('NodesCleared', True)

        elif args[0] == 'WhoAmI':
            self.LOG(self.who_am_i, True)

        elif args[0] == 'ResetAll':
            self.reset_all()
            self.set_alarm(config.NO_ALARM)
            self.LOG('ResetAll', True)
        else:
            self.LOG('CommandProcessor,DidNotProcess,|{}|'.format(command), True)
