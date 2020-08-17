# This is a script to automate running and recording a reflow profile
# and tracking Job and boar information. the goal is to trigger this
# script after a pick and place operation has finished and that job
# job info can be passed to this. This full profile is logged for
# QA purposes.

import serial
import time
import logging

#startup information
print('Enter Job Information')
job = input("Input Job Number:")
board = input("Board Number:")
user = input("Operator Name:")


#Configure Logger
logger = logging.getLogger('myapp')
hdlr = logging.FileHandler(job + '-' + board + ".txt")
formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

logger.info( "Job:" + job + " Board: " + board + " Operator Name:" + user)

logger.info("starting serial port")

# Initialize Serial Port
ser = serial.Serial()
ser.port = "COM" + input("select com port: COM:")  # Arduino serial port
ser.baudrate = 115200
ser.timeout = 50  # specify timeout when using readline()
ser.open()
if ser.is_open == True:
    print("\nConnected to reflow oven")
    logger.info((str(ser)))

print('Starting 63/37 profile for ' + job + ':' + board + '\n')

ser.write(b'select profile 2')
time.sleep(0.5) #wait for response
print('MESSAGE FROM OVEN:\n')

b=''
while(ser.inWaiting()>0):
    b = ser.readline().rstrip().lstrip().decode('utf-8', errors="ignore")
    logger.info("msg from oven:" + b)
    print(b)

userInput = input('Is this the correct profile? (y/n):')
if (userInput == 'y'):
    logger.info(user + " has accepted profile from oven")
    ser.write(b'reflow')
    time.sleep(1)

    b = ser.readline().rstrip().lstrip().decode('utf-8', errors="ignore")

    headerString = '# Time,  Temp0, Temp1, Temp2, Temp3,  Set,Actual, Heat, Fan,  ColdJ, Mode'
    #read lines until the header comes up, log to file
    while (b != headerString):
        b = ser.readline().rstrip().lstrip().decode('utf-8', errors="ignore")
        logger.info(b)
        print(b)

    #print the header and reset
    b = ""

    msgInterrupted="Reflow interrupted by keypress"
    msgDone = "Reflow done"

    print('')
    #while ((b != msgInterrupted) and (b != msgDone)):
    while(True):
        b = ser.readline().rstrip().lstrip().decode('utf-8', errors="ignore")
        if ((b == msgInterrupted) or (b == msgDone)):
            logger.info(b)
            print('\n'+b)
            break
        if len(b) > 0:
            print(b, end='\r')
            logger.info(b)


    print('closing serial port')
    logger.info("Closing serial port")
    ser.close()
