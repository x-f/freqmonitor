freqmonitor
===========

Monitor and plot data with RTLSDR.

Inspired by the works of superkuh (http://www.superkuh.com/rtlsdr.html#pyrtlsdr_logger).


Requirements:
  gnuplot
  rtlsdr - http://cgit.osmocom.org/cgit/rtl-sdr/
  pyrtlsdr - https://github.com/roger-/pyrtlsdr
  pylab (SciPy)


Usage:

To scan a list of frequencies - from 35 to 85 MHz, and from 1420 to 1421 MHz in 0.05 MHz steps with a gain of 25 using RTLSDR device with the index 0
  ./freqmonitor.py --flist="35-85,1420-1421" -d 0 -i 0.05 -g 25

Two log files will be produced:
  1. scan-35.0-85.0.log
  2. scan-1420.0-1421.0.log


Plot the data with GNUplot:

1. For a particular frequency
Prepare the log file (TODO: optimize to have just one file)
  grep " 1420\.4 " ./scan-1420.0-1421.0.log > ./scan-freq-1420.4.log

Prepare the GNUplot script, save it as, for example, scan-1420.4.gp:
  set terminal png size 1000,500
  set ylabel "Intensity (dB)"
  set xlabel "Time (UTC)"
  set xdata time
  set timefmt "%s"
  set format x "%d/%m\n%H"
  set grid
  set key off
  set pointsize 0.5
  set title "1420.4 MHz"
  set output "./scan-1420.4.png"
  plot './scan-freq-1420.4.log' using 1:3 smooth bezier with lines lc 3

Run GNUplot:
  cat ./scan-1420.4.gp | gnuplot

2. To generate a spectral map
Prepare the GNUplot script, save it as, for example, scan-35-85.gp:
  set view map
  set terminal png crop
  set term png size 1200, 730
  set key off
  set ylabel 'Frequency (MHz)'
  set xlabel "Time (UTC)"
  set xdata time
  set timefmt "%s"
  set format x "%d/%m\n%H"
  set cblabel 'Intensity (dB)'
  set title "35 - 85 Mhz"
  set ytics 5
  set output './spectral-map-35-85.png'
  plot './scan-35.0-85.0.log' using 1:2:3 with points ps 0.5 pt 5 palette

Run GNUplot:
  cat ./scan-35-85.gp | gnuplot


