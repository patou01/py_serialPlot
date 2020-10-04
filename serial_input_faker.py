import serial
import sys
import msvcrt
from time import sleep
import math
import json
import jsonschema 

settingsFile = 'settings.json'
schema = 'schema.json'

def main():
	with open(settingsFile, 'r') as f, open(schema, 'r') as ref:
		settings = json.load(f)
		refSettings = json.load(ref)
		jsonschema.validate(settings, refSettings)
	
	with serial.Serial(settings['testPort'], settings['baud']) as ser:
		i = 0
		points = []
		for j in range(0,settings['nInputs']):
			points.append(0)
			
		run = True
		while run:
			for j in range(0,settings['nInputs']):
				points[j] = round(math.sin((j+1)*i*settings['dt']),2)
			points_str = str(points).strip('[]')
			
			if settings['firstInputAsX'] :
				outstr = f"{i*settings['dt']:.2f} , {points_str} \n"
			else:
				outstr = f"{points_str} \n"

			ser.write(outstr.encode('utf-8'))

			i = i+1
			if msvcrt.kbhit() == True:
				c = msvcrt.getch().decode('ASCII')
				if c == 'q':
					run = False
		
			sleep(settings['dt'])
	
if __name__ == '__main__':
	main()