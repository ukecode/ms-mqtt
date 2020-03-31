from decouple import config
from flask import Flask, request, jsonify
from flask_mqtt import Mqtt
from random import random
import json
import requests
app = Flask(__name__)

# Funcionalidades MQTT
app.config['MQTT_REFRESH_TIME'] = 1.0
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = config('MQTT_URL')
app.config['MQTT_BROKER_PORT'] = int(config('MQTT_PORT'))
app.config['MQTT_USERNAME'] = config('MQTT_USER')
app.config['MQTT_PASSWORD'] = config('MQTT_PASSWORD')
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TLS_ENABLED'] = False
mqtt = Mqtt(app)


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('#')

@mqtt.on_subscribe()


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    topic = message.topic
    payload = message.payload.decode()
    payload = json.loads(payload)
    print(topic, payload)
    if topic == 'controller/sendrequest':
        print(payload['method'], payload['url'])
        req = ""
        if payload['method'].lower() == 'get':
            req = requests.get(payload['url'])
            print(req.text)
        if payload['method'].lower() == 'post':
            req = requests.post(payload['url'], data=payload['body'])
        if payload['method'].lower() == 'put':
            req = requests.put(payload['url'], data=payload['body'])
        if payload['method'].lower() == 'delete':
            req = requests.delete(payload['url'], data=payload['body'])
        print(req)
        mqtt.publish('controller/out', req.status_code)


def handle_publish(data):
    mqtt.publish(data['topic'], data['message'])


@app.route('/')
def index():
    return {"data": random()}


@app.route('/send-mqtt', methods=['POST'])
def send_mqtt():
    content = request.json
    handle_publish(content)
    return content

if __name__ == '__main__':
    app.run(port=config('PORT'))
