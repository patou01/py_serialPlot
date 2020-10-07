import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import serial
import time
import platform
import sys
from cycler import cycler
import json
import jsonschema

settingsFile = 'settings.json'
schema = 'schema.json'

run = True # not ideal, but will be global for now.

def main():
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

	# make figure
#	plt.ion()
#	fig = plt.figure()
	
	
	fig, ax, lines = makeFig(useCustomLabels, np.array(customLabels), nData)

	nPoints = 0
	with serial.Serial(serialPort, baud) as ser:
		lastDisplay = time.time()
		while run:
			# get inputs from serial
			while ser.inWaiting():
				line = ser.readline()
				datasplit = str(line, 'utf-8').split(',')
				inputs = [float(f) for f in datasplit]
				nPoints = nPoints + 1
				
				# add data to arrays, use roll to make a circular buffer
				if x.size < windowSize:
					x = np.append(x, inputs[0] if firstInputAsX == True else x.size)
					#print(f"{y.size}, {np.array(inputs[int(firstInputAsX):]).size}")
					y = np.vstack([y, np.array(inputs[int(firstInputAsX):])])
				else:
					x = np.roll(x, -1)
					x[-1] = inputs[0] if firstInputAsX == True else nPoints
					y = np.roll(y, -1, axis=0)
					y[-1] = np.array(inputs[int(firstInputAsX):])
					
			# update display
			t = time.time()
			if(t - lastDisplay > displayTime):
				lastDisplay = t
				
				# update line data for plots		
				i = 0
				for l in lines:
						l.set_ydata(y[:,i])
						l.set_xdata(x)
						i = i+1
				
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
			
			time.sleep(0.5*dt)

def windowClosure(evt):
	global run
	run = False
	
def makeFig(useCustom, labels, nData):
	plt.style.use('seaborn-darkgrid')
	plt.rc('figure', facecolor='darkgrey')
	plt.rc('figure.subplot', left=0.05, right=0.98, top=0.98, bottom=0.1)
	plt.rc('xtick',  labelsize=7)     
	plt.rc('ytick',  labelsize=7)
	plt.rc('lines',  linewidth=1)
	plt.rc('legend', frameon=True, loc='upper left', facecolor='white', framealpha=0.5, fontsize=7)
	plt.rc('axes',   prop_cycle=(cycler(color=['b','g','r','c','y','m','k']) +
							   cycler(linestyle=['-.','-','-',':',':','-','-'])))
	plt.rc('font', size=7) 

	plt.ion()
	fig = plt.figure()
	fig.canvas.mpl_connect('close_event', windowClosure)
	
	ax = fig.add_subplot(111)
	ax.set_autoscale_on(True)
	ax.autoscale_view(True,True,True)

	# add lines to plot
	lines = []
	for i in range(0, nData):
		lines = np.append(lines, ax.plot(np.array([0.0]), np.array([0.0])))

	#print(len(lines))
	#labels = np.array(customLabels
	if not useCustom:
		labels = np.array([f"y{i}" for i in range(0, nData)])
		
	print(labels)
	#ax.legend(labels, bbox_to_anchor=(0,1.1), loc="upper left", ncol=len(labels))	
	ax.legend(labels)
	
	return fig, ax, lines

if __name__ == '__main__':
	main()