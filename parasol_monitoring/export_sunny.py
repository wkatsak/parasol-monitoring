from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from deps.SunnyWebBox import SunnyWebBoxHTTP

import argparse
import logging
import time
import sys

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

class SunnyWebboxCollector(object):
	VALUE_NAME_PREFIXES = {
		'SE' : 'sunny_sensorbox',
		'SI' : 'sunny_island',
		'WR' : 'sunny_boy',
	}

	VALUE_NAME_MAPPINGS = {
		'SE' : {
			'TmpMdul C' : 'temp_mod',
			'TmpAmb C' : 'temp_amb',
			'IntSolIrr' : 'solar_irradiation',
			'WindVel m/s' : 'wind_velocity',
		},
		'SI' : {
			'BatSoc' : 'battery_level',
			'BatSocErr' : 'battery_level_error',
			'BatTmp' : 'battery_temp',
			'Pac' : 'pac',
			'ExtPwrAt' : 'external_power',
			'ExtPwrAtSlv1' : 'external_power_slv1',
			'ExtVtg' : 'external_voltage',
			'ExtVtgSlv1' : 'external_voltage_slv1',
			'ExtCur' : 'external_current',
			'ExtCurSlv1': 'external_current_slv1',
			'TotExtPwrAt' : 'external_power_total',

			'InvPwrAt' : 'inverter_power',
			'InvPwrAtSlv1' : 'inverter_power_slv1',
			'InvVtg': 'inverter_voltage',
			'InvVtgSlv1': 'inverter_voltage_slv1',
			'InvCur': 'inverter_current',
			'InvCurSlv1': 'inverter_current_slv1',
			'TotalInvPtrAt' : 'inverter_power_total',

			'GdEgyCntOut' : 'grid_energy_out',
			'GdEgyCntIn' : 'grid_energy_in',
			'EgyCntOut' : 'energy_out',
			'EgyCntIn' : 'energy_in',
			'E-Total' : 'energy_total',
			'E-Total-In' : 'energy_in_total',
		},
		'WR' : {
			'A.Ms.Watt' : 'power_in',
			'A.Ms.Vol' :  'voltage_in',
			'A.Ms.Amp' : 'current_in',
			'Pac' : 'power_out',
			'E-Total' : 'energy_total',
		}
	}

	def __init__(self, args):
		self.args = args

	def collect(self):
		# hold the metrics here while collecting them
		metrics = []

		# initialize the interface to the Sunny Web Box
		swb = SunnyWebBoxHTTP(self.args.webbox_address, password=self.args.webbox_password)

		# iterate over Sunny devices and collect the metrics
		for d in swb.getDevices():
			deviceKey = d['key']
			lookupPrefix = d['name'][0:2]
			if lookupPrefix not in self.VALUE_NAME_PREFIXES:
				continue

			channels = swb.getProcessDataChannels(deviceKey)
			data = swb.getProcessData([{'key' : deviceKey, 'channels' : channels}])

			PREFIX = self.VALUE_NAME_PREFIXES[lookupPrefix]
			MAPPINGS = self.VALUE_NAME_MAPPINGS[lookupPrefix]

			for c in data[deviceKey]:
				if c['name'] not in MAPPINGS:
					continue

				try:
					name = c['name']

					metricName = PREFIX + "_" + MAPPINGS[name]
					metricHelpText = "Sunny Value - Name: %s, Unit: %s" % (c['name'], c['unit'])
					metricValue = float(c['value'])

					m = GaugeMetricFamily(metricName, metricHelpText, labels=['device'])
					m.add_metric([d['name']], metricValue)
					metrics.append(m)
				except ValueError as e:
					pass

		for m in metrics:
			yield m

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--webbox_address', type=str, action='store', required=True)
	parser.add_argument('--webbox_password', type=str, action='store', default='')
	parser.add_argument('--listen_port', type=int, action='store', required=True)

	args = parser.parse_args()

	logger.info("inititalizing...")

	REGISTRY.register(SunnyWebboxCollector(args))
	logger.info("initialized collector")

	start_http_server(args.listen_port)
	logger.info("listening on http port {}".format(args.listen_port))

	while True:
		time.sleep(1)
