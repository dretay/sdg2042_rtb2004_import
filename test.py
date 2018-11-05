# -*- coding: utf-8 -*-
import vxi11
import binascii
import time 

arbgen =  vxi11.Instrument("192.168.1.59")
scope =  vxi11.Instrument("192.168.1.34")

wave_points = []
# these are the #'s less than 0
for pt in range(0x8000, 0xffff, 1):
    wave_points.append(pt)
wave_points.append(0xffff)

# these are the #'s greater than 0
for pt in range(0x0000, 0x7fff, 1):
    wave_points.append(pt)
       
def create_wave_file():
  """create a file"""
  f = open("wave1.bin", "wb")
  for a in wave_points:
      b = hex(a)
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


def send_wave_data(dev):
	"""send wave1.bin to the device"""
	f = open("wave1.bin", "rb") #wave1.bin is the waveform to be sent 
	data = f.read()
	print('write bytes:',len(data))
	dev.write_raw(b"C1:WVDT WVNM,wave1,FREQ,2000.0,TYPE,8,AMPL,4.0,OFST,0.0,PHASE,0.0,WAVEDATA,%s" % (data))
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
	# Xstart, Xstop, record length in samples
	print(scope.ask("CHAN:DATA:HEAD?"))
	
	# create_wave_file()
	# send_wave_data(arbgen)
	# arbgen.write("C1:SRATE MODE,TARB,VALUE,333333,INTER,LINE") #Use TrueArb and fixed sample rate to play every point
	