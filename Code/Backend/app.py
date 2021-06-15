import time
from RPi import GPIO
import threading
from Mcp import Mcp
from KlasseLCDPCF import KlasseLCDPCF
from subprocess import check_output

from flask_cors import CORS
from flask_socketio import SocketIO, emit, send
from flask import Flask, jsonify, request
from repositories.DataRepository import DataRepository
from datetime import datetime, date


# Code voor Hardware
sensor_file_name1 = '/sys/bus/w1/devices/28-03189779e3f7/w1_slave'
sensor_file_name2 = '/sys/bus/w1/devices/28-00000da0125f/w1_slave'
sensor_file_name3 = '/sys/bus/w1/devices/28-00000d9f5e61/w1_slave'
temperaturen = ['Nog geen waarde gemeten.',
                'Nog geen waarde gemeten.', 'Nog geeen waarde gemeten.']

id_temperatuur_sensor1 = 6
id_temperatuur_sensor2 = 7
id_temperatuur_sensor3 = 8

id_light_sensor1 = 1
id_light_sensor2 = 2
id_light_sensor3 = 3
id_light_sensor4 = 4
id_light_sensor5 = 5

id_moisture_sensor = 9
id_water_sensor = 10

pin_blue_leds = 12
pin_green_leds = 19
pin_pump = 26

GPIO.setwarnings(False)
adc = Mcp(0, 0)
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_blue_leds, GPIO.OUT)
GPIO.setup(pin_green_leds, GPIO.OUT)
GPIO.setup(pin_pump, GPIO.OUT)


def read_temp_sensor():
    while True:
        sensor_file1 = open(sensor_file_name1, 'r')
        for line in sensor_file1:
            line = line.rstrip('\n')
            plaats = line.find('t=')
            if plaats != -1:
                temperaturen[0] = round(int(line[29:34])/1000+0.6, 2)
        sensor_file1.close()

        sensor_file2 = open(sensor_file_name2, 'r')
        for line in sensor_file2:
            line = line.rstrip('\n')
            plaats = line.find('t=')
            if plaats != -1:
                temperaturen[1] = round(int(line[29:34])/1000-0.9, 2)
        sensor_file2.close()

        sensor_file3 = open(sensor_file_name3, 'r')
        for line in sensor_file3:
            line = line.rstrip('\n')
            plaats = line.find('t=')
            if plaats != -1:
                temperaturen[2] = round(int(line[29:34])/1000-0.8, 2)
        sensor_file3.close()
        if DataRepository.create_log_temp_sensor(id_temperatuur_sensor1, datetime.now(), temperaturen[0]) and DataRepository.create_log_temp_sensor(id_temperatuur_sensor2, datetime.now(), temperaturen[1]) and DataRepository.create_log_temp_sensor(id_temperatuur_sensor3, datetime.now(), temperaturen[2]):
            socketio.emit('B2F_waarde_temperatuur_sensoren', {
                          'temperatuur_sensoren': temperaturen})
            print(temperaturen)
            time.sleep(60)


def read_light_sensors():
    pwm_green_leds = GPIO.PWM(pin_green_leds, 200)
    pwm_green_leds.start(0)
    while True:
        values_light_sensors = [round((1023-adc.read_channel(id_light_sensor1-1))/10.23, 2), round((1023-adc.read_channel(id_light_sensor2-1))/10.23, 2), round(
            (1023-adc.read_channel(id_light_sensor3-1))/10.23, 2), round((1023-adc.read_channel(id_light_sensor4-1))/10.23, 2), round((1023-adc.read_channel(id_light_sensor5-1))/10.23, 2)]
        avg = 0
        for light in values_light_sensors:
            avg += light
        pwm_green_leds.ChangeDutyCycle(round((avg/len(values_light_sensors))*4.5,0))
        if DataRepository.create_log_light_sensor(id_light_sensor1, datetime.now(), values_light_sensors[0]) and DataRepository.create_log_light_sensor(id_light_sensor2, datetime.now(), values_light_sensors[1]) and DataRepository.create_log_light_sensor(id_light_sensor3, datetime.now(), values_light_sensors[2]) and DataRepository.create_log_light_sensor(id_light_sensor4, datetime.now(), values_light_sensors[3]) and DataRepository.create_log_light_sensor(id_light_sensor5, datetime.now(), values_light_sensors[4]):
            socketio.emit('B2F_value_light_sensor', {
                          'light_sensors': values_light_sensors})
            print(values_light_sensors)
            time.sleep(60)


def read_moisture_sensor():
    pwm_blue_leds = GPIO.PWM(pin_blue_leds, 200)
    pwm_blue_leds.start(0)
    while True:
        value_moisture_sensor = round(adc.read_channel(5)/10.23*1.4, 2)
        pwm_blue_leds.ChangeDutyCycle(round(value_moisture_sensor,0))
        print(f"Pomp: {value_moisture_sensor}")
        if value_moisture_sensor < 30:
            water_pump()
        if DataRepository.create_log_moisture_sensor(id_moisture_sensor, datetime.now(), value_moisture_sensor):
            socketio.emit("B2F_value_moisture_sensor", {
                          'moisture_sensor': value_moisture_sensor})
            print(value_moisture_sensor)
            time.sleep(60)


def water_pump():
    print("POMP aan")
    GPIO.output(pin_pump, GPIO.HIGH)
    # DataRepository.create_log_pump(11, datetime.now(), 1)
    time.sleep(2)
    GPIO.output(pin_pump, GPIO.LOW)
    # DataRepository.create_log_pump(11, datetime.now(), 0)


def print_ip_on_screen():
    lcd = KlasseLCDPCF(False, 21, 20)
    ips = get_ips()
    print(ips)
    lcd.LCDInit()
    lcd.sendMessage(ips[0])
    lcd.secondRow()
    lcd.sendMessage(ips[1])


def get_ips():
    ips = str(check_output(['hostname', '--all-ip-addresses']))
    ips = ips.replace("b'", "")
    ips = ips.replace("\\n'", "")
    ips = ips.split(" ")
    return ips


    # Code voor Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'geheim!'
socketio = SocketIO(app, cors_allowed_origins="*", logger=False,
                    engineio_logger=False, ping_timeout=1)

CORS(app)


@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    print(e)


# START een thread op. Belangrijk!!! Debugging moet UIT staan op start van de server, anders start de thread dubbel op
# werk enkel met de packages gevent en gevent-websocket.
read_temp = threading.Timer(30, read_temp_sensor)
read_temp.start()
read_light = threading.Timer(30, read_light_sensors)
read_light.start()
read_moisture = threading.Timer(30, read_moisture_sensor)
read_moisture.start()
print_ip = threading.Timer(20, print_ip_on_screen)
print_ip.start()


print("**** Program started ****")

# API ENDPOINTS
endpoint = "/api/v1"


@app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."


@app.route(endpoint + "/history/<id>", methods=["GET"])
def get_histry_sensor(id):
    if request.method == "GET":
        final_value = []
        labels = []
        if id == "1":

            values1 = DataRepository.read_history(1)
            values2 = DataRepository.read_history(2)
            values3 = DataRepository.read_history(3)
            values4 = DataRepository.read_history(4)
            values5 = DataRepository.read_history(5)
            for i in range(0, len(values1)):
                data_pre_process = (values1[i]["Waarde"] + values2[i]["Waarde"] +
                                    values3[i]["Waarde"] + values4[i]["Waarde"] + values5[i]["Waarde"]) / 5
                final_value.append(round(data_pre_process, 2))
                labels.append(values1[i]["Datum"])
        elif id == "6":
            values1 = DataRepository.read_history(6)
            values2 = DataRepository.read_history(7)
            values3 = DataRepository.read_history(8)
            for i in range(0, len(values1)):
                data_pre_process = (values1[i]["Waarde"] + values2[i]["Waarde"] +
                                    values3[i]["Waarde"]) / 3
                final_value.append(round(data_pre_process, 2))
                labels.append(values1[i]["Datum"])

        elif id == "9":
            value = DataRepository.read_history(9)
            for i in range(0, len(value)):
                final_value.append(round(value[i]["Waarde"], 2))
                labels.append(value[i]["Datum"])
        final_value.reverse()
        labels.reverse()
        return jsonify(waardes=final_value, label=labels), 200


@socketio.on('connect')
def initial_connection():
    print('A new client connect')
    # # Send to the client!
    socketio.emit('connected')


@socketio.on('F2B_get_last_temps')
def get_last_temps():
    temperaturen = [DataRepository.read_last_record(6)['Waarde'], DataRepository.read_last_record(7)[
        'Waarde'], DataRepository.read_last_record(8)['Waarde']]
    print(temperaturen)
    socketio.emit('B2F_waarde_temperatuur_sensoren', {
                  'temperatuur_sensoren': temperaturen})


@socketio.on('F2B_get_last_light')
def get_last_lights():
    lights = [DataRepository.read_last_record(1)['Waarde'], DataRepository.read_last_record(1)[
        'Waarde'], DataRepository.read_last_record(3)['Waarde'], DataRepository.read_last_record(4)['Waarde'], DataRepository.read_last_record(5)['Waarde']]
    print(lights)
    socketio.emit('B2F_value_light_sensor', {
                  'light_sensors': lights})


@socketio.on("F2B_get_last_moisture")
def get_last_moisture():
    moisture = DataRepository.read_last_record(9)['Waarde']
    print(moisture)
    socketio.emit("B2F_value_moisture_sensor", {
        'moisture_sensor': moisture})


@socketio.on("F2B_activate_pump")
def activate_pump():
    water_pump()
    print("pomp aan")


# ANDERE FUNCTIES
if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')
