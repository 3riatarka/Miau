#!/usr/bin/env python3

import requests, argparse, json

# Change your elGato Light Strip IP address here:
ip = ""

class Lights:
    hue = -1
    saturation = -1
    brightness = -1
    status = -1
    endpoint = ""

    def __init__(self, endpoint):
        self.endpoint = endpoint
        try:
            r = requests.get(endpoint)
            if r.status_code != 200:
                raise Exception()
        except Exception as ex:
            print(f"Light strip on %s unreachable\n\n%s" % (endpoint, ex))
            exit(1)
        data = json.loads(r.content)
        self.hue = round(data['lights'][0]['hue'])
        self.saturation = round(data['lights'][0]['saturation'])
        self.brightness = round(data['lights'][0]['brightness'])
        self.status = data['lights'][0]['on']

    def show(self):
        print(">>> Status of elGato Light Strip on %s\n\tHue: %d\n\tSaturation: %d%%\n\tBrightness: %d%%\t" % (self.endpoint, self.hue, self.saturation, self.brightness))
        if self.status:
            print("\tStatus: on")
        else:
            print("\tStatus: off")


    def switch(self):
        if self.status:
            self.status = 0
        else:
            self.status = 1
        try:
            r = requests.put(self.endpoint, json={"lights":[{"on":self.status}], "numberOfLights":1})
        except Exception as ex:
            print(">>> Unable to switch the light strip: %s" % ex)

    def update(self, hue, sat, bri):
        if hue != -1:
            self.hue = round(hue)
        if sat != -1:
            self.saturation = sat
        if bri != -1:
            self.brightness = bri
        try:
            r = requests.put(self.endpoint, json={"lights":[{"hue":self.hue,"saturation":self.saturation}],"numberOfLights":1})
            r2 = requests.put(self.endpoint, json={"lights":[{"brightness":self.brightness}], "numberOfLights":1})
        except Exception as ex:
            print(">>> Error updating the light strip: %s" % ex)
            exit(1)

parser = argparse.ArgumentParser(description="Simple elGato Light Strip client for linux CLI")
parser.add_argument('-c', '--color', type=int, nargs='?', default=-1, help="Hue formatted as an integer from 0 to 350")
parser.add_argument('-s', '--saturation', type=int, nargs='?', default=-1, help="Color saturation percentage")
parser.add_argument('-b', '--brightness', type=int, nargs='?', default=-1, help="Brightness percentage")
parser.add_argument('--show', action='store_const', const=1, help="Print current values")
parser.add_argument('--switch', action='store_const', const=1, help="Switch the device on or off")

options = parser.parse_args()

gato = Lights('http://%s:9123/elgato/lights' % ip)

if options.switch:
    gato.switch()
if options.show:
    gato.show()
    exit(0)

# Data validation:
if options.color < -1 or options.color > 350:
    print(">>> ERROR: Color out of range. Select a value between 0 - 350")
    exit(1)
if options.saturation < -1 or options.saturation > 100:
    print(">>> ERROR: Saturation out of range. Select a value between 0 - 100")
    exit(1)
if options.brightness < -1 or options.brightness > 100:
    print(">>> ERROR: Brightness out of range. Select a value between 0 - 100")
    exit(1)

gato.update(options.color, options.saturation, options.brightness)
