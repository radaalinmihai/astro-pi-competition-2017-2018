#!usr/bin/python3
from sense_hat import SenseHat
from time import sleep
from picamera import PiCamera
from picamera import Color
import time
import ephem
import math
from math import sqrt
import os

cam = PiCamera()
sense = SenseHat()

cam.resolution = (2592, 1944)

name = "ISS (ZARYA)"             
line1 = "1 25544U 98067A   18015.76213144  .00002375  00000-0  42846-4 0  9998"
line2 = "2 25544  51.6430  58.5835 0003578  19.8447  92.3735 15.54313934 94810"


iss = ephem.readtle(name, line1, line2)
sun = ephem.Sun()
twilight = math.radians(-6)

r = (255,0,0)
w = (0,0,0)
g = (0, 255, 0)

happy_face = [
    w,w,g,g,g,g,w,w,
    w,g,w,w,w,w,g,w,
    g,w,g,w,w,g,w,g,
    g,w,w,w,w,w,w,g,
    g,w,g,w,w,g,w,g,
    g,w,w,g,g,w,w,g,
    w,g,w,w,w,w,g,w,
    w,w,g,g,g,g,w,w
    ]

sad_face = [
    w,w,r,r,r,r,w,w,
    w,r,w,w,w,w,r,w,
    r,w,r,w,w,r,w,r,
    r,w,w,w,w,w,w,r,
    r,w,w,r,r,w,w,r,
    r,w,r,w,w,r,w,r,
    w,r,w,w,w,w,r,w,
    w,w,r,r,r,r,w,w
    ]

start = 0

while True:
    def cpu_temp():
        res = os.popen("vcgencmd measure_temp").readline()
        return(res.replace("temp=","").replace("'C\n",""))
    
    temp = sense.get_temperature()
    humidity = sense.get_humidity()
    pressure = sense.get_pressure()

    real_temp = temp - (float(cpu_temp()) - temp) / 2
    real_humidity = humidity + (float(cpu_temp()) - temp)

    real_temp = round(real_temp, 2)
    real_humidity = round(real_humidity, 2)
    pressure = round(pressure, 2)
    
    iss.compute()
    
    obs = ephem.Observer()
    obs.lat = iss.sublat
    obs.long = iss.sublong
    obs.elevation = 0
    
    sun.compute(obs)
    sun_angle = math.degrees(sun.alt)
    day_night = "Day" if sun_angle > twilight else "Night"
    
    date = time.strftime("%H-%M-%S")
    
    cam.annotate_text_size = 120
    cam.annotate_foreground = Color("White")
    cam.annotate_background = Color("Black")
    cam.annotate_text = "Lat: %s - Long: %s - %s" % (iss.sublat, iss.sublong, day_night)
    
    if start >= 54:
        cam.capture(date + ".jpg")
        print(date + ".jpg")

    print(start)

    if real_temp < 26.7 or real_temp > 18.3 or real_humidity < 70 or real_humidity > 40:
        sense.set_pixels(happy_face)
        
    if real_temp > 26.7 or real_temp < 18.3 or real_humidity > 70 or real_humidity < 40:
        sense.set_pixels(sad_face)

    acceleration = sense.get_accelerometer_raw()

    AcX = acceleration["x"]
    AcY = acceleration["y"]
    AcZ = acceleration["z"]

    gyroscope = sense.get_gyroscope_raw()

    GyX = gyroscope["x"]
    GyY = gyroscope["y"]
    GyZ = gyroscope["z"]

    if start == 54:
        start = 0


    magnetometer = sense.get_compass_raw()

    MaX = magnetometer["x"]
    MaY = magnetometer["y"]
    MaZ = magnetometer["z"]

    magnetometer_equation = sqrt(MaX * MaX + MaY * MaY + MaZ * MaZ)

    with open("date.csv", "a") as file:
        file.write(date)
        file.write(", ")
        file.write(str(real_temp))
        file.write(", ")
        file.write(str(real_humidity))
        file.write(", ")
        file.write(str(pressure))
        file.write(", ")
        file.write(str(AcX))
        file.write(", ")
        file.write(str(AcY))
        file.write(", ")
        file.write(str(AcZ))
        file.write(", ")
        file.write(str(GyX))
        file.write(", ")
        file.write(str(GyY))
        file.write(", ")
        file.write(str(GyZ))
        file.write(", ")
        file.write(str(MaX))
        file.write(", ")
        file.write(str(MaY))
        file.write(", ")
        file.write(str(MaZ))
        file.write(", ")
        file.write(str(magnetometer_equation))
        file.write("\n")
    start = start + 1
    sleep(1)
