import os, time, sys
import httplib, urllib, signal
import RPi.GPIO as GPIO




os.system("modprobe w1-gpio")
os.system("modprobe w1-therm")

logfile="temparature_log_garage"
#devices="28-00000505ac8f"
devices="28-02146065e5ff" #ordered encased temp probe
set_temp=30

#GPIO.cleanup()

#GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT)

def signal_handler(signal, frame):

	print "Interrupted/terminated"
        print "Turning off relay..."
	GPIO.output(25, True) #OFF

	GPIO.cleanup()
	

	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def get_temp():
	tfile = open("/sys/bus/w1/devices/"+devices+"/w1_slave")
	text = tfile.read()
	tfile.close()
	temperature_data = text.split()[-1]
	temperature = float(temperature_data[2:])
	temperature = temperature / 1000
	return temperature

def getCPUtemperature():
	res = os.popen('vcgencmd measure_temp').readline()
	return(res.replace("temp=","").replace("'C\n",""))


def post_thingspeak(temp,fire):
	cpu = getCPUtemperature()


#keep the names field1 and field2 etc... they are hardcoded

	params1 = urllib.urlencode({'field1': temp, 'field2': cpu,'field3': fire,'field4': temp * 1.8 + 32, 'key':'GV9GP8H74L71Y9BW'})     
                                     # temp is the data you will be sending to the thingspeak channel for plotting the graph. You can add more than one channel and plot more graphs
        headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
	conn = httplib.HTTPConnection("api.thingspeak.com:80")
	try:
		conn.request("POST", "/update", params1, headers)
		response = conn.getresponse()
		print response.status, response.reason
		data = response.read()
		conn.close()
		print temp

			
	except:
		print  "connection failed!"                                                                                                                                      
                                                                                                                                                                                                                                                                                                                                                     
#main look, runs forever
while True == True:

	#writing to file
	f=open(logfile,"a")
	ts=time.strftime("%Y-%m-%d %H:%M")
	

	temp=get_temp()

	if temp < set_temp:  # if lower
		GPIO.output(25, False) #ON
		print "Temp is lower, switching ON"
		fire=1
        if temp >= set_temp: # if highter
		GPIO.output(25, True) #OFF
		print "Temp is higher, switching OFF"
		fire=0

	post_thingspeak(temp,fire)
	f.write(ts+ ", " + str(temp)+"\n")
	f.close()
		
	time.sleep(16)

	
