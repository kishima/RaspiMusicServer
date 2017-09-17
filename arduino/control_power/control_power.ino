#include <Wire.h>

int pin_LED      = 13;
int pin_button   = 12;
int pin_shutdown = 9;
int pin_rpistat  = 8;
int pin_relay    = 3;
int i2c_slave_addr = 0x10;

void setup() {
  //I2C
  Wire.begin(i2c_slave_addr);
  Wire.onReceive(callback_i2c_receive);

  //GPIO
  pinMode(pin_LED,OUTPUT);
  pinMode(pin_button,INPUT);
  pinMode(pin_shutdown,OUTPUT);
  pinMode(pin_rpistat,INPUT);
  pinMode(pin_relay,OUTPUT);

  digitalWrite(pin_LED,LOW);
  digitalWrite(pin_shutdown,HIGH);
  digitalWrite(pin_relay,LOW);

  Serial.begin(9600);

  delay(1000);
  Serial.println("---------Gets started------------");
}

const int RPI_STAT_SHUTDOWN = 0;
const int RPI_STAT_BOOT     = 1;
const int RPI_STAT_RUNNING  = 2;
const int RPI_STAT_WAIT_SHUTDOWN  = 3;
const int RPI_STAT_UNKNOWN  = 4;
int raspi_stat = RPI_STAT_SHUTDOWN;

void turn_on(){
  digitalWrite(pin_relay,HIGH);
  digitalWrite(pin_shutdown,HIGH);
}

void turn_off(){
  digitalWrite(pin_relay,LOW);
  digitalWrite(pin_shutdown,HIGH);
}

int blink_stat = 0;
void control_LED(int count){
  switch(raspi_stat){
    case RPI_STAT_SHUTDOWN:
      digitalWrite(pin_LED,LOW);
      break;
    case RPI_STAT_BOOT:
      if(count%10==0){
        if(blink_stat==0){
          digitalWrite(pin_LED,LOW);
          blink_stat=1;
        }else{
          digitalWrite(pin_LED,HIGH);
          blink_stat=0;
        }
      }
      break;
    case RPI_STAT_RUNNING:
      digitalWrite(pin_LED,HIGH);
      break;
    case RPI_STAT_WAIT_SHUTDOWN:
      if(count%7==0){
        if(blink_stat==0){
          digitalWrite(pin_LED,LOW);
          blink_stat=1;
        }else{
          digitalWrite(pin_LED,HIGH);
          blink_stat=0;
        }
      }
      break;
    case RPI_STAT_UNKNOWN:
      if(count%5==0 && blink_stat==0){
        digitalWrite(pin_LED,LOW);
        blink_stat=1;
      }else{
        digitalWrite(pin_LED,HIGH);
        blink_stat=0;
      }
      break;
  }
}

void button_event(int press_duration){
   switch(raspi_stat){
    case RPI_STAT_SHUTDOWN:
      //Power on
      Serial.println("start turn on process");
      turn_on();
      Serial.println("*** TURN ON power ***");
      raspi_stat = RPI_STAT_BOOT;
      clear_timer();
      break;
    case RPI_STAT_BOOT:
      Serial.println("ignore");
      //button is ignored when it's booting
      break;
    case RPI_STAT_RUNNING:
      //shutdown will start when it's running
      Serial.println("start shutdown process");
      digitalWrite(pin_shutdown,LOW);
      raspi_stat = RPI_STAT_WAIT_SHUTDOWN;
      break;
    case RPI_STAT_WAIT_SHUTDOWN:
      //button is ignored when it's shutting down
      Serial.println("ignore");
      break;
    case RPI_STAT_UNKNOWN:
      //power can be off by long press when status is UNKNOWN
      if(press_duration > 20*3){ //3sec (50*20*3 msec)
        Serial.println("*** Emergency turn off ***");
        turn_off();
        digitalWrite(pin_shutdown,HIGH);
        raspi_stat = RPI_STAT_SHUTDOWN;
      }else{
        Serial.println("RPI_STAT_UNKNOWN:ignore");
      }
      break;
   }
}

void normal_task(int loop_count){
  //LED
  control_LED(loop_count);

  static int timeout_counter1=0;
  static int timeout_counter2=0;

  switch(raspi_stat){
    case RPI_STAT_SHUTDOWN:
      //check timer
      if(loop_count % 20 == 0){ check_timer(); }
      timeout_counter1=0;
      timeout_counter2=0;
      break;
    case RPI_STAT_BOOT:
      //Check RasPi's GPIO
      //GPIO is LOW: "shutdown_checker.py" gets started
      timeout_counter1++;
      if(timeout_counter1 > 20*60*2 ){//50*20 * 60 * 2 (2min)
        Serial.println("*** BOOT error ***");
        timeout_counter1=0;
        raspi_stat = RPI_STAT_UNKNOWN;
      }
      if(loop_count % 10 == 0){
        //Raspberry Pi status check
        int stat = digitalRead(pin_rpistat);
        //Serial.println(stat);
        if(stat == 0){
          Serial.println("*** TURN ON successfully ***");
          raspi_stat = RPI_STAT_RUNNING;
        }
      }
      break;
    case RPI_STAT_RUNNING:
      break;
    case RPI_STAT_WAIT_SHUTDOWN:
      static int shtdwn_delay_count=0;
      if(shtdwn_delay_count>0){
        shtdwn_delay_count++;
      }else{
        timeout_counter2++;
        if(timeout_counter2 > 20*60*2 ){//50*20 * 60 * 2 (2min)
          Serial.println("*** Shutdown error ***");
          timeout_counter2=0;
          raspi_stat = RPI_STAT_UNKNOWN;
        }
      }
      if(loop_count % 10 == 0){
        if(shtdwn_delay_count==0){
          //Raspberry Pi status check
          int stat = digitalRead(pin_rpistat);
          //Serial.println(stat);
          if(stat == 1){
            shtdwn_delay_count=1; // start couting up until power off
            Serial.println("start TURN OFF power count down");
            digitalWrite(pin_shutdown,HIGH);
          }
        }else{
          if(shtdwn_delay_count>20*30){ //50*20 * 30 msec (30sec)
            raspi_stat = RPI_STAT_SHUTDOWN;
            Serial.println("*** TURN OFF power successfully ***");
            turn_off();
            shtdwn_delay_count=0;
          }
        }
      }
      break;
    case RPI_STAT_UNKNOWN:
      //do nothing
      break;
   }
}


const int  CMD_SET_WAKUP_TIMER01    = 0x11;
const int  CMD_SET_WAKUP_TIMER02    = 0x12;
const int  CMD_CLEAR_TIMER          = 0x40;
const int  CMD_SHUTDOWN_NOW         = 0xFF;

unsigned long raspy_timer[] = {0,0}; 

void clear_timer(){
      raspy_timer[0]=0;
      raspy_timer[1]=0;
}

void wakeup_by_timer(){
      Serial.println("start turn on process by timer");
      turn_on();
      Serial.println("*** TURN ON power ***");
      raspi_stat = RPI_STAT_BOOT;
      clear_timer();
}

void check_timer(){
  unsigned long now = millis();
  if(raspy_timer[0] > 0 && now > raspy_timer[0]){
      Serial.println("Timer1 ignition");
      wakeup_by_timer();
  }
  if(raspy_timer[1] > 0 && now > raspy_timer[1]){
      Serial.println("Timer2 ignition");
      wakeup_by_timer();
  }
}

void callback_i2c_receive(int length){
  unsigned long now = millis();
  int cmd = Wire.read();
  int data_len = Wire.read();
  Serial.print("cmd = ");
  Serial.println(cmd);
  Serial.print("data_len = ");
  Serial.println(data_len);
  unsigned long data=0;
  if(data_len==4){
    int count=3;
    while (0 < Wire.available()) {
      int d = Wire.read();
      data += d << (8*count);
      count -= 1;
    }
    Serial.print("\ndata=");
    Serial.println(data);
  }
  
  switch(cmd){
    case CMD_SET_WAKUP_TIMER01:
      Serial.println("CMD_SET_WAKUP_TIMER01");
      raspy_timer[0]=millis()+data*1000 + now;
      break;
    case CMD_SET_WAKUP_TIMER02:
      Serial.println("CMD_SET_WAKUP_TIMER02");
      raspy_timer[1]=millis()+data*1000 + now;
      break;
    case CMD_CLEAR_TIMER:
      Serial.println("CMD_CLEAR_TIMER");
      clear_timer();
      break;
    case CMD_SHUTDOWN_NOW:
      Serial.println("CMD_SHUTDOWN_NOW");
      if(raspi_stat == RPI_STAT_RUNNING){ 
        Serial.println("shutdown request from Raspi");
        digitalWrite(pin_shutdown,LOW);
        raspi_stat = RPI_STAT_WAIT_SHUTDOWN;
      }
      break;
  }
  
}


//************************************************************
void loop() {
  static int press_duration=0;
  static int loop_count = 0;
  static int button_stat = 1; // 0:pressed 1:not pressed

  delay(50);
  loop_count++;
  if(loop_count>=30000){
    loop_count = 0;
  }

  //button
  int button_press = 0;
  int new_button_stat = digitalRead(pin_button);
  if(button_stat==0 && new_button_stat==0){
    press_duration++;
  }
  if(new_button_stat != button_stat){
    //Serial.println(new_button_stat);
  }
  if(new_button_stat != button_stat && button_stat == 0){
    Serial.print("button released > press_duration = ");
    Serial.println(press_duration);
    button_press = 1;
  }
  button_stat = new_button_stat;

  //button event
  if(button_press==1){
    button_event(press_duration);
  }

  if(new_button_stat==1){
    press_duration=0;
  }

  //normal task
  normal_task(loop_count);

}

