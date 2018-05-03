#include <SPI.h>
#include <Wire.h>
#include <Servo.h>
#include <stdio.h>
#include <string.h>


void motor_move_to_angle(int motorid, int targetangle, int speeds,int currentpos);
void motor_sweep(int motorid, int offset, int speeds);


char tbs[600];




Servo Motors[6];
Servo myservomiddleL;  // create servo object to control a servo
Servo myservorearR;
Servo myservorearL;
Servo myservofrontL;
Servo myservofrontR;
Servo myservomiddleR;

int pos;    
int n;
int speeds=10;
int originalpos=90;
int currentpos[6];
char read_data[10];
int offset=90;
int motorid=0;
int rd;
int ndx = 0;
int current=offset;
void setup(void) 
{
#ifndef ESP8266
  while (!Serial);     // will pause Zero, Leonardo, etc until serial console opens
#endif
  Serial.begin(9600);

  myservomiddleL.attach(9);  //connect servo to pins
  myservorearR.attach(8);
  myservorearL.attach(7);
  myservofrontL.attach(6);
  myservofrontR.attach(5);
  myservomiddleR.attach(4);
  
  Motors[0] = myservomiddleL;
  Motors[1] = myservorearR;
  Motors[2] = myservorearL;
  Motors[3] = myservofrontL;
  Motors[4] = myservofrontR;
  Motors[5] = myservomiddleR;
  for (int i = 0; i < 6; i++){
  currentpos[i] = originalpos;
  }
}


void loop(void){
  
  char input;
  Serial.println('r');
  delay(20);
  while(Serial.available()>0 ){
     input = Serial.read();
     if (input == 'm'){
      //Serial.println("success");
      boolean newData = false;
        if (Serial.available() > 0){
           while(Serial.available() > 0 && newData == false){
            
              rd= Serial.read();
              if (rd != 'n'){
                read_data[ndx] = rd;
                Serial.print("the char is: ");Serial.println(read_data[ndx]);
                ndx++;
              }
              else{
                newData = true;
                ndx=0;
              }
            }
        }
        motorid = ((int) read_data[0]-48);
        Serial.print("Motor ID is:");Serial.println(motorid);
        offset = ((int)read_data[1]-48)*100 + ((int)read_data[2]-48)*10 + (int)read_data[3]-48;
        Serial.print("offset is:");Serial.println(offset);
        speeds = ((int)read_data[4]-48)*100 + ((int)read_data[5]-48)*10 + (int)read_data[6]-48;
        Serial.print("time delay is:");Serial.println(speeds);
        //motor_function(motorid,targetpos,speeds,currentpos);
      }

     
     }
             if (current != offset){
               motor_move_to_angle(motorid, offset, speeds,current);
             }
             motor_sweep(motorid,offset,speeds);
             current = offset;


}


void motor_sweep(int motorid, int offset, int speeds) {      // controlling motor to sweep
  n=speeds; // delay time period for movement of every degree
  
  //Serial.println("in motor function");
  //Serial.print("Motor ID is:");Serial.println(motorid);
  //Serial.print("offset is:");Serial.println(offset);
  //Serial.print("time delay is:");Serial.println(speeds);
  
  pos = offset;
  for (pos = offset; pos <= offset+35; pos ++) { 
      // in steps of 1 degree
      Motors[motorid].write(pos);              
      delay(n);       //   one degree / delay time n     1 degree /10ms == 100 degree / s        
  }
  for (pos = offset+35; pos >= offset-35; pos --) { 
      Motors[motorid].write(pos);              
      delay(n);                      
  }
  for (pos = offset-35; pos <= offset; pos ++) { 
      Motors[motorid].write(pos);              
      delay(n);                      
  }
  
  //Serial.print("curr postion is:");Serial.println(pos);
  //Serial.print("end of motor function ");   
}
void motor_move_to_angle(int motorid, int targetangle, int speeds,int currentpos) {      // controlling motor to specific angle.
  n=speeds; // delay time period for movement of every degree
  //Serial.print("in motor function");
  if (currentpos < targetangle){
    for (pos = currentpos; pos <= targetangle; pos ++) { 
      // in steps of 1 degree
      Motors[motorid].write(pos);              
      delay(n);             
    }
  }
  else{
      for (pos = currentpos; pos >= targetangle; pos --) { 
      Motors[motorid].write(pos);              
      delay(n);                      
  }
  }
  
  //Serial.print("end of motor function ");   
}



