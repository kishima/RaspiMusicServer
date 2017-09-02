
int pin_LED      = 13;
int pin_button   = 12;
int pin_shutdown = 9;
int pin_rpistat  = 8;
int pin_relay    = 3;

void setup() {
  // put your setup code here, to run once:
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
      //電源ON
      Serial.println("start turn on process");
      turn_on();
      Serial.println("*** TURN ON power ***");
      raspi_stat = RPI_STAT_BOOT;
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
      //do nothing
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
          if(shtdwn_delay_count>20*50){ //50*20 * 50 msec (50sec)
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

