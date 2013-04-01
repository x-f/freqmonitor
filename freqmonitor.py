#!/usr/bin/python

# from __future__ import print_function
import sys
import argparse
import gc
from time import time, gmtime, strftime
from rtlsdr import *
from pylab import *

	
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--device", type=int, default = 0, help="device index")
	parser.add_argument("-s", "--start_freq", type=float, help="starting frequency (MHz)")
	parser.add_argument("-e", "--end_freq", type=float, help="ending frequency (MHz)")
	parser.add_argument("-fl", "--flist", type=str, help="if not start and end freqs, then a range of frequencies to scan (\"24-30,400-410\")")
	parser.add_argument("-i", "--step", type=float, default = 1, help="step between sampling (MHz)")
	parser.add_argument("-single", "--single_freq", type=bool, default = False, help="scan only single frequency (speeds up scanning)")
	parser.add_argument("-t", "--readtimes", type=int, default = 1, help="times to read samples on one frequency for averaging")
	parser.add_argument("-r", "--sample_rate", type=float, default = 2.4, help="sample rate (Mbps)")
	parser.add_argument("-g", "--gain", type=int, default = 10, help="gain")
	parser.add_argument("-rst", "--reset_every", type=int, default = 0, help="after how many cycles reconnect the device")
	parser.add_argument("-w", "--io_write_every", type=int, default = 0, help="after how many cycles write data to file")
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

	if args.single_freq:
		single_freq = args.single_freq

	if args.readtimes:
		readtimes = args.readtimes
	
	if args.sample_rate:
		sample_rate = args.sample_rate * 1e6

	if args.gain:
		gain = args.gain

	reset_every = int(0)
	if args.reset_every:
		reset_every = args.reset_every

	io_write_every = int(0)
	if args.io_write_every:
		io_write_every = args.io_write_every

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
		print >> sys.stderr, strftime("%H:%M:%S", gmtime()) + " ",
		sdr = RtlSdr(deviceID)
	except:
		print "Failed to create object for SDR"
		sys.exit(2)


	datastring_buffer = str()

	try:
		sdr.rs = sample_rate
		sdr.gain = gain
		sdr.fc = 100e6

		# warm up
		print "warming up.."
		for i in xrange(0, 120):
			# sdr.read_samples(2**16)
			sdr.read_samples(2**16)
			# print ".",
		print "starting scan"

		cnt = 0
		io_cnt = 0
		
		while True:
			
			io_cnt = io_cnt + 1					
			# reset the device
			cnt = cnt + 1;
			if cnt > reset_every and reset_every > 0:
				cnt = 1
				sdr.close()
				try:
					print >> sys.stderr, strftime("%H:%M:%S", gmtime()) + " ",
					sdr = RtlSdr(deviceID)
				except:
					print "Failed to create object for SDR"
					sys.exit(2)

				sdr.rs = sample_rate
				sdr.gain = gain
				sdr.fc = 100e6

				# warm up
				# for i in xrange(0, 60):
					# sdr.read_samples(2**16)
				
			for range in frequency_list:
				freq = start_freq = range[0]
				end_freq = range[1]
				
				print 'Scanning ' + str(start_freq) + ' to ' + str(end_freq) + ' in ' + str(step) + ' MHz steps..',
				starttime = time()
				
				datastring = str()
				while freq <= end_freq:
					try:
						if cnt <= 1:
							# print "setting freq"
							sdr.fc = freq * 1000000
					except:
						print "Warning: center frequency not set, trying.."
						try:
							sdr.fc = freq * 1000000
						except:
							print "Failed to set center frequency of " + freq * 1000000
							sys.exit(2)
						
					timestamp = time()

					tmp = 0
					for x in xrange(1, readtimes + 1):
						# tmp += 10 * log10(var(sdr.read_samples(2**16)))
						tmp += 10 * log10(var(sdr.read_samples(2**12)))
					signal_strength = tmp / readtimes
					
					if cnt > 1:
						datastring += str(timestamp) + ' ' + str(freq) + ' ' + str(round(signal_strength, 2)) + ' ' + str(gain) + '\n'
					# else:
						# print "skipping"
					
					freq += step
			
				# naakamreiz no saakuma
				freq = start_freq

				# print datastring
				# logfile = directory + '/' + 'scan-' + str(start_freq) + '-' + str(end_freq) + '.log'
				# f = open(logfile, 'a+')
				# f.write(datastring)
				datastring_buffer += datastring

				print " 	done in " + str(round(time() - starttime, 1)) + " seconds"
				
				gc.collect()

			# write data to file
			if io_cnt == io_write_every:
				logfile = directory + '/' + 'scan-' + str(start_freq) + '-' + str(end_freq) + '.log'
				f = open(logfile, 'a+')
				f.write(datastring_buffer)
				f.flush()
				datastring_buffer = str()
				io_cnt = 0
				# print "I/O"
			
	except KeyboardInterrupt:
		print "\nstopped"
		if datastring_buffer != "":
			logfile = directory + '/' + 'scan-' + str(start_freq) + '-' + str(end_freq) + '.log'
			f = open(logfile, 'a+')
			f.write(datastring_buffer)

	#except:
	#	print "Unexpected error:", sys.exc_info()[0]

	sdr.close()
	sys.exit(2)
	

if __name__ == '__main__':
  main()
