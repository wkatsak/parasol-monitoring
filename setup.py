from __future__ import print_function

from setuptools import setup, find_packages

setup(
	name="parasol_monitoring",
	version="0.1",
	description="Parasol Monitoring Scripts (Prometheus Exporters)",
	author="William Katsak <wkatsak@cs.rutgers.edu>",
	packages=find_packages(),
	install_requires=["prometheus_client"],
	entry_points= {
		'console_scripts' : [
			'sunny_exporter = parasol_monitoring.exporters.sunny_exporter:main'
		]
	}
)
