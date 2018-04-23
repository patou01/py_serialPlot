import matplotlib.pyplot as plt
import numpy as np
import StringIO
import serial
import io
import time


#### SETTINGS 

# serial port
serialPort = '/dev/ttyUSB0'
baud = 1000000

# number of points to view
windowSize = 800

# number of data to plot (not including x)
nData = 1;

# allow custom labels for data
useCustomLabels = False
# if using custom labels, you are responsible for having as many entries as nData
customLabels = ['poney1', 'poney2'] 


# if true, use first input from serial as x axis, else just plot it
firstInputAsX = True



######  END SETTINGS


ser = serial.Serial(serialPort, baud)

x = np.array([0.0])
y = np.zeros(shape=(1,nData))
lines = []

intX = int(firstInputAsX)



if firstInputAsX:
	dataNames = 'x'
else:
	dataNames = 'y0'
		
		
dNames = [dataNames]
for i in range(int(not firstInputAsX), nData):
	dataNames = dataNames + ', y' + str(i) 
	dNames = np.append(dNames, 'y' + str(i))


print dataNames
print dNames

# dataTypes for parsing serial line
dataTypes = []
for i in range(0, intX+nData): # 1+ because of x input
	dataTypes = np.append(dataTypes, np.dtype(np.float))


# make figure
plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_autoscale_on(True)
ax.autoscale_view(True,True,True)


# add lines to plot
for i in range(0, nData):
	lines = np.append(lines, ax.plot(x, y[:,i]))


# add labels
if useCustomLabels:
	ax.legend(customLabels)
else:
	ax.legend(dNames[intX:len(dNames)])


print('begin while loop')
lastDisplay = time.time()
while True:
	start = time.time()
	
	# read line on serial
	while ser.inWaiting():
		
		line = ser.readline()
		f = StringIO.StringIO(line)
		data = np.genfromtxt(f, names = dataNames, dtype = dataTypes)
		
		
		
		
		# handle nans
		for i in range(0, nData + intX):
			if np.isnan(data[dNames[i]]):
				data[dNames[i]] = 0
				
		# add data to Y arrays
		yTemp = []
		for i in range(intX, nData+intX):
			yTemp = np.append(yTemp, data[dNames[i]])
		y = np.vstack([y, yTemp])
		
		# add data to X array
		if firstInputAsX:
			x = np.append(x, data['x'])
		else:
			x = np.append(x, x[x.size-1] + 1)
		
	

		# update data
		for i in range(0, nData):
			if x.size > windowSize:
				lines[i].set_ydata(y[y[:,i].size-windowSize:y[:,i].size,i])
				lines[i].set_xdata(x[x.size-windowSize:x.size])
			else:
				lines[i].set_ydata(y[:,i])
				lines[i].set_xdata(x)			

	end = time.time()
	#	print(1000*(end - start))
#		print(x[x.size-1])
	# plot
	if 1000*(end-lastDisplay):
		lastDisplay = time.time()
		ax.relim()
		ax.autoscale_view(True,True,True)
		fig.canvas.draw()
		fig.canvas.flush_events()
		
	
