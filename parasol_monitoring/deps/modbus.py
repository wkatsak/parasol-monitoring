#!/usr/bin/env python

import numpy
import minimalmodbus
import serial

class ModbusRegister:
	def __init__(self, id, value=-1, type='uint16', decimals=0, units=''):
		self.id = id
		#uint16
		#int16
		#uint32
		#int32
		self.value = value
		self.type = type
		self.decimals = decimals
		self.units = units
	
	def setValue(self, value):
		if self.type == 'int16':
			self.value = numpy.int16(value)
		elif self.type == 'int32':
			self.value = numpy.int32(value)
		else:
			self.value = value
		for i in range(0, self.decimals):
			self.value = self.value/10.0
	
	def is32(self):
		return self.type == 'uint32' or self.type == 'int32'
	
	@staticmethod
	def to32(val0, val1):
		return (val1 << 16) + val0

def getModbus(dev, modbusId, baudrate=9600):
	instrument = minimalmodbus.Instrument(dev, modbusId) # port name, slave address (in decimal)

	instrument.serial.port          # this is the serial port name
	instrument.serial.baudrate = baudrate   # Baud
	instrument.serial.parity   = serial.PARITY_NONE
	instrument.serial.bytesize = 8
	instrument.serial.stopbits = 1
	instrument.serial.timeout  = 1   # seconds
	
	return instrument

def readModbusRegisters(client, unit=0, schema={}, addrs=[]):
	ret = {}
	
	try:
		# Get ids
		registers = []
		for addr in addrs:
			if isinstance(addr, str):
				if addr in schema:
					registerDesc = schema[addr]
					registers.append(registerDesc.id)
					if registerDesc.type.find('32')>=0:
						registers.append(registerDesc.id+1)
			else:
				registers.append(addr)
		
		# Get register range
		registers = sorted(registers)
		ini = registers[0]
		fin = registers[-1]
		count = fin-ini+1
		
		if False:
			print 'Debugging ModBus reading'
			print 'Address:', addr
			print 'Schema:', schema
			print registers
			print ini, fin, count
			print unit
		
		# Check with the power meter
		rr = client.read_holding_registers(address=ini, count=count, unit=unit)
		if rr == None:
			print 'Cannot connect to modbus device.'
		else:
			#print rr.registers
			for i in range(0, len(rr.registers)):
				regId = ini+i
				if regId in registers:
					# Look for register name
					key = None
					for auxKey in schema.keys():
						if regId == schema[auxKey].id:
							key = auxKey
							break
					# Read register properly
					if key != None:
						registerDesc = schema[key]
						if registerDesc.is32():
							aux = ModbusRegister.to32(rr.registers[i], rr.registers[i+1])
							registerDesc.setValue(aux)
						else:
							#print key, rr.registers[i]
							registerDesc.setValue(rr.registers[i])
						# Check value
						ret[key] = registerDesc.value
	except Exception, e:
		print 'Error reading modbus registers:', e
	return ret
