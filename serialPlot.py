import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from io import BytesIO
import serial
import time
import platform


#### SETTINGS 

# serial port
serialPort = '/dev/ttyUSB0'
baud = 115200

# number of points to view
windowSize = 50

# number of data to plot (not including x)
nData = 2;


# if separatePlots is True, each set is plotted on a different subplot
# all subplots have same X however.
separatePlots = False

# allow custom labels for data
useCustomLabels = True
# if using custom labels, you are responsible for having as many entries as nData
customLabels = ['poney1', 'poney2'] 


# if true, use first input from serial as x axis, else just plot it
firstInputAsX = True
# Only used to estimate the x interval to display at the beginning
# dt is ~ the time expected between 2 points. 
# Only used when firstInputAsX is True
dt = 0.0100 



# y auto resize. If autoResizeY set to False, please give minY < maxY
autoResizeY = True
minY = 0
maxY = 100




######  END SETTINGS


print("Using python: " + platform.python_version())
print("Using numpi: " + np.__version__)
print("Using matplotlib: " + matplotlib.__version__)
print("Serial: " + serial.__version__)

ser = serial.Serial(serialPort, baud)

x = np.array([0.0])
y = np.zeros(shape=(1,nData))
lines = []
ax = []

intX = int(firstInputAsX)



if firstInputAsX:
	dataNames = 'x'
else:
	dataNames = 'y0'
		
		
dNames = [dataNames]
for i in range(int(not firstInputAsX), nData):
	dataNames = dataNames + ', y' + str(i) 
	dNames = np.append(dNames, 'y' + str(i))



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
	ax.legend(customLabels, bbox_to_anchor=(0,1.1), loc="upper left", ncol=nData)
else:
	ax.legend(dNames[intX:len(dNames)],bbox_to_anchor=(0,1.1), loc="upper left", ncol=nData)



lastDisplay = time.time()
while True:
	start = time.time()
	
	# read line on serial
	while ser.inWaiting():
		
		line = ser.readline()
		f = BytesIO(line)
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

	lastDisplay = time.time()
	
	
	ax.autoscale_view(True,x.size < windowSize,autoResizeY)
	if not autoResizeY:
		ax.set_ylim(minY, maxY)
		
	if x.size < windowSize :
		if firstInputAsX:
			ax.set_xlim(0, dt*windowSize)
		else:
			ax.set_xlim(0, windowSize)
			
	else:
		ax.set_xlim(x[x.size-windowSize], x[x.size-1], True, True)
	
	
	ax.relim()
	fig.canvas.draw()
	fig.canvas.flush_events()
		
	
