__author__ = 'ND'

import unittest
import Declare

class MyTestCase(unittest.TestCase):

	_configuration_ = None

	def setUp(self):
		self._configuration_ = Declare.Configuration.read("configuration.json")

if __name__ == '__main__':
	unittest.main()
