from neopixel import *
import board
import paho.mqtt.client as mqtt
import threading
import colorsys

global rgbs
global pixels_1
global pixels_2

pixel_pin_1 = board.D18
pixel_pin_2 = board.D19
ORDER = GRB
# The number of NeoPixels
num_pixels = 16

pixels_1 = NeoPixel(
    pixel_pin_1, num_pixels, brightness=0.2, auto_write=False,
    pixel_order=ORDER
)

pixels_2 = NeoPixel(
    pixel_pin_2, num_pixels, brightness=0.2, auto_write=False,
    pixel_order=ORDER
)
rgbs = [[0, 0, 100, 255, 255, 255], [0, 0, 100, 255, 255, 255]]


def light_status(msg, strip, rgb_index, all_rgb):
    if msg.payload == "true":
        color = (all_rgb[rgb_index][3],
                 all_rgb[rgb_index][4],
                 all_rgb[rgb_index][5])
        if all_rgb[rgb_index][2] == 0:
            all_rgb[rgb_index][2] = 100
        strip.setBrightness(all_rgb[rgb_index][2])
        strip.fill(color)
        strip.show()
    else:
        all_rgb[rgb_index][2] = 0
        strip.setBrightness(all_rgb[rgb_index][2])
        strip.show()


def brightness(msg, strip, rgb_index, all_rgb):
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
    color = (all_rgb[rgb_index][4],
             all_rgb[rgb_index][3],
             all_rgb[rgb_index][5])
    strip.fill(color)


def saturation(msg, strip, rgb_index, all_rgb):
    all_rgb[rgb_index][0] = int(msg.payload) * .01
    c2 = colorsys.hls_to_rgb(all_rgb[rgb_index][1], .5, all_rgb[rgb_index][0])
    all_rgb[rgb_index][3] = int(c2[0] * 255)
    all_rgb[rgb_index][4] = int(c2[1] * 255)
    all_rgb[rgb_index][5] = int(c2[2] * 255)
    color = (all_rgb[rgb_index][4], all_rgb[rgb_index][3],
                  all_rgb[rgb_index][5])
    strip.fill(color)


def on_connect(client, userdata, flags, rc):
    # Light1
    client.subscribe("light1/#")
    # Light2
    client.subscribe("light2/#")

def on_message(client, userdata, msg):
    global rgbs
    if msg.topic == "light1/status":
        t = threading.Thread(target=light_status, args=(msg, pixels_1, 0, rgbs))
        t.start()
    if msg.topic == "light2/status":
        t = threading.Thread(target=light_status, args=(msg, pixels_2, 1, rgbs))
        t.start()

    if msg.topic == "light1/brightness":
        t = threading.Thread(target=brightness, args=(msg, pixels_1, 0, rgbs))
        t.start()
    if msg.topic == "light2/brightness":
        t = threading.Thread(target=brightness, args=(msg, pixels_2, 1, rgbs))
        t.start()

    if msg.topic == "light1/saturation":
        t = threading.Thread(target=saturation, args=(msg, pixels_1, 0, rgbs))
        t.start()
    if msg.topic == "light2/saturation":
        t = threading.Thread(target=saturation, args=(msg, pixels_2, 1, rgbs))
        t.start()

    if msg.topic == "light1/hue":
        t = threading.Thread(target=hue, args=(msg, pixels_1, 0, rgbs))
        t.start()
    if msg.topic == "light2/hue":
        t = threading.Thread(target=hue, args=(msg, pixels_2, 1, rgbs))
        t.start()


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_forever()
