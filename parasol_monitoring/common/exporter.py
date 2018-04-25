from argparse import ArgumentParser
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY
import logging
import sys
import time

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

class ParasolCollectorException(Exception):
	pass

class ParasolCollectorBase(object):
	name = "Unnamed Collector"

	def __init__(self, args):
		self.args = args

	def collect(self):
		raise ParasolCollectorException("This class is intended to be abstract, please subclass it first.")

class ParasolMetricExporter(object):
	DEFAULT_NAME = "Unnamed Exporter"

	def __init__(self, name=DEFAULT_NAME):
		self.name = name

		self.parser = ArgumentParser()
		self.parser.add_argument("--port", type=int, action="store", required=True)

		self.collector_classes = []

	def _parse_args(self):
		self.args = self.parser.parse_args()

	def add_argument(self, *args, **kwargs):
		self.parser.add_argument(*args, **kwargs)

	def add_collector(self, collector_class):
		assert issubclass(collector_class, ParasolCollectorBase)
		self.collector_classes.append(collector_class)

	def start(self):
		assert len(self.collector_classes) > 0
		self._parse_args()

		logger.info("Initializing {}...".format(self.name))
		for collector_class in self.collector_classes:
			collector = collector_class(self.args)
			REGISTRY.register(collector)
			logger.info("...initialized {}".format(collector.name))

		start_http_server(self.args.port)
		logger.info("READY: HTTP server listening on port {}".format(self.args.port))

		while True:
			time.sleep(1)
