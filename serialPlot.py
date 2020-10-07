import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import serial
import time
import platform
import sys
import json
import jsonschema

settingsFile = 'settings.json'
schema = 'schema.json'

def main():
	print("Using python: " + platform.python_version())
	print("Using numpi: " + np.__version__)
	print("Using matplotlib: " + matplotlib.__version__)
	print("Serial: " + serial.__version__)

	with open(settingsFile, 'r') as f, open(schema, 'r') as ref:
		settings = json.load(f)
		refSettings = json.load(ref)
		jsonschema.validate(settings, refSettings)
		
		serialPort = settings['port']
		baud = settings['baud']
		nData = settings['nInputs']
		firstInputAsX = settings['firstInputAsX']
		dt = settings['dt']
		windowSize = settings['windowSize']
		autoResizeY = settings['autoSizeY']
		minY = settings['yMin']
		maxY = settings['yMax']
		useCustomLabels = settings['useCustomLabels']
		customLabels = settings['dataLabels']
		displayTime = 1.0/settings['displayRate']

	x = np.array([0.0])
	y = np.zeros(shape=(1,nData))
	lines = []
	ax = []

	# make figure
	plt.ion()
	fig = plt.figure()

	ax = fig.add_subplot(111)
	ax.set_autoscale_on(True)
	ax.autoscale_view(True,True,True)

	# add lines to plot
	for i in range(0, nData):
		lines = np.append(lines, ax.plot(x, y[:,i]))


	labels = np.array(customLabels)
	ax.legend(labels, bbox_to_anchor=(0,1.1), loc="upper left", ncol=nData)


	nPoints = 0
	with serial.Serial(serialPort, baud) as ser:
		lastDisplay = time.time()
		while True:
			
			while ser.inWaiting():
				# get inputs from serial
				line = ser.readline()
				datasplit = str(line, 'utf-8').split(',')
				inputs = [float(f) for f in datasplit]
				nPoints = nPoints + 1
				
				# add data to arrays
				if x.size < windowSize:
					x = np.append(x, inputs[0] if firstInputAsX == True else x.size)
					y = np.vstack([y, np.array(inputs[int(firstInputAsX):])])
				else:
					x = np.roll(x, -1)
					x[-1] = inputs[0] if firstInputAsX == True else nPoints
					y = np.roll(y, -1, axis=0)
					y[-1] = np.array(inputs[int(firstInputAsX):])
					
				# update line data for plots		
				i = 0
				for l in lines:
						l.set_ydata(y[:,i])
						l.set_xdata(x)
						i = i+1


			# update display
			t = time.time()
			if(t - lastDisplay > displayTime):
				lastDisplay = t
				ax.autoscale_view(True,x.size < windowSize,autoResizeY)
				if not autoResizeY:
					ax.set_ylim(minY, maxY)
					
				if x.size < windowSize :
					if firstInputAsX:
						ax.set_xlim(0, dt*windowSize)
					else:
						ax.set_xlim(0, windowSize)		
				else:
					ax.set_xlim(x[0], x[-1], True, True)
				
				ax.relim()
				fig.canvas.draw()
				fig.canvas.flush_events()
			
			time.sleep(0.7*displayTime)

if __name__ == '__main__':
	main()