#include <SPI.h>
#include <Wire.h>
#include <Servo.h>
#include <stdio.h>
#include <string.h>


void motor_move_to_angle(int motorid, int roll_targetangle,int pitch_targetangle, int speeds,int roll_currentpos, int pitch_currentpos);
void motor_sweep(int motorid, int roll_offset,int pitch_offset, int speeds, int dir);
void serialEvent();

char tbs[500];




Servo Motors[6];
Servo myservomiddleL;  // create servo object to control a servo
Servo myservorearR;
Servo myservorearL;
Servo myservofrontL;
Servo myservofrontR;
Servo myservomiddleR;
  
int n;
int pos;
int speeds=10;
int originalpos=90;
int currentpos[6];
char read_data[15];
int offset=90;
int motorid=0;
int rd;
int ndx = 0;
int roll_current=offset-35;
int pitch_current=offset-35;
boolean newData = false;
char input;
char wasted_data;
int input_count=0;
int dir=0;
int roll_offset = offset;
int pitch_offset = offset;
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

  while (Serial.available() > 11 && input_count < 33){
    wasted_data = Serial.read();
    input_count++;
  }
  input_count=0;
  
  Serial.print(Serial.available());
  while(Serial.available() && !newData ){
     
     input = (char)Serial.read();
      //Serial.println("success");
     read_data[ndx] = input;
     //Serial.print("the char is: ");Serial.println(read_data[ndx]);
     ndx++;
          
     if (input == 'n'){
       if (ndx== 10){
        newData = true;
       }
       else{
        newData = false;
        ndx = 0;
       }
     }
     if (ndx==11 && !newData){
       ndx = 0;
     }
     if(newData == true){
        motorid = ((int) read_data[0]-48);
        //Serial.print("Motor ID is:");Serial.println(motorid);
        roll_offset = ((int)read_data[1]-48)*100 + ((int)read_data[2]-48)*10 + (int)read_data[3]-48;
        Serial.print("offset is:");Serial.println(offset);
        pitch_offset = ((int)read_data[4]-48)*100 + ((int)read_data[5]-48)*10 + (int)read_data[6]-48;
        //Serial.print("time delay is:");Serial.println(speeds);
        //motor_function(motorid,targetpos,speeds,currentpos);
	speeds = ((int)read_data[7]-48)*100 + ((int)read_data[8]-48)*10 + (int)read_data[9]-48;
        ndx = 0;
        Serial.flush();
     }
  }

     
     
    if (roll_current != roll_offset-35 || pitch_current != pitch_offset - 35){
        motor_move_to_angle(motorid, roll_offset-35,pitch_offset-35, speeds,roll_current, pitch_current);
    }
    motor_sweep(motorid,roll_offset,pitch_offset, speeds,dir);
    newData = false;
    
    

    	
    roll_current = roll_offset-35;
    pitch_current = pitch_offset-35;

}



void motor_sweep(int motorid, int roll_offset,int pitch_offset, int speeds, int dir) {      // controlling motor to sweep
  n=speeds; // delay time period for movement of every degree
  
  //Serial.println("in motor function");
  //Serial.print("Motor ID is:");Serial.println(motorid);
  //Serial.print("offset is:");Serial.println(offset);
  //Serial.print("time delay is:");Serial.println(speeds);
  
 int roll_pos = roll_offset;
 // if (dir == 1){
  for (int i = -35; i <= 35; i ++) { 
      // in steps of 1 degree
      Motors[5].write(roll_pos + i);
      Motors[0].write((roll_pos + i));
      //Motors[5].write(pos);      
      delay(n);       //   one degree / delay time n     1 degree /10ms == 100 degree / s        
  }
  for (int i = 35; i >= -35; i --) { 
      Motors[5].write(roll_pos + i);
      Motors[0].write( (roll_pos + i));
      //Motors[5].write(pos);
      delay(n);                      
  }
/*
  for (pos = offset-35; pos <= offset; pos ++) { 
      Motors[0].write(pos);
      Motors[4].write(pos);
      Motors[5].write(pos);
      delay(n);                      
  }
*/
// }
/*
 else{
   for (pos = offset; pos >= offset-35; pos --) {
      // in steps of 1 degree
      Motors[0].write(pos);
      Motors[4].write(pos);
      Motors[5].write(pos);
      delay(n);       //   one degree / delay time n     1 degree /10ms == 100 degree / s        
  }
  for (pos = offset-35; pos <= offset+35; pos ++) {
      Motors[0].write(pos);
      Motors[4].write(pos);
      Motors[5].write(pos);
      delay(n);
  }
  for (pos = offset+35; pos >= offset; pos --) {
      Motors[0].write(pos);
      Motors[4].write(pos);
      Motors[5].write(pos);
      delay(n);
  }
 }
  */
  //Serial.print("curr postion is:");Serial.println(pos);
  //Serial.print("end of motor function ");   
}

void motor_move_to_angle(int motorid, int roll_targetangle,int pitch_targetangle, int speeds,int roll_currentpos,int pitch_currentpos) {      // controlling motor to specific angle.
  n=speeds; // delay time period for movement of every degree
  //Serial.print("in motor function");
  if (roll_currentpos < roll_targetangle || pitch_currentpos < pitch_targetangle){
    for (pos = roll_currentpos+1; pos <= roll_targetangle; pos ++) { 
      // in steps of 1 degree
      Motors[0].write( pos);
      //Motors[4].write(pos);
      Motors[5].write(pos);
      delay(n);             
    }
  }
  else if(roll_currentpos > roll_targetangle || pitch_currentpos > pitch_targetangle){
      for (pos = roll_currentpos-1; pos >= roll_targetangle; pos --) { 
      Motors[0].write( pos);
      //Motors[4].write(pos);
      Motors[5].write(pos);
      delay(n);
      
  }
  }
  
  //Serial.print("end of motor function ");   
}



