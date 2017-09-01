# RaspiMusicServer
This an music server on Raspeberry pi with Grovepi and Arduino.

![Schematic](https://github.com/kishima/RaspiMusicServer/blob/master/Picture_surface.jpg)
![Schematic](https://github.com/kishima/RaspiMusicServer/blob/master/Picture_in_Box.jpg)

## Materials

- Raspberry Pi3
- Arduino uno
- Pololu Basic SPDT Relay Carrier with 5VDC Relay (Partial Kit)
  - https://www.pololu.com/product/2481
- SparkFun Logic Level Converter - Bi-Directional
  - https://www.sparkfun.com/products/12009
- Cables

- GrovePi
  - https://www.dexterindustries.com/grovepi/
- Grove - LCD RGB Backlight
  - http://wiki.seeed.cc/Grove-LCD_RGB_Backlight/
- Grove - Button
  - http://wiki.seeed.cc/Grove-Button/
- Grove - Slide Potentiometer
  - http://wiki.seeed.cc/Grove-Slide_Potentiometer/

## Software

### Arduino

Arduino controls power supply of Raspberry pi.
arduino/control_power.ino shall be loaded into Arduino.

### Raspberry pi

1. Communication with Arduino
"shutdown_check/shutdown_check.py" shall be run from /etc/rc.local by super user.

2. Music server application
"audioserver/run.sh" shall be from cron by pi user.

## Notification

- Power of the system is supplied by 5V DC. Maximum current should not be less than 2.5A since it will be applied for RasPi3, Arduino and peripherals.


## Schematic

Following is schematic of the server.

![Schematic](https://github.com/kishima/RaspiMusicServer/blob/master/schematic.PNG)

