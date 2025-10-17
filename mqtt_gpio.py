import paho.mqtt.client as mqtt
from gpiozero import LED

# ---------------- GPIO Configuration ----------------
gpio_pins = {
    17: LED(17),
    27: LED(27),
    22: LED(22)
}

# ---------------- MQTT Broker Configuration ----------------
broker = "13.234.21.33"  # আপনার EC2 Public IP
port = 1883

# MQTT Client
client = mqtt.Client("raspberrypi")

# ---------------- Topic Mapping ----------------
# Dashboard JS অনুযায়ী topics
set_topic_map = {
    17: "home/device/rpi-01/gpio/17/set",
    27: "home/device/rpi-01/gpio/27/set",
    22: "home/device/rpi-01/gpio/22/set"
}

state_topic_map = {
    17: "home/device/rpi-01/gpio/17/state",
    27: "home/device/rpi-01/gpio/27/state",
    22: "home/device/rpi-01/gpio/22/state"
}

# ---------------- MQTT Callbacks ----------------
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # সব /set topic subscribe
    for topic in set_topic_map.values():
        client.subscribe(topic)
    print("Subscribed to set topics")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode().upper()
    print(f"{topic}: {payload}")

    # কোন pin এর topic আসছে check
    for pin, t in set_topic_map.items():
        if topic == t:
            if payload == "ON":
                gpio_pins[pin].on()
            elif payload == "OFF":
                gpio_pins[pin].off()
            # Corresponding /state topic publish
            client.publish(state_topic_map[pin], payload)
            print(f"GPIO {pin} set to {payload}")

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
