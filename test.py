# -*- coding: utf-8 -*-
import vxi11
import binascii
import time 
import numpy as np
from numpy import *
from matplotlib import pyplot as plt
import math

arbgen =  vxi11.Instrument("192.168.1.59")
scope =  vxi11.Instrument("192.168.1.34")

def int2hex(number, bits):
  if number < 0:
    return hex((1 << bits) + number)
  else:
    return hex(number)

MAX_INT = 32767
PP = 6.0

# wave_points = []
def convert_me(voltage,pp): 
	dac_val = int((voltage*MAX_INT)/(pp/2))
	return int2hex(dac_val, 16)
# wave_points.append(convert_me(-2.5,PP))
# wave_points.append(convert_me(-1,PP))
# wave_points.append(convert_me(0,PP))
# wave_points.append(convert_me(1,PP))
# wave_points.append(convert_me(2.5,PP))
# these are the #'s less than 0
# for pt in range(0x8000, 0xffff, 1):
#     wave_points.append(pt)
# wave_points.append(0xffff)

# # these are the #'s greater than 0
# for pt in range(0x0000, 0x7fff, 1):
#     wave_points.append(pt)
       
def create_wave_file(wave_points,pp):
  """create a file"""
  f = open("wave1.bin", "wb")
  for a in wave_points:
      b = convert_me(a, pp)
      #print 'wave_points: ',a,b
      b = b[2:]
      len_b = len(b)
      if (0 == len_b):
          b = '0000'
      elif (1 == len_b):
          b = '000' + b
      elif (2 == len_b):
          b = '00' + b
      elif (3 == len_b):
           b = '0' + b
      b = b[2:4] + b[:2] #change big-endian to little-endian
      c = binascii.a2b_hex(b) #Hexadecimal integer to ASCii encoded string
      f.write(c)
  f.close()


def send_wave_data(dev, frequency):
	"""send wave1.bin to the device"""
	f = open("wave1.bin", "rb") #wave1.bin is the waveform to be sent 
	data = f.read()
	print('write bytes:',len(data))
	dev.write_raw(b"C1:WVDT WVNM,wave1,FREQ,%f,TYPE,8,AMPL,%f,OFST,0.0,PHASE,0.0,WAVEDATA,%s" % (frequency, PP, data))
	dev.write("C1:ARWV NAME,wave1") 
	f.close()


def get_wave_data(dev):
	"""get wave from the devide"""
	f = open("wave2.bin", "w") #save the waveform as wave2.bin
	dev.write("WVDT? user,wave1") #"X" series (SDG1000X/SDG2000X/SDG6000X/X-E) 
	time.sleep(1)
	data = dev.read()
	data_pos = data.find("WAVEDATA,") + len("WAVEDATA,")
	print(data[0:data_pos])
	wave_data = data[data_pos:]
	print('read bytes:',len(wave_data))
	f.write(wave_data)
	f.close()

if __name__ == '__main__': 
	""""""
	
	# scope.write("*RST")

	# single acquisition
	scope.ask("SING;*OPC?")	

	#set data range to all points displayed
	scope.write("CHAN:DATA:POIN DMAX")

	#set manual depth
	scope.write("ACQuire:POINts 10000")
	
	# # Xstart, Xstop, record length in samples
	xstart, xstop, rec_len, vals_per_interval = (float(f) for f in scope.ask("CHAN:DATA:HEAD?").split(',',4)) 

	frequency = math.pow((xstop-xstart),-1)
	
	# vertical resolution
	yres = int(scope.ask("CHAN:DATA:YRES?"))
	
	# voltage for binary value 0
	yor = float(scope.ask("CHAN:DATA:YOR?"))	
	
	# time of first sample
	xor = float(scope.ask("CHAN:DATA:XOR?"))
	
	# time between adjacent samples
	xinc = float(scope.ask("CHAN:DATA:XINC?"))

	scope.write("FORM UINT,8") #set format to unsigned 8bit integer
	yinc = float(scope.ask("CHAN:DATA:YINC?")) #voltage value per bit
	data = scope.ask_raw(b"CHAN:DATA?") #channel data
	data2 = np.array(list(map(lambda x: yor+(yinc*x), data))[10:-1])
	plt.plot( data2 )
	plt.show()

	create_wave_file(data2, 6.0)
	send_wave_data(arbgen, frequency)
	# arbgen.write("C1:SRATE MODE,TARB,VALUE,333333,INTER,LINE") #Use TrueArb and fixed sample rate to play every point
	