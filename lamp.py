#!/usr/bin/env python3

import requests, math
import time
import sys

lamp="esp_f39a78"
#norm=(100,21,33)
norm=(100,68,29)

def convertData(data):
    #cp=dict(data)
    #data['r'] = cp['b']
    #data['g'] = cp['r']
    #data['b'] = cp['g']
    print(int(data[2]),int(data[0]),int(data[1]))
    return {'r':int(data[2]),'g':int(data[0]),'b':int(data[1]),'p':1023}
    #return {'r':int(data[2]*1023/255),'g':int(data[0]*1023/255),'b':int(data[1]*1023/255),'p':1023}

def send(data,host="192.168.10.48"):
    host = "http://"+host+"/leds"
    print(host)
    try:
        r = requests.post(host,data=data)
        
        # FIXME convert needed for readability
        cp=dict(data)
        data['r'] = cp['g']
        data['g'] = cp['b']
        data['b'] = cp['r']
        t = r.text.split(" ")
        print(data, " |||  ", t[0], t[1], t[3].replace("g","r"), t[4].replace("b","g"), t[2].replace("r","b"), t[5])

        #print(data, " |||  ", t.text)
    except requests.exceptions.ConnectionError:
        print("Lamp not available: No route to host")

def hsv2rgb(h, s, v):
    h = float(h)
    s = float(s/1023)
    v = float(v/1023)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    r, g, b = int(r * 1023), int(g * 1023), int(b * 1023)
    return r, g, b

def normalize(h,s,v):
    r,g,b = hsv2rgb(h,s,1023)
    r,g,b = r*norm[0]/100, g*norm[1]/100, b*norm[2]/100
    M = max(r,g,b)
    mult = v / M
    return (r*mult,g*mult,b*mult)

if __name__ == '__main__':  
    if len(sys.argv) == 1:
        data=[240,1023,1023]
        while True:
            data[0]=(data[0]+1)%360
            d=normalize(*data)
            send(convertData(d))
            time.sleep(0.4)
    if len(sys.argv) == 2:
        if sys.argv[1] == "on":
            data=normalize(0,0,1023)
        elif sys.argv[1] == "off":
            data=normalize(0,0,0)
        else:
            data=normalize(float(sys.argv[1]),1023,1023)
    if len(sys.argv) == 3:
        data=normalize(float(sys.argv[1]),int(float(sys.argv[2])*10.23),1023)
    if len(sys.argv) == 4:
        data=normalize(float(sys.argv[1]),int(float(sys.argv[2])*10.23),int(float(sys.argv[3])*10.23))
    if len(sys.argv) > 4:
        print("too many parameters")
        sys.exit(1)
  
    send(convertData(data),lamp)
