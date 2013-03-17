#!/usr/bin/python

# from __future__ import print_function
import sys
import argparse
from time import time
from rtlsdr import *
from pylab import *


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--device", type=int, default = 0, help="device index")
	parser.add_argument("-s", "--start_freq", type=float, help="starting frequency (MHz)")
	parser.add_argument("-e", "--end_freq", type=float, help="ending frequency (MHz)")
	parser.add_argument("-fl", "--flist", type=str, help="if not start and end freqs, then a range of frequencies to scan (\"24-30,400-410\")")
	parser.add_argument("-i", "--step", type=float, default = 1, help="step between sampling (MHz)")
	parser.add_argument("-t", "--readtimes", type=int, default = 1, help="times to read samples for one frequency")
	parser.add_argument("-r", "--sample_rate", type=float, default = 2.4, help="sample rate (Mbps)")
	parser.add_argument("-g", "--gain", type=int, default = 10, help="gain")
	parser.add_argument("-ld", "--log_dir", type=str, default = ".", help="existing directory for logfiles")
	args = parser.parse_args()
	
	deviceID = int(0)
	if args.device:
		deviceID = args.device

	if args.flist == None:
		if args.start_freq == None:
			print "No starting frequency specified"
			sys.exit(2);
		else:
			start_freq = args.start_freq
    
		if args.end_freq == None:
			print "No ending frequency specified"
			sys.exit(2);
		else:
			end_freq = args.end_freq
    
		if args.start_freq and args.end_freq:
			flist = str(args.start_freq) + "-" + str(args.end_freq)
	else:
		flist = args.flist
    
	if args.step:
		step = args.step

	if args.readtimes:
		readtimes = args.readtimes
	
	if args.sample_rate:
		sample_rate = args.sample_rate * 1e6

	if args.gain:
		gain = args.gain

	if args.log_dir:
		directory = args.log_dir

	frequency_list = []
	ranges = flist.split(',')
	for item in ranges:
		tmp = item.split('-')
		range = [float(tmp[0]), float(tmp[1])]
		frequency_list.append(range)
	print frequency_list

    
	try:
		sdr = RtlSdr(deviceID)
	except:
		print "Failed to create object for SDR"
		sys.exit(2)


	#freq = start_freq
	sdr.rs = sample_rate
	sdr.gain = gain
	# ppm

	try:
		while True:
			for range in frequency_list:
				freq = start_freq = range[0]
				end_freq = range[1]
				
				print 'Scanning ' + str(start_freq) + ' to ' + str(end_freq) + ' in ' + str(step) + ' MHz steps..',
				starttime = time()
				
				datastring = str()
				while freq <= end_freq:
					# print freq
					sdr.fc = freq * 1000000
				
					timestamp = time()

					tmp = 0
					for x in xrange(1, readtimes + 1):
						tmp += 10 * log10(var(sdr.read_samples(2**16)))
					signal_strength = tmp / readtimes
									
					datastring += str(timestamp) + ' ' + str(freq) + ' ' + str(round(signal_strength, 2)) + ' ' + str(gain) + '\n'
					
					freq += step
			
				# naakamreiz no saakuma
				freq = start_freq

				# print datastring
				logfile = directory + '/' + 'scan-' + str(start_freq) + '-' + str(end_freq) + '.log'
				f = open(logfile, 'a+')
				f.write(datastring)

				# logfile = directory + '/' + 'all.log'
				# f = open(logfile, 'a+')
				# f.write(datastring)
				
				print " 	done in " + str(round(time() - starttime, 1)) + " seconds"
				
			
	except KeyboardInterrupt:
		print "\nstopped"
	except:
		print "Unexpected error:", sys.exc_info()[0]

	sys.exit(2)
	

if __name__ == '__main__':
  main()