import paho.mqtt.client as mqtt
from gpiozero import LED
from time import sleep

# ---------------- GPIO Configuration ----------------
gpio_pins = {
    "pi_led1": LED(17),
    "pi_led2": LED(27),
    "pi_led3": LED(22)
}

# ---------------- MQTT Broker Configuration ----------------
broker = "13.234.21.33"   # এখানে আপনার AWS EC2 public IP বসান
port = 1883
client = mqtt.Client("raspberrypi")

# ---------------- MQTT Callbacks ----------------
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # সব টপিক সাবস্ক্রাইব করা
    for topic in gpio_pins:
        client.subscribe(topic)
    # স্টেটাস পাঠানো
    client.publish("status/pi", "online")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    print(f"{topic}: {payload}")

    # নির্দিষ্ট টপিক অনুযায়ী GPIO অন/অফ করা
    if topic in gpio_pins:
        if payload.upper() == "ON":
            gpio_pins[topic].on()
        elif payload.upper() == "OFF":
            gpio_pins[topic].off()
        # Dashboard-এ লাইভ স্টেটাস পাঠানো
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
