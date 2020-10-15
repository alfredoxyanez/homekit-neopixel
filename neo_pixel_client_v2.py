from neopixel import *
import board
import paho.mqtt.client as mqtt
import threading
import colorsys

global rgbs
global pixels_1
global pixels_2

pixel_pin_1 = board.D12
pixel_pin_2 = board.D13
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
# [Saturation, , Brightness, G, R, B]
light_status = [0, 0, 100, 255, 255, 255]


def status(msg):
    if msg.payload == "true":
        light_status[2] = 100 if light_status[2] == 0 else light_status[2]
    else:
        light_status[2] = 0

    pixels_1.brightness = light_status[2]
    pixels_1.show()
    pixels_2.brightness = light_status[2]
    pixels_2.show()


def brightness(msg):
    bn = int(msg.payload)
    bn = int(255 * bn * .01)
    light_status[2] = bn
    pixels_1.brightness = light_status[2]
    pixels_1.show()
    pixels_2.brightness = light_status[2]
    pixels_2.show()


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
    color = (all_rgb[rgb_index][3],
             all_rgb[rgb_index][4],
             all_rgb[rgb_index][5])
    strip.fill(color)


def on_connect(client, userdata, flags, rc):
    # Light1
    client.subscribe("light1/#")

def on_message(client, userdata, msg):
    import pdb; pdb.set_trace()
    if msg.topic == "shelf/status":
        status(msg)
    if msg.topic == "shelf/brightness":
        brightness(msg)
    if msg.topic == "shelf/saturation":
        saturation(msg)
    if msg.topic == "shelf/hue":
        hue(msg)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_forever()
