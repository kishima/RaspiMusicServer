# RaspiMusicServer

This an music server on Raspeberry pi with Grovepi and Arduino.
The server plays music by mpc and can be controlled by either a joystick, a button or gesture. Audio volume can be changed by a slide bar.
Power supply is managed by Arduino with a button safely. We don't need to take care of timing of turning on/off Raspi.

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
- Heat sink and 5V fan for RasPi CPU
- GrovePi
  - https://www.dexterindustries.com/grovepi/
- Grove - LCD RGB Backlight
  - http://wiki.seeed.cc/Grove-LCD_RGB_Backlight/
- Grove - Button
  - http://wiki.seeed.cc/Grove-Button/
- Grove - Slide Potentiometer
  - http://wiki.seeed.cc/Grove-Slide_Potentiometer/
- Grove - Thumb Joystick
  - http://wiki.seeed.cc/Grove-Thumb_Joystick/
- Grove - Gesture V1.0
  - http://wiki.seeed.cc/Grove-Gesture_v1.0/
- Motion detection sensor
  - https://www.amazon.co.jp/dp/B00HG82S9U/ref=cm_sw_r_tw_dp_x_tRURzb390VVFQ

## Software

### Arduino

Arduino controls power supply of Raspberry pi.
arduino/control_power.ino shall be loaded into Arduino.

### Raspberry pi

1. Communication with Arduino
"shutdown_check/shutdown_check.py" shall be run from /etc/rc.local by super user.

2. Install mpd/mpc

3. Set a playlist as you want

4. Music server application
"audioserver/run.sh" shall be from cron by pi user.

5. Connect either a speaker or a DAC. 
I connected a USB DAC.
http://akizukidenshi.com/catalog/g/gK-05369/

## Notification

- Power of the system is supplied by 5V DC. Maximum current should not be less than 2.5A since it will be applied for RasPi3, Arduino and peripherals.


## Schematic

Following is schematic of the server.

![Schematic](https://github.com/kishima/RaspiMusicServer/blob/master/schematic.PNG)

## License

This software is released under the MIT License, see LICENSE.

"grove_gesture_sensor.py" is
Copyright (C) 2017  Dexter Industries
