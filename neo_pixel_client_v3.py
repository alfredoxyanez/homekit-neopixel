
import time
import colorsys
import paho.mqtt.client as mqtt
from rpi_ws281x import ws, Color, Adafruit_NeoPixel

# LED strip configuration:
LED_COUNT = 16  # Number of LED pixels.
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_CHANNEL2 = 1  # set to '1' for GPIOs 13, 19, 41, 45 or 53

# [Saturation, Hue, Brightness (1,100), R, G, B]
light_status = [0, 0, 50, 255, 255, 255]

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    global strip_odd
    global strip_even

    strip_odd = Adafruit_NeoPixel(LED_COUNT, 12, LED_FREQ_HZ, LED_DMA,
                                  LED_INVERT, LED_BRIGHTNESS, 0)
    strip_even = Adafruit_NeoPixel(LED_COUNT, 13, LED_FREQ_HZ, LED_DMA,
                                   LED_INVERT, LED_BRIGHTNESS, 1)
    strip_odd.begin()
    strip_even.begin()

    client.subscribe("shelf/#")

def colorWipeNoShow(strip, color):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)

def colorWipe(strip, color):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

def status(msg):
    payload = msg.payload.decode("utf-8")
    if payload == 'true':
        light_status[2] = 255 if light_status[2] == 0 else light_status[2]
        if (strip_odd.getPixelColorRGB(0).r == 0 and
                strip_odd.getPixelColorRGB(0).g == 0 and
                strip_odd.getPixelColorRGB(0).b == 0):
            strip_odd.setBrightness(light_status[2])
            color = Color(light_status[3],
                          light_status[4],
                          light_status[5])
            colorWipeNoShow(strip_odd, color)
            colorWipeNoShow(strip_even, color)
    else:
        light_status[2] = 0

    strip_odd.setBrightness(light_status[2])
    strip_even.setBrightness(light_status[2])
    strip_odd.show()
    strip_even.show()

def brightness(msg):
    bn = int(msg.payload)
    bn = int(255 * bn * .01)
    light_status[2] = bn
    strip_odd.setBrightness(light_status[2])
    strip_even.setBrightness(light_status[2])
    strip_odd.show()
    strip_even.show()


def hue(msg):
    light_status[1] = int(msg.payload) / 360.0
    c = colorsys.hls_to_rgb(light_status[1], .5, light_status[0])
    light_status[3] = int(c[0] * 255)  # R
    light_status[4] = int(c[1] * 255)  # G
    light_status[5] = int(c[2] * 255)  # B
    color = Color(light_status[3],
                  light_status[4],
                  light_status[5])
    colorWipe(strip_odd, color)
    colorWipe(strip_even, color)


def saturation(msg):
    light_status[0] = int(msg.payload) * .01
    c = colorsys.hls_to_rgb(light_status[1], .5, light_status[0])
    light_status[3] = int(c[0] * 255)
    light_status[4] = int(c[1] * 255)
    light_status[5] = int(c[2] * 255)
    color = Color(light_status[3],
                  light_status[4],
                  light_status[5])
    colorWipe(strip_odd, color)
    colorWipe(strip_even, color)


def on_message(client, userdata, msg):
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