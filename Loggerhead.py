import serial
import time
import math
import sys
import time
import math
import IMU
import datetime
import os
import PID
from PID import *

ser = serial.Serial('/dev/ttyACM2',9600)
count=0

offset = 90
speed = 10
rolls=[0]*5
pitchs=[0]*5
IMU_upside_down = 0     # Change calculations depending on IMu orientation. 
                                                # 0 = Correct side up. This is when the skull logo is facing down
                                                # 1 = Upside down. This is when the skull logo is facing up 
                                                
                                                
RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070          # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
AA =  0.40              # Complementary filter constant
MAG_LPF_FACTOR = 0.4    # Low pass filter constant magnetometer
ACC_LPF_FACTOR = 0.4    # Low pass filter constant for accelerometer
ACC_MEDIANTABLESIZE = 9         # Median filter table size for accelerometer. Higher = smoother but a longer delay
MAG_MEDIANTABLESIZE = 9         # Median filter table size for magnetometer. Higher = smoother but a longer delay

#Kalman filter variables
Q_angle = 0.02
Q_gyro = 0.0015
R_angle = 0.005
y_bias = 0.0
x_bias = 0.0
XP_00 = 0.0
XP_01 = 0.0
XP_10 = 0.0
XP_11 = 0.0
YP_00 = 0.0
YP_01 = 0.0
YP_10 = 0.0
YP_11 = 0.0
KFangleX = 0.0
KFangleY = 0.0
gyroXangle = 0.0
gyroYangle = 0.0
gyroZangle = 0.0
CFangleX = 0.0
CFangleY = 0.0
CFangleXFiltered = 0.0
CFangleYFiltered = 0.0
kalmanX = 0.0
kalmanY = 0.0
oldXMagRawValue = 0
oldYMagRawValue = 0
oldZMagRawValue = 0
oldXAccRawValue = 0
oldYAccRawValue = 0
oldZAccRawValue = 0

a = datetime.datetime.now()



#Setup the tables for the mdeian filter. Fill them all with '1' soe we dont get devide by zero error 
acc_medianTable1X = [1] * ACC_MEDIANTABLESIZE
acc_medianTable1Y = [1] * ACC_MEDIANTABLESIZE
acc_medianTable1Z = [1] * ACC_MEDIANTABLESIZE
acc_medianTable2X = [1] * ACC_MEDIANTABLESIZE
acc_medianTable2Y = [1] * ACC_MEDIANTABLESIZE
acc_medianTable2Z = [1] * ACC_MEDIANTABLESIZE
mag_medianTable1X = [1] * MAG_MEDIANTABLESIZE
mag_medianTable1Y = [1] * MAG_MEDIANTABLESIZE
mag_medianTable1Z = [1] * MAG_MEDIANTABLESIZE
mag_medianTable2X = [1] * MAG_MEDIANTABLESIZE
mag_medianTable2Y = [1] * MAG_MEDIANTABLESIZE
mag_medianTable2Z = [1] * MAG_MEDIANTABLESIZE

IMU.detectIMU()     #Detect if BerryIMUv1 or BerryIMUv2 is connected.
IMU.initIMU()       #Initialise the accelerometer, gyroscope and compass


while True:

        #Read the accelerometer,gyroscope and magnetometer values
        ACCx = IMU.readACCx()
        ACCy = IMU.readACCy()
        ACCz = IMU.readACCz()
        GYRx = IMU.readGYRx()
        GYRy = IMU.readGYRy()
        GYRz = IMU.readGYRz()
        MAGx = IMU.readMAGx()
        MAGy = IMU.readMAGy()
        MAGz = IMU.readMAGz()
        
        ##Calculate loop Period(LP). How long between Gyro Reads
        b = datetime.datetime.now() - a
        a = datetime.datetime.now()
        LP = b.microseconds/(1000000*1.0)
        #print "Loop Time | %5.2f|" % ( LP ),
        
        
        
        ############################################### 
        #### Apply low pass filter ####
        ###############################################
        MAGx =  MAGx  * MAG_LPF_FACTOR + oldXMagRawValue*(1 - MAG_LPF_FACTOR);
        MAGy =  MAGy  * MAG_LPF_FACTOR + oldYMagRawValue*(1 - MAG_LPF_FACTOR);
        MAGz =  MAGz  * MAG_LPF_FACTOR + oldZMagRawValue*(1 - MAG_LPF_FACTOR);
        ACCx =  ACCx  * ACC_LPF_FACTOR + oldXAccRawValue*(1 - ACC_LPF_FACTOR);
        ACCy =  ACCy  * ACC_LPF_FACTOR + oldYAccRawValue*(1 - ACC_LPF_FACTOR);
        ACCz =  ACCz  * ACC_LPF_FACTOR + oldZAccRawValue*(1 - ACC_LPF_FACTOR);

        oldXMagRawValue = MAGx
        oldYMagRawValue = MAGy
        oldZMagRawValue = MAGz
        oldXAccRawValue = ACCx
        oldYAccRawValue = ACCy
        oldZAccRawValue = ACCz

        ######################################### 
        #### Median filter for accelerometer ####
        #########################################
        # cycle the table
        for x in range (ACC_MEDIANTABLESIZE-1,0,-1 ):
                acc_medianTable1X[x] = acc_medianTable1X[x-1]
                acc_medianTable1Y[x] = acc_medianTable1Y[x-1]
                acc_medianTable1Z[x] = acc_medianTable1Z[x-1]

        # Insert the lates values
        acc_medianTable1X[0] = ACCx
        acc_medianTable1Y[0] = ACCy
        acc_medianTable1Z[0] = ACCz     

        # Copy the tables
        acc_medianTable2X = acc_medianTable1X[:]
        acc_medianTable2Y = acc_medianTable1Y[:]
        acc_medianTable2Z = acc_medianTable1Z[:]

        # Sort table 2
        acc_medianTable2X.sort()
        acc_medianTable2Y.sort()
        acc_medianTable2Z.sort()

        # The middle value is the value we are interested in
        ACCx = acc_medianTable2X[ACC_MEDIANTABLESIZE/2];
        ACCy = acc_medianTable2Y[ACC_MEDIANTABLESIZE/2];
        ACCz = acc_medianTable2Z[ACC_MEDIANTABLESIZE/2];



        ######################################### 
        #### Median filter for magnetometer ####
        #########################################
        # cycle the table
        for x in range (MAG_MEDIANTABLESIZE-1,0,-1 ):
                mag_medianTable1X[x] = mag_medianTable1X[x-1]
                mag_medianTable1Y[x] = mag_medianTable1Y[x-1]
                mag_medianTable1Z[x] = mag_medianTable1Z[x-1]

        # Insert the latest values      
        mag_medianTable1X[0] = MAGx
        mag_medianTable1Y[0] = MAGy
        mag_medianTable1Z[0] = MAGz     

        # Copy the tables
        mag_medianTable2X = mag_medianTable1X[:]
        mag_medianTable2Y = mag_medianTable1Y[:]
        mag_medianTable2Z = mag_medianTable1Z[:]

        # Sort table 2
        mag_medianTable2X.sort()
        mag_medianTable2Y.sort()
        mag_medianTable2Z.sort()

        # The middle value is the value we are interested in
        MAGx = mag_medianTable2X[MAG_MEDIANTABLESIZE/2];
        MAGy = mag_medianTable2Y[MAG_MEDIANTABLESIZE/2];
        MAGz = mag_medianTable2Z[MAG_MEDIANTABLESIZE/2];



        #Convert Gyro raw to degrees per second
        rate_gyr_x =  GYRx * G_GAIN
        rate_gyr_y =  GYRy * G_GAIN
        rate_gyr_z =  GYRz * G_GAIN


        #Calculate the angles from the gyro. 
        gyroXangle+=rate_gyr_x*LP
        gyroYangle+=rate_gyr_y*LP
        gyroZangle+=rate_gyr_z*LP


        ##Convert Accelerometer values to degrees
        AccXangle =  (math.atan2(ACCy,ACCz)+M_PI)*RAD_TO_DEG
        AccYangle =  (math.atan2(ACCz,ACCx)+M_PI)*RAD_TO_DEG




        # Change the rotation value of the accelerometer to -/+ 180 and move the Y axis '0' point to up
        # Two different pieces of code are used depending on how your IMU is mounted
        if IMU_upside_down :            # If IMU is upside down E.g Skull logo is facing up.
                if AccXangle >180:
                        AccXangle -= 360.0
                        AccYangle-=90
                if AccYangle >180:
                        AccYangle -= 360.0

        else :                                          # If IMU is up the correct way E.g Skull logo is facing down.
                AccXangle -= 180.0
                if AccYangle > 90:
                        AccYangle -= 270.0
                else:
                        AccYangle += 90.0



        #Complementary filter used to combine the accelerometer and gyro values.
        CFangleX=AA*(CFangleX+rate_gyr_x*LP) +(1 - AA) * AccXangle
        CFangleY=AA*(CFangleY+rate_gyr_y*LP) +(1 - AA) * AccYangle
        index = count % 5
        rolls.insert(index,CFangleX) 
        pitchs.insert(index,CFangleY)
        count = count + 1




        if IMU_upside_down : 
                MAGy = -MAGy

        #Calculate heading
        heading = 180 * math.atan2(MAGy,MAGx)/M_PI

        #Only have our heading between 0 and 360
        if heading < 0:
                heading += 360




        #Normalize accelerometer raw values.
        accXnorm = ACCx/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
        accYnorm = ACCy/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)


        #Calculate pitch and roll
        if IMU_upside_down :
                accXnorm = -accXnorm                            #flip Xnorm as the IMU is upside down
                accYnorm = -accYnorm                            #flip Ynorm as the IMU is upside down
                pitch = math.asin(accXnorm)
                roll = math.asin(accYnorm/math.cos(pitch))
        else :
                pitch = math.asin(accXnorm)
                roll = -math.asin(accYnorm/math.cos(pitch))


        #Calculate the new tilt compensated values
        magXcomp = MAGx*math.cos(pitch)+MAGz*math.sin(pitch)
        magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)-MAGz*math.sin(roll)*math.cos(pitch)

        #Calculate tilt compensated heading
        tiltCompensatedHeading = 180 * math.atan2(magYcomp,magXcomp)/M_PI
        
        #Only have our heading between 0 and 360
        if tiltCompensatedHeading < 0:
                tiltCompensatedHeading += 360





        #if 0:                  #Change to '0' to stop showing the angles from the accelerometer
                #print ("\033[1;34;40mACCX Angle %5.2f ACCY Angle %5.2f  \033[0m  " % (AccXangle, AccYangle)),

        #if 0:                  #Change to '0' to stop  showing the angles from the gyro
                #print ("\033[1;31;40m\tGRYX Angle %5.2f  GYRY Angle %5.2f  GYRZ Angle %5.2f" % (gyroXangle,gyroYangle,gyroZangle)),

        #if 0:                  #Change to '0' to stop  showing the angles from the complementary filter
        #print ("   \tCFangleX Angle %5.2f \033[1;36;40m  CFangleY Angle %5.2f \n" % (CFangleX,CFangleY)),

        #if 0:                  #Change to '0' to stop  showing the heading
                #print ("HEADING  %5.2f \33[1;37;40m tiltCompensatedHeading %5.2f" % (heading,tiltCompensatedHeading)),

        #if 0:                  #Change to '0' to stop  showing the angles from the Kalman filter
                #print ("\033[1;31;40m kalmanX %5.2f  \033[1;35;40m kalmanY %5.2f  " % (kalmanX,kalmanY)),

        #print(" ")

        #slow program down a bit, makes the output more readable
        time.sleep(0.03)
        previous=count-1;
        if abs((rolls[(previous % 5)] - rolls[(count % 5)])) >= 1 and count>=5:
              roll_avg = (rolls[0]+rolls[1]+rolls[2]+rolls[3]+rolls[4]) / 5
              pitch_avg = (pitchs[0]+pitchs[1]+pitchs[2]+pitchs[3]+pitchs[4]) / 5
          
              motorid=0
              #p=PID()
              #p.setKp=3
              #p.setKi=0
              #p.setKd=0
              #p.setpoint=0
              #roll_pid=p.update(roll_avg)
              #print(roll_pid)
<<<<<<< HEAD
              pre_offset = offset
              offset= int(90 + (roll_avg/90)*45)
              speed=20
              if (offset != pre_offset):
                  print(b'%d%03d%03dn' %(motorid,offset,speed))
                  ser.write(b'%d%03d%03dn' %(motorid,offset,speed))
                  time.sleep(0.7)
              
              
              count = count%5 + 1
=======
              offset= 90 + (roll_avg/90)*45
              speed=5
              print(b'm%d%03d%03dn' %(motorid,offset,speed))
              ser.write(b'm%d%03d%03dn' %(motorid,offset,speed)) 
              rolls = 0
              pitchs = 0
              count = 1
>>>>>>> 7c1c29ff45979a0dc537f4883a101ee410b68bce
          #read_serial= ser.readline()
          #print (read_serial)
 #         motor = []
 #         motor = [0,30,20]
 #         ser.write(motor)
#          speed = 20 #ms delay
#          ser.write(b'speed')
          




