import matplotlib.pyplot as plt
import numpy as np
import serial
import time
import sys
import json
import jsonschema

settingsFile = 'settings.json'
schema = 'schema.json'
run = True

def main():
	with open(settingsFile, 'r') as f, open(schema, 'r') as ref:
		settings = json.load(f)
		refSettings = json.load(ref)
		jsonschema.validate(settings, refSettings)
		
	nPoints = 0
	x = np.array([0.0])
	y = np.zeros(shape=(1,settings['nInputs']))
	displayTime = 1.0/settings['displayRate']
	
	labels = makeLabels(settings['useCustomLabels'], settings['nInputs'], settings['dataLabels'])
	
	# get initial value for right side of the plot.
	if settings['firstInputAsX']:
		xMax = settings['dt']*settings['windowSize']
	else:
		xMax = settings['windowSize']
	
	fig, ax, lines = makePlot(labels, xMax, settings['autoSizeY'], \
								settings['yMin'], settings['yMax'])

	with serial.Serial(settings['port'], settings['baud']) as ser:
		lastDisplay = time.time()
		while run:
			# read serial if data available
			while ser.inWaiting():
				x, y, nPoints = readSerial(x, y, ser.readline(), len(x) < settings['windowSize'], \
											settings['firstInputAsX'], nPoints)
				
			# update display at requested update rate
			t = time.time()
			if(t - lastDisplay > displayTime):
				lastDisplay = t	
				fig, ax, lines = updatePlot(fig, ax, lines, x, y, settings['windowSize'], \
											settings['autoSizeY'])
			
			time.sleep(0.7*displayTime)


# add data to arrays using a roll-over to make a circular buffer.
# nPoints and firstInputAsX needed to know how to interpret data
def readSerial(x, y, line, appendData, firstInputAsX, nPoints):
	datasplit = str(line, 'utf-8').split(',')
	inputs = [float(f) for f in datasplit]
	nPoints = nPoints + 1
	
	if appendData:
		x = np.append(x, inputs[0] if firstInputAsX == True else x.size)
		y = np.vstack([y, np.array(inputs[int(firstInputAsX):])])
	else:
		x = np.roll(x, -1)
		x[-1] = inputs[0] if firstInputAsX == True else nPoints
		y = np.roll(y, -1, axis=0)
		y[-1] = np.array(inputs[int(firstInputAsX):])
		
	return x, y, nPoints
	

# makes array of labels, truncates if there's too many custom labels.
def makeLabels(useCustom, nData, customLabels):
	if useCustom:
		if nData > len(customLabels):
			print(f"error, expected {nData} inputs but got {len(customLabels)} labels")
			exit(1)
		labels = np.array(customLabels[0:nData])
	else:
		labels = np.array([f"y{i}" for i in range(0, nData)])
		
	return labels


def updatePlot(fig, ax,lines, x, y, windowSize, autoResizeY):
	i = 0
	for l in lines:
		l.set_ydata(y[:,i])
		l.set_xdata(x)
		i = i+1		
		
	ax.autoscale_view(tight=True,scalex=False, scaley=autoResizeY)
	if len(x) == windowSize :
		ax.set_xlim(x[0], x[-1])
	
	ax.relim()
	fig.canvas.draw()
	fig.canvas.flush_events()
	return fig, ax, lines


def makePlot(labels, xMax, autoResizeY, minY=-1, maxY=1):
	plt.ion()
	fig = plt.figure()
	fig.canvas.mpl_connect('close_event', figureClosed)
	
	ax = fig.add_subplot(111)
	ax.autoscale_view(tight=True,scalex=False, scaley=autoResizeY)

	if not autoResizeY:
		ax.set_ylim(minY, maxY)

	ax.set_xlim(0, xMax)

	# add lines to plot
	lines = []
	for i in range(0, len(labels)):
		lines = np.append(lines, ax.plot(np.array([0.0]), np.array([0.0])))

	ax.legend(labels, bbox_to_anchor=(0,1.1), loc="upper left", ncol=len(labels))
	
	return fig, ax, lines


def figureClosed(evt):
	global run
	run = False


if __name__ == '__main__':
	main()