from ..common.exporter import ParasolCollectorBase, ParasolMetricExporter
from ..deps.cooling import TKS3000
from prometheus_client.core import GaugeMetricFamily

class TKS3000Collector(ParasolCollectorBase):
	name = "TKS3000 Collector"

	VALUE_NAME_PREFIX = "cooling"

	VALUE_NAME_MAPPINGS = {
		'TempIndoor' : 'temp_inside',
		'TempOutdoor' : 'temp_outside',
		'TempSetCooling' : 'control_setpoint_cooling',
		'TempSetHeating' : 'control_setpoint_heating',
		'TempPBand' : 'control_pband',
		'FanSpeed': 'control_fan_speed',
		'MaxFanSpeed': 'control_max_fan_speed',
		'TempDiffAC' : 'control_ac_diff',
		'TempDeltaAC' : 'control_ac_delta',
		'StateAC': 'state_ac',
		'StateHeater' : 'state_heater',
		'StateDamper' : 'state_damper',
	}

	def collect(self):
		tks3000 = TKS3000(self.args.serial_port)
		data = tks3000.getTKSValues()

		metrics = []

		for key in data:
			if key not in self.VALUE_NAME_MAPPINGS:
				continue

			metricName = "{}_{}".format(self.VALUE_NAME_PREFIX, self.VALUE_NAME_MAPPINGS[key])
			metricHelpText = "{} from TKS3000".format(key)
			metricValue = data[key]

			m = GaugeMetricFamily(metricName, metricHelpText)
			m.add_metric([], metricValue)
			metrics.append(m)

		for m in metrics:
			yield m

def main():
	exporter = ParasolMetricExporter(name="Cooling Exporter")
	exporter.add_argument("--serial_port", type=str, action="store", required=True)
	exporter.add_collector(TKS3000Collector)
	exporter.start()

if __name__ == "__main__":
	main()
