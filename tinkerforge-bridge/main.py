# HOST = "wifi-extension-v2"
HOST = "192.168.1.139"
PORT = 4223
UID = "CWZ"
UDP_IP = "0.0.0.0"
UDP_PORT = 80
MESSAGE = "Hello, World!2"

MASTERBRICK_GARAGE_IP = "192.168.1.210"
MASTERBRICK_GARAGE_PORT = 4223
MASTERBRICK_GARAGE_RELAY_EXTENSION_1_UID = "CXm"
MASTERBRICK_GARAGE_TEMPERATURE_EXTENSION_UID = "zkc"
MASTERBRICK_GARAGE_DIGITAL_IN_EXTENSION_UID = "CpG"

server_address = ('192.168.1.100', 8000)


import eventlet
eventlet.monkey_patch()

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_humidity_v2 import BrickletHumidityV2
from tinkerforge.bricklet_dual_relay import BrickletDualRelay
from tinkerforge.bricklet_temperature import BrickletTemperature
from time import sleep
from flask import Flask, render_template
from flask_socketio import SocketIO
import socket


def cb_humidity(humidity):
    print("Masterbrick Server - Humidity: " + str(temp/100.0) + " % RH")
    string = "humserver=" + str(humidity/100.0)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.sendto(string.encode(), server_address)
    sock.close()


def cb_temperature(temp):
    print("Masterbrick Server - Temperature: " + str(temp/100.0) + " °C")
    string = "tempserver=" + str(temp/100.0)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.sendto(string.encode(), server_address)
    sock.close()


def cb_temperature_masterbrick_garage(temperature):
    print("Masterbrick Garage - Temperature: " + str(temperature/100.0) + " °C")
    string = "tempgarage=" + str(temperature/100.0)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.sendto(string.encode(), server_address)
    sock.close()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'IBims1SecretVongServerHer'
socketio = SocketIO(app)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/hum")
def get_hum():
    ipcon = IPConnection()
    h = BrickletHumidityV2(UID, ipcon)
    ipcon.connect(HOST, PORT)
    humidity = h.get_humidity()
    temperature = h.get_temperature()
    ipcon.disconnect()
    return str(humidity/100.0) + ";" + str(temperature/100.0)


@app.route("/garage/light/on")
def garage_light_on():
    try:
        ipcon = IPConnection()
        ipcon.connect(MASTERBRICK_GARAGE_IP, MASTERBRICK_GARAGE_PORT)
        dr = BrickletDualRelay(MASTERBRICK_GARAGE_RELAY_EXTENSION_1_UID, ipcon)
        dr.set_state(True, False)
        ipcon.disconnect()
    except:
        return "error"
    return "ok"


@app.route("/garage/light/off")
def garage_light_off():
    try:
        ipcon = IPConnection()
        ipcon.connect(MASTERBRICK_GARAGE_IP, MASTERBRICK_GARAGE_PORT)
        dr = BrickletDualRelay(MASTERBRICK_GARAGE_RELAY_EXTENSION_1_UID, ipcon)
        dr.set_state(False, False)
        ipcon.disconnect()
    except:
        return "error"
    return "ok"


if __name__ == '__main__':

    ipcon = IPConnection()
    ipcon.connect(HOST, PORT)

    h = BrickletHumidityV2(UID, ipcon)
    h.register_callback(h.CALLBACK_TEMPERATURE, cb_temperature)
    h.register_callback(h.CALLBACK_HUMIDITY, cb_humidity)
    h.set_temperature_callback_configuration(30000, False, "x", 0, 0)
    h.set_humidity_callback_configuration(30000, False, "x", 0, 0)

    # --- GARAGE SERVER CALLBACKS ---

    masterbrick_garage_ipcon = IPConnection()
    masterbrick_garage_ipcon.connect(HOST, PORT)
    t = BrickletTemperature(MASTERBRICK_GARAGE_TEMPERATURE_EXTENSION_UID, masterbrick_garage_ipcon)
    t.register_callback(t.CALLBACK_TEMPERATURE, cb_temperature_masterbrick_garage)
    t.set_temperature_callback_period(30000)

    socketio.run(app, host='0.0.0.0', port=80, debug=False)

    ipcon.disconnect()
    masterbrick_garage_ipcon.disconnet()
