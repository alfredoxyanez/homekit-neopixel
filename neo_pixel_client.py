# MQTT Client demo
# Continuously monitor two different MQTT topics for data,
# check if the received data matches two predefined 'commands'

import paho.mqtt.client as mqtt
from neopixel import *
import colorsys
import time
import threading

# LED strip configuration:
LED_COUNT = 16  # Number of LED pixels.
LED_PIN = 12  # GPIO pin connected to the pixels (18 uses PWM!).
LED_PIN2 = 13  # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_PIN3 = 18
LED_PIN4 = 19
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_CHANNEL2 = 1  # set to '1' for GPIOs 13, 19, 41, 45 or 53
cycle = False

#[saturation,hue,brightness,r,g,b]
rgbs = [[0, 0, 100, 255, 255, 255], [0, 0, 100, 255, 255, 255]]


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    global strip1
    global strip2
    global strip3
    global strip4

    strip1 = Adafruit_NeoPixel(LED_COUNT, 12, LED_FREQ_HZ, LED_DMA, LED_INVERT,
                               LED_BRIGHTNESS, 0)
    strip2 = Adafruit_NeoPixel(LED_COUNT, 13, LED_FREQ_HZ, LED_DMA, LED_INVERT,
                               LED_BRIGHTNESS, 1)
    strip3 = Adafruit_NeoPixel(LED_COUNT, 18, LED_FREQ_HZ, LED_DMA, LED_INVERT,
                               LED_BRIGHTNESS, 0)
    strip4 = Adafruit_NeoPixel(LED_COUNT, 19, LED_FREQ_HZ, LED_DMA, LED_INVERT,
                               LED_BRIGHTNESS, 1)
    strip1.begin()
    strip2.begin()
    strip3.begin()
    strip4.begin()
    #test
    client.subscribe('test/#')

    #Light1
    client.subscribe("light1/#")
    # client.subscribe("light1/report/status")
    # client.subscribe("light1/status")
    # client.subscribe("light1/report/brightness")
    # client.subscribe("light1/brightness")
    # client.subscribe("light1/report/hue")
    # client.subscribe("light1/hue")
    # client.subscribe("light1/report/saturation")
    # client.subscribe("light1/saturation")
    #Light2
    client.subscribe("light2/#")
    client.subscribe("lights/random")
    # client.subscribe("light2/report/status")
    # client.subscribe("light2/status")
    # client.subscribe("light2/report/brightness")
    # client.subscribe("light2/brightness")
    # client.subscribe("light2/report/hue")
    # client.subscribe("light2/hue")
    # client.subscribe("light2/report/saturation")
    # client.subscribe("light2/saturation")


def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def colorWipe2(strip, strip2, all_rgb, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    print("colorwipe2", cycle)
    colors = [Color(0, 255, 0), Color(255, 0, 0), Color(0, 0, 255)]
    while True:
        if cycle == False:
            break
        for color in colors:
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, color)
                strip2.setPixelColor(i, color)
                strip.show()
                strip2.show()
                time.sleep(wait_ms / 1000.0)
    color = Color(all_rgb[0][4], all_rgb[0][3], all_rgb[0][5])
    color2 = Color(all_rgb[1][4], all_rgb[1][3], all_rgb[1][5])
    colorWipe(strip, color)
    colorWipe(strip2, color2)


def light_status(msg, strip, rgb_index, all_rgb):
    if msg.payload == "true":
        print('ON status ', rgb_index)
        color = Color(all_rgb[rgb_index][4], all_rgb[rgb_index][3],
                      all_rgb[rgb_index][5])
        if all_rgb[rgb_index][2] == 0:
            all_rgb[rgb_index][2] = 100
        strip.setBrightness(all_rgb[rgb_index][2])
        colorWipe(strip, color)
    else:
        all_rgb[rgb_index][2] = 0
        strip.setBrightness(all_rgb[rgb_index][2])
        strip.show()


def brightness(msg, strip, rgb_index, all_rgb):
    print('inside bts ', rgb_index)
    bn = int(msg.payload)
    bn = int(255 * bn * .01)
    all_rgb[rgb_index][2] = bn
    strip.setBrightness(all_rgb[rgb_index][2])
    strip.show()


def hue(msg, strip, rgb_index, all_rgb):
    all_rgb[rgb_index][1] = int(msg.payload) / 360.0
    c = colorsys.hls_to_rgb(all_rgb[rgb_index][1], .5, all_rgb[rgb_index][0])
    all_rgb[rgb_index][3] = int(c[0] * 255)
    all_rgb[rgb_index][4] = int(c[1] * 255)
    all_rgb[rgb_index][5] = int(c[2] * 255)
    color = Color(all_rgb[rgb_index][4], all_rgb[rgb_index][3],
                  all_rgb[rgb_index][5])
    colorWipe(strip, color)
    print(color, 'wipe')


def saturation(msg, strip, rgb_index, all_rgb):
    all_rgb[rgb_index][0] = int(msg.payload) * .01
    c2 = colorsys.hls_to_rgb(all_rgb[rgb_index][1], .5, all_rgb[rgb_index][0])
    all_rgb[rgb_index][3] = int(c2[0] * 255)
    all_rgb[rgb_index][4] = int(c2[1] * 255)
    all_rgb[rgb_index][5] = int(c2[2] * 255)
    color = Color(all_rgb[rgb_index][4], all_rgb[rgb_index][3],
                  all_rgb[rgb_index][5])
    colorWipe(strip, color)
    print(color, 'wipe')


    #for i in range(strip.numPixels()):
    #    strip.setPixelColor(i, color)
    #strip.show()
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    global rgbs
    global cycle
    print(rgbs)
    if msg.topic == "light1/status":
        cycle = False
        light_status(msg, strip1, 0, rgbs)
    if msg.topic == "light2/status":
        print('light2')
        cycle = False
        light_status(msg, strip2, 1, rgbs)
    # if msg.topic == "light3/status":
    #     print('light3')
    #     light_status(msg, strip3, 2, rgbs)
    # if msg.topic == "light4/status":
    #     print('light4')
    #     light_status(msg, strip4, 3, rgbs)

    if msg.topic == "light1/brightness":
        brightness(msg, strip1, 0, rgbs)
    if msg.topic == "light2/brightness":
        brightness(msg, strip2, 1, rgbs)
    # if msg.topic == "light3/brightness":
    #     brightness(msg, strip3, 2, rgbs)
    # if msg.topic == "light4/brightness":
    #     brightness(msg, strip4, 3, rgbs)

    if msg.topic == "light1/saturation":
        saturation(msg, strip1, 0, rgbs)
    if msg.topic == "light2/saturation":
        saturation(msg, strip2, 1, rgbs)
    # if msg.topic == "light3/saturation":
    #     saturation(msg, strip3, 2, rgbs)
    # if msg.topic == "light4/saturation":
    #     saturation(msg, strip4, 3, rgbs)

    if msg.topic == "light1/hue":
        hue(msg, strip1, 0, rgbs)
    if msg.topic == "light2/hue":
        hue(msg, strip2, 1, rgbs)

    if msg.topic == "lights/random":
        print(msg.payload)
        if msg.payload == "on":
            cycle = True
            print("cycle: ", cycle)
            t = threading.Thread(
                target=colorWipe2, args=(strip1, strip2, rgbs))
            t.start()
        else:
            cycle = False
            print("cycle: ", cycle)

    # if msg.topic == "light3/hue":
    #     hue(msg, strip3, 2, rgbs)
    # if msg.topic == "light4/hue":
    #     hue(msg, strip4, 3, rgbs)
    #TEST
    if msg.topic == "test/one":
        colorWipe(strip1, Color(0, 255, 0))
    if msg.topic == "test/two":
        colorWipe(strip2, Color(0, 255, 0))
    if msg.topic == "test/three":
        colorWipe(strip3, Color(0, 255, 0))
    if msg.topic == "test/four":
        colorWipe(strip4, Color(0, 255, 0))
    print(rgbs)


#client = mqtt.Client("", True, None, mqtt.MQTTv31)
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
#client = mqtt.Client("", True, None, mqtt.MQTTv31)
# Process network traffic and dispatch callbacks. This will also handle
# reconnecting. Check the documentation at
# https://github.com/eclipse/paho.mqtt.python
# for information on how to use other loop*() functions
client.loop_forever()
