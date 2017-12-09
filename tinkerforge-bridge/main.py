# HOST = "wifi-extension-v2"
HOST = "192.168.1.139"
PORT = 4223
UID = "CWZ"
UDP_IP = "0.0.0.0"
UDP_PORT = 80
MESSAGE = "Hello, World!2"

server_address = ('192.168.1.100', 8000)


import eventlet
eventlet.monkey_patch()

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_humidity_v2 import BrickletHumidityV2
from time import sleep
from flask import Flask, render_template
from flask_socketio import SocketIO
import socket


def cb_humidity(humidity):
    string = "humserver=" + str(humidity/100.0)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.sendto(string.encode(), server_address)
    sock.close()


def cb_temperature(temp):
    string = "tempserver=" + str(temp/100.0)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.sendto(string.encode(), server_address)
    sock.close()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
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


if __name__ == '__main__':

    ipcon = IPConnection()
    ipcon.connect(HOST, PORT)

    h = BrickletHumidityV2(UID, ipcon)
    h.register_callback(h.CALLBACK_TEMPERATURE, cb_temperature)
    h.register_callback(h.CALLBACK_HUMIDITY, cb_humidity)
    h.set_temperature_callback_configuration(20000, False, "x", 0, 0)
    h.set_humidity_callback_configuration(20000, False, "x", 0, 0)

    socketio.run(app, host='0.0.0.0', port=80, debug=False)

    ipcon.disconnect()
