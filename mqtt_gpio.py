import paho.mqtt.client as mqtt
from gpiozero import LED

# ---------------- GPIO Configuration ----------------
gpio_pins = {
    "pi_led1": LED(17),
    "pi_led2": LED(27),
    "pi_led3": LED(22)
}

# ---------------- MQTT Broker Configuration ----------------
broker = "13.234.21.33"   # আপনার EC2 public IP বসান
port = 1883
client = mqtt.Client("raspberrypi")  # v1.6.1 compatible

# ---------------- MQTT Callbacks ----------------
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    for topic in gpio_pins:
        client.subscribe(topic)
    client.publish("status/pi", "online")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode().upper()
    print(f"{topic}: {payload}")

    if topic in gpio_pins:
        if payload == "ON":
            gpio_pins[topic].on()
        elif payload == "OFF":
            gpio_pins[topic].off()
        client.publish(f"status/{topic}", payload)

# ---------------- MQTT Setup ----------------
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, port, 60)

# ---------------- Main Loop ----------------
try:
    client.loop_forever()
except KeyboardInterrupt:
    for led in gpio_pins.values():
        led.off()
    client.disconnect()
    print("Disconnected cleanly")
