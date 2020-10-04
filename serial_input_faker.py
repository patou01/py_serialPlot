import serial
import sys
import msvcrt
from time import sleep
import math

# serial port
serialPort = '/COM3'
baud = 921600


# number of data to plot (not including x)
nData = 6;


# if true, use first input from serial as x axis, else just plot it
firstInputAsX = True

dt = 0.0100 

def initSerial(port):
	print("starting up serial port {port}")


def main():
	run = True
		
	initSerial(serialPort)
	
	with serial.Serial(serialPort, baud) as ser:
		#ser.write('hello'.encode('utf-8'))
		i = 0
		while run:
			points = []
			for j in range(0,nData):
				points.append(math.sin(j*i*dt))
			
			points_str = str(points).strip('[]')
			
			outstr = f"{i*dt:.2f} , {points_str} \n"
			ser.write(outstr.encode('utf-8'))
	#		print(outstr)
			i = i+1
			kbhit = msvcrt.kbhit()
			if kbhit == True:
				c = msvcrt.getch().decode('ASCII')
				ex = 'q'
				print(f"received {c}, exit is {ex}")
				if c == 'q':
					run = False
		
			sleep(dt)
	
if __name__ == '__main__':
	main()