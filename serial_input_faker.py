import serial
import sys
import msvcrt
from time import sleep
import math
import sys
import json
import jsonschema 

settingsFile = 'settings.json'
schema = 'schema.json'

def main():
	run = True

	with open(settingsFile, 'r') as f, open(schema, 'r') as ref:
		settings = json.load(f)
		refSettings = json.load(ref)
		jsonschema.validate(settings, refSettings)
		
		serialPort = settings['testPort']
		baud = settings['baud']
		nData = settings['nInputs']
		firstInputAsX = settings['firstInputAsX']
		dt = settings['dt']
	
	with serial.Serial(serialPort, baud) as ser:
		i = 0
		points = []
		for j in range(0,nData):
			points.append(0)
			
		while run:
			for j in range(0,nData):
				points[j] = round(math.sin((j+1)*i*dt),2)
			points_str = str(points).strip('[]')
			
			if firstInputAsX :
				outstr = f"{i*dt:.2f} , {points_str} \n"
			else:
				outstr = f"{points_str} \n"

			ser.write(outstr.encode('utf-8'))

			i = i+1
			if msvcrt.kbhit() == True:
				c = msvcrt.getch().decode('ASCII')
				ex = 'q'
				
				if c == 'q':
					print(f"received {c}, exit is {ex}")
					run = False
		
			sleep(dt)
	
if __name__ == '__main__':
	main()