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
import numpy as np
from scipy.stats import pearsonr

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
		df = pd.read_csv('processed_right_hand_data.txt', header=0, index_col=0, delimiter = ",\s+")
		df = df.drop(df.keys()[-1], axis = 1)

		threshold = 0.05
		network = 'Weighted network'   
		header = df.columns.tolist()
		l = len(header)

		totsize = len(df.index)
		timestep = 512

		for k in range(0,totsize,timestep):
		
			print(k)
			
			df1 = df.iloc[k:k+timestep]

			nodei = []
			nodej = []
			weight = []

			for i in range(l):
				# ADJ_corr[i][i] = 1  # setting the diagonal elements 
				for j in range(i+1,l):
					[corr_TS, Pval_TS] = pearsonr(df1[header[i]], df1[header[j]])

					if Pval_TS < threshold and corr_TS>0.8:
						nodei.append(i)
						nodej.append(j)
						if network == 'Weighted network':
							weight.append(corr_TS)
						else:    
							weight.append(1)

			point_data = {
				'node1':nodei,
				'node2':nodej,
				'weight':weight,
				'mean':np.mean(weight)
			}
			print(weight, np.mean(weight))
			#write the json object to the socket
			self.write_message(json.dumps(point_data))

			#create new ioloop instance to intermittently publish data
			ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=0.5), self.send_data)
			time.sleep(0.5)

# def readCsvNets(dir='./nets'):
	# with open("Smaller_EEGfile.csv") as csvfile:
	# for net in os.listdir('./nets'):
	# 	print "./nets/" + str(net)
	# 	with open("./nets/"+net) as csvfile:
	# 		# csv_reader = csv.reader(csvfile, delimiter=",")
	# 		csv_reader = pd.read_csv(csvfile, header=0)
	# 		#threshold values
	# 		csv_reader = csv_reader[csv_reader['weight']>0.97] #threshold weights
	# 		# print csv_reader['node1']
	# 		#create a new data point
	# 		point_data = {
	# 			'node1': list(csv_reader['node1']),
	# 			'node2': list(csv_reader['node2']),
	# 			'weight': list(csv_reader['weight']) #abs(float(row[4]))
	# 		}


if __name__ == "__main__":
	#create new web app w/ websocket endpoint available at /websocket
	print "Starting websocket server program. Awaiting client requests to open websocket ..."
	application = web.Application([(r'/websocket', WebSocketHandler)])
	application.listen(8001)
	ioloop.IOLoop.instance().start()
