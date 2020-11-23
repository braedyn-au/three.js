import time
import random
import json
import datetime
from tornado import websocket, web, ioloop
from datetime import timedelta
from random import randint
import csv
import pandas as pd
import os

paymentTypes = ["cash", "tab", "visa","mastercard","bitcoin"]
namesArray = ['Ben', 'Jarrod', 'Vijay', 'Aziz']

class WebSocketHandler(websocket.WebSocketHandler):
	
	def check_origin(self, origin):
		return True
	
	#on open of this socket
	def open(self):
		print 'Connection established.'
		#ioloop to wait for 3 seconds before starting to send data
		ioloop.IOLoop.instance().add_timeout(datetime.       
		timedelta(seconds=1.0), self.send_data)

	#close connection
	def on_close(self):
		print 'Connection closed.'

	# Our function to send new (random) data for charts
	def send_data(self):
		print "Sending Data"
		#create a bunch of random data for various dimensions we want
		k = 0
		# with open("Smaller_EEGfile.csv") as csvfile:
		for net in os.listdir('./nets'):
			print "./nets/" + str(net)
			with open("./nets/"+net) as csvfile:
				# csv_reader = csv.reader(csvfile, delimiter=",")
				csv_reader = pd.read_csv(csvfile, header=0)
				#threshold values
				csv_reader = csv_reader[csv_reader['weight']>0.9]
				# print csv_reader['node1']
				#create a new data point
				point_data = {
					'node1': list(csv_reader['node1']),
					'node2': list(csv_reader['node2']),
					'weight': list(csv_reader['weight']) #abs(float(row[4]))
				}

				#write the json object to the socket
				self.write_message(json.dumps(point_data))

				#create new ioloop instance to intermittently publish data
				ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=0.5), self.send_data)
				time.sleep(0.5)
				k+=1
				if k>100:
					break

if __name__ == "__main__":
	#create new web app w/ websocket endpoint available at /websocket
	print "Starting websocket server program. Awaiting client requests to open websocket ..."
	application = web.Application([(r'/websocket', WebSocketHandler)])
	application.listen(8001)
	ioloop.IOLoop.instance().start()
