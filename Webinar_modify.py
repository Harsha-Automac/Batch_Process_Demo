import pymodbus
import serial
from pymodbus.pdu import ModbusRequest
from pymodbus.client.sync import ModbusSerialClient as ModbusClient  # initialize a serial RTU client instance
from pymodbus.transaction import ModbusRtuFramer
import json
import paho.mqtt.client as mqtt
import datetime
import time

client = ModbusClient(method="rtu", port="/dev/ttyUSB0", stopbits=1, bytesize=8, parity='E', baudrate=9600)

connection = client.connect()


class mqtttest():
    def __init__(self):
        self.msg = '{"start":"null", "mode":"null"}'

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe("demo/control/01")

    def on_message(self, client, userdata, msg):
        strmsg = msg.payload.decode()
        self.msg = strmsg


test = mqtttest()
mqclient = mqtt.Client()
mqclient.connect("broker.hivemq.com", 1883, 60)
mqclient.loop_start()
mqclient.on_connect = test.on_connect
mqclient.on_message = test.on_message

def sensor_valve_status():
    t1hl = client.read_discrete_inputs(1024, 1, unit=0x01)
    print("t1hl  ", not t1hl.bits[0])
    t1ll = client.read_discrete_inputs(1025, 1, unit=0x01)
    print("t1ll  ", not t1ll.bits[0])
    mqclient.publish('demo/monitor/01', json.dumps(
        {'type': 'sensor_status', 'tank_one_high_level': not t1hl.bits[0], 'tank_one_low_level': not t1ll.bits[0],
         'date': datetime.datetime.now().isoformat()}))

    t2hl = client.read_discrete_inputs(1026, 1, unit=0x01)
    print("t2hl  ", not t2hl.bits[0])
    t2ll = client.read_discrete_inputs(1027, 1, unit=0x01)
    print("t2ll  ", t2ll.bits[0])
    mqclient.publish('demo/monitor/01', json.dumps(
        {'type': 'sensor_status', 'tank_two_high_level': not t2hl.bits[0], 'tank_two_low_level': t2ll.bits[0],
         'date': datetime.datetime.now().isoformat()}))

    t3hl = client.read_discrete_inputs(1028, 1, unit=0x01)
    print("t3hl  ", not t3hl.bits[0])
    t3ll = client.read_discrete_inputs(1029, 1, unit=0x01)
    print("t3ll  ", not t3ll.bits[0])
    mqclient.publish('demo/monitor/01', json.dumps(
        {'type': 'sensor_status', 'tank_three_high_level': not t3hl.bits[0], 'tank_three_low_level': not t3ll.bits[0],
         'date': datetime.datetime.now().isoformat()}))

    sv1 = client.read_coils(1280, 1, unit=0x01)
    print("sv1  ", sv1.bits[0])
    mqclient.publish('demo/monitor/01', json.dumps({'type': 'valve_status', 'tank_one_valve': sv1.bits[0],
                                                    'date': datetime.datetime.now().isoformat()}))

    sv2 = client.read_coils(1281, 1, unit=0x01)
    print("sv2  ", sv2.bits[0])
    mqclient.publish('demo/monitor/01', json.dumps({'type': 'valve_status', 'tank_two_valve': sv2.bits[0],
                                                    'date': datetime.datetime.now().isoformat()}))

    sv3 = client.read_coils(1282, 1, unit=0x01)
    print("sv3  ", sv3.bits[0])
    mqclient.publish('demo/monitor/01', json.dumps({'type': 'valve_status', 'tank_three_valve': sv3.bits[0],
                                                    'date': datetime.datetime.now().isoformat()}))

    m1 = client.read_coils(1283, 1, unit=0x01)
    print("m1  ", m1.bits[0])
    mqclient.publish('demo/monitor/01', json.dumps({'type': 'motor_status', 'motor': m1.bits[0],
                                                    'date': datetime.datetime.now().isoformat()}))


def manual_mode(push):
    time.sleep(1)
    print("In the Manual FN")
    sensor_valve_status()
    try:
        print("bfr motor False")
        if (push['motor'] == False):
            print("M - 0")
            result5 = client.write_register(4102, 0, unit=0x01)
            print(result5)
        # D4 - Tank 1 Solenoid Valve
        print("bfr motor True")
        if (push['motor'] == True):
            print("M - 1")
            result5 = client.write_register(4102, 1, unit=0x01)
            print(result5)
    except:
        print("Key error")

    try:
        # print("bfr tank_one_valve True")
        if (push['tank_one_valve'] == True):
            print("TOV - 1")
            result5 = client.write_register(4100, 1, unit=0x01)
            print(result5)
        if (push['tank_one_valve'] == False):
            print("TOV - 0")
            result5 = client.write_register(4100, 0, unit=0x01)
            print(result5)
    except:
        print("Key error")

    try:
        if (push['tank_two_valve'] == True):
            print("TTV - 1")
            result5 = client.write_register(4101, 1, unit=0x01)
            print(result5)
        if (push['tank_two_valve'] == False):
            print("TTV - 0")
            result5 = client.write_register(4101, 0, unit=0x01)
            print(result5)
    except:
        print("Key error")

    try:
        # D7 - Tank 3 Solenoid Valve
        if (push['tank_three_valve'] == True):
            result5 = client.write_register(4103, 1, unit=0x01)
            print(result5)
        if (push['tank_three_valve'] == False):
            result5 = client.write_register(4103, 0, unit=0x01)
    except:
        print("Key error")

    try:
        if (push['emg'] == True):
            print("emg enter true")
            result5 = client.write_register(4099, 1, unit=0x01)

        if (push['emg'] == False):
            print("emg enter false")
            result5 = client.write_register(4099, 0, unit=0x01)
            D1 = client.write_register(4097, 1, unit=0x01)
            D2 = client.write_register(4098, 0, unit=0x01)
    except:
        print("Key error")

def auto_mode():
    print('In Auto FN')
    time.sleep(1)
    sensor_valve_status()
    try:
        if(push['start'] == True):
            print("Machine in Auto and start")
            mqclient.publish('demo/monitor/01',
                     json.dumps({"type": "ack", "mode": "auto", "start": True}))
            result = client.write_register(4096, 1, unit=0x01)
            D1 = client.write_register(4097, 1, unit=0x01)
            D2 = client.write_register(4098, 0, unit=0x01)
            #mode = "auto
        if(push['start'] == False):
            print("Machine in Auto and stop")
            mqclient.publish('demo/monitor/01',
                     json.dumps({"type": "ack", "mode": "auto", "start": False}))
            result = client.write_register(4096, 1, unit=0x01)
            D1 = client.write_register(4097, 0, unit=0x01)
            D2 = client.write_register(4098, 1, unit=0x01)
    except:
        print("start error")

    try:
        if (push['emg'] == True):
            print("emg enter true")
            result5 = client.write_register(4099, 1, unit=0x01)

        if (push['emg'] == False):
            print("emg enter false")
            result5 = client.write_register(4099, 0, unit=0x01)
            D1 = client.write_register(4097, 1, unit=0x01)
            D2 = client.write_register(4098, 0, unit=0x01)
    except:
        print("emg error")




while True:
    push = json.loads(test.msg)
    print("push   ", push)

    if (push['mode'] == 'manual'):
        print("Machine in Manual")
        mqclient.publish('demo/monitor/01',
                         json.dumps({"type": "ack", "mode": "manual"}))
        result = client.write_register(4096, 2, unit=0x01)
        # print(result.registers)
        mode = "manual"
        manual_mode(push)

    if (push['mode'] == 'auto'):
        auto_mode()

