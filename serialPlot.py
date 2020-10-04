import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from io import BytesIO
import serial
import time
import platform


#### SETTINGS 

# serial port
serialPort = '/COM4'
baud = 115200

# number of points to view
windowSize = 2000

# number of data to plot (not including x)
nData = 6;


# if separatePlots is True, each set is plotted on a different subplot
# all subplots have same X however.
separatePlots = False

# allow custom labels for data
useCustomLabels = True
# if using custom labels, you are responsible for having as many entries as nData
customLabels = ['sinx', 'sin2x'] 


# if true, use first input from serial as x axis, else just plot it
firstInputAsX = True
# Only used to estimate the x interval to display at the beginning
# dt is ~ the time expected between 2 points. 
# Only used when firstInputAsX is True
dt = 0.0100 



# y auto resize. If autoResizeY set to False, please give minY < maxY
autoResizeY = False
minY = -1
maxY = 1




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
	nPoints = 0
	# read line on serial
	while ser.inWaiting():
		
		
		# get inputs from serial
		line = ser.readline()
		datasplit = str(line, 'ASCII').split(',')
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
		