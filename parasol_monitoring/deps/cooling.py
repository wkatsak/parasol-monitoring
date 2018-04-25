#!/usr/bin/env python

from ..deps.modbus import ModbusRegister, readModbusRegisters
from pymodbus.client.sync import ModbusSerialClient

FLEXIBOX_MODBUS_ID = 1

TKS_MASK_HEATER = 0b00000001
TKS_MASK_AC = 0b00000100
TKS_MASK_DAMPER = 0b00001000

TKS_TEMP_INDOOR = 0x00
TKS_TEMP_OUTDOOR = 0x01
TKS_OPER_FLAG = 0x02  # AC mode, Line failure...
TKS_TEMP_SET_COOLING = 0x03
TKS_TEMP_SET_HEATING = 0x04
TKS_TEMP_PBAND = 0x05  # 1-10 C
TKS_MAX_FAN_SPEED = 0x06  # 0-100%
TKS_TEMP_DIFF_AC = 0x09  # 2-10 C
TKS_TEMP_DELTA_AC = 0x1E  # 0-10 C
TKS_FAN_SPEED = 0x16  # %
TKS_EXTERNAL_DEVICES = 0x18

class TKS3000(object):
	schema = {
		'TempIndoor' :     ModbusRegister(TKS_TEMP_INDOOR, type='int16', decimals=1, units='C'),
		'TempOutdoor' :    ModbusRegister(TKS_TEMP_OUTDOOR, type='int16', decimals=1, units='C'),
		
		'TempSetCooling' : ModbusRegister(TKS_TEMP_SET_COOLING, type='uint16', units='C'),
		'TempSetHeating' : ModbusRegister(TKS_TEMP_SET_HEATING, type='uint16', units='C'),
		'TempPBand' :      ModbusRegister(TKS_TEMP_PBAND, type='uint16', units='C'),
		'TempDiffAC' :     ModbusRegister(TKS_TEMP_DIFF_AC, type='uint16', units='C'),
		'TempDeltaAC' :    ModbusRegister(TKS_TEMP_DELTA_AC, type='uint16', units='C'),
		
		'FanSpeed' :       ModbusRegister(TKS_FAN_SPEED, type='uint16', units='%'),
		'MaxFanSpeed' :    ModbusRegister(TKS_MAX_FAN_SPEED, type='uint16', units='%'),
		
		'Operation' :      ModbusRegister(TKS_OPER_FLAG, type='uint16', units='C'),
		'ExternalDevices' :ModbusRegister(TKS_EXTERNAL_DEVICES, type='uint16'),
		}
	
	def __init__(self, serialPort, modbusId=FLEXIBOX_MODBUS_ID):
		self.serialPort = serialPort
		self.modbusId = modbusId

	## Change temperature setpoint (SP) ##
	#instrument.write_register(TEMP_SET_COOLING, 20, numberOfDecimals=0, functioncode=6)
	def getTKSValues(self):
		client = ModbusSerialClient(method='rtu', port=self.serialPort, baudrate=9600)

		addrs = [
			'TempIndoor',
			'TempOutdoor',
			'TempSetCooling',
			'TempSetHeating',
			'TempPBand',
			'FanSpeed',
			'MaxFanSpeed',
			'TempDiffAC',
			'TempDeltaAC',
			'ExternalDevices',
		]

		registers = readModbusRegisters(client, unit=self.modbusId, schema=self.schema, addrs=addrs)

		results = {}
		print registers

		results['TempIndoor']  = registers['TempIndoor']
		results['TempOutdoor'] = registers['TempOutdoor']
		results['TempSetCooling']  = registers['TempSetCooling']
		results['TempSetHeating']  = registers['TempSetHeating']
		results['FanSpeed']    = registers['FanSpeed']
		results['MaxFanSpeed']    = registers['MaxFanSpeed']
		results['TempPBand']       = registers['TempPBand']
		results['TempDiffAC']      = registers['TempDiffAC']
		results['TempDeltaAC']     = registers['TempDeltaAC']

		registerIO = registers['ExternalDevices']
		results['StateAC'] = (registerIO & TKS_MASK_AC) == TKS_MASK_AC
		results['StateHeater'] = (registerIO & TKS_MASK_HEATER) == TKS_MASK_HEATER
		results['StateDamper'] = (registerIO & TKS_MASK_DAMPER) == TKS_MASK_DAMPER

		return results
