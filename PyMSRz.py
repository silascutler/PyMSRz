#!/usr/bin/env python
__author__      = "Silas Cutler"
__copyright__   = "Copyright 2018"
__license__     = "GPL"
__version__     = "0.0.2"
__maintainer__  = "Silas Cutler"
__email__       = "Silas.Cutler@BlackListThisDomain.com"
__status__      = "Development"

import sys
import time
import bluetooth

def hexdump(src, length=16):
    FILTER = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])
    lines = []
    for c in xrange(0, len(src), length):
        chars = src[c:c+length]
        hex = ' '.join(["%02x" % ord(x) for x in chars])
        printable = ''.join(["%s" % ((ord(x) <= 127 and FILTER[ord(x)]) or '.') for x in chars])
        lines.append("%04x  %-*s  %s\n" % (c, length*3, hex, printable))
    return ''.join(lines)

class MSRz(object):
	def __init__(self, bHandle):
		self.handle = bHandle
		self.ICTOL_CODES = {
			"WRITE_START"          : "\x1B\x77\x1B\x73",
			"RAWWRITE_START"       : "\x1B\x6E\x1B\x73",

			"TRACK_1"              : "\x1B\x01",
			"TRACK_2"              : "\x1B\x02",
			"TRACK_3"              : "\x1B\x03",
			"WRITE_END"            : "\x3F\x1C",

			"READ"                 : "\x1B\x72",
			"RAWREAD"              : "\x1B\x6D", 

			"SENSORTEST"           : "\x1B\x86",
			"RAMTEST"              : "\x1B\x87",	

			"BLANK"                : "\x1B\x2B",	


			"GET_MODEL"            : "\x1B\x74", 
			"GET_FIRMWARE_VERSION" : "\x1B\x76",

			"ACTIVATE_YELLOW_LED"  : "\x1B\x83",
			"ACTIVATE_GREEN_LED"   : "\x1B\x83",
			"ACTIVATE_RED_LED"     : "\x1B\x85",
			"ACTIVATE_ALL_LED"     : "\x1B\x81",
			"DEACTIVATE_ALL_LED"   : "\x1B\x81",
		}
		if not self.testConnection():
			raise( "Setup Error")

	def testConnection(self):
		try:
			self.handle.send( self.ICTOL_CODES["GET_MODEL"] )
			self._read(3)
			return True
		except Exception, e:
			print "Error Test: %s" % e
			return False

	def _read(self, readLen = None):
		data = ""
		try:
			while True:
				data += self.handle.recv(1)
				if len(data) == 0: break
				if data[-4:-1] == "\x3f\x1c\x1b": break # End Flag: 3f 1c 1b ??
				if readLen:
					readLen -= 1	
					if readLen <= 0:
						return data

		except Exception, e:
			print "Exception: %s" % e
		return data

	def _write(self, indata):
		self.handle.send( indata )


	def read(self):
		print "Ready to read..."
		self.handle.send( self.ICTOL_CODES["READ"] )
		return self._read()[2:-2]

	def print_tracks(self, indata):
		print hexdump(indata)


		t2_index = t3_index = 0
		if self.ICTOL_CODES["TRACK_1"] in indata:
			t1_index = indata.index( self.ICTOL_CODES["TRACK_1"] ) + 2
		if self.ICTOL_CODES["TRACK_2"] in indata:
			t2_index = indata.index( self.ICTOL_CODES["TRACK_2"] ) + 2
		if self.ICTOL_CODES["TRACK_3"] in indata:	
			t3_index = indata.index( self.ICTOL_CODES["TRACK_3"] ) + 2
		
		if t1_index > 0:
			t1_data = indata[t1_index : t2_index - 2 ]
			if t1_data != self.ICTOL_CODES["BLANK"]:
				print "Track 1: %s ( %s )" % ( t1_data , t1_data.encode('hex') )
		if t2_index > 0:
			t2_data = indata[t2_index : t3_index - 2 ]
			if t2_data != self.ICTOL_CODES["BLANK"]:
				print "Track 2: %s ( %s )" % ( t2_data, t2_data.encode('hex') )
		if t3_index > 0:
			t3_data	= indata[t3_index :  -2 ]
			if t3_data != self.ICTOL_CODES["BLANK"]:
				print "Track 3: %s ( %s )" % ( t3_data, t3_data.encode('hex') )

#	def write_track1(self, indata):
#		print "Writing..."
#
#		buffer = self.ICTOL_CODES["RAWWRITE_START"] 
#		buffer += self.ICTOL_CODES["TRACK_1"] 
#		buffer += _DATA_CONV[('raw', 'iso')](indata, 1)
#		buffer += self.ICTOL_CODES["TRACK_2"] 
#		buffer += "\x00"
#		buffer += self.ICTOL_CODES["TRACK_3"] 
#		buffer += "\x00"
#		buffer += self.ICTOL_CODES["WRITE_END"] 
#
#		self._write(buffer)
#		return self._read(1)


if __name__ == "__main__":
	client_socket = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
	client_socket.connect((sys.argv[1], 3))
	t = MSRz( client_socket )
	t.print_tracks(t.read())

