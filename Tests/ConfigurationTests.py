__author__ = 'ND'

import unittest
import Declare


class ConfigurationTestCase(unittest.TestCase):
	"""
	Test configuration reader
	"""

	_configuration_ = None

	def setUp(self):
		"""
		read configuration from 'configuration.json'
		"""
		self._configuration_ = Declare.Configuration.read("configuration.json")

	def test_successful_read(self):
		"""
		check that configuration was successfully read
		"""
		self.assertTrue(self._configuration_ is not None)

	def test_resource_exists(self):
		"""
		check that a declared resource exists
		"""
		self.assertTrue(self._configuration_.resources().has_key("AddWordTaskRepeat") and self._configuration_.resources().has_key("RemoveWordTaskRepeat"))

	def test_resource_value(self):
		"""
		check resource value is as expected
		"""
		self.assertTrue(self._configuration_.resources()["RemoveWordTaskRepeat"] == False)

	def test_component_specifications_exist(self):
		"""
		check all specified component exists
		"""
		self.assertTrue(not (self._configuration_["AddWordDefinitionTask"] is None
		                     or self._configuration_["ListWordDefinitionsTask"] is None or
		                     self._configuration_["RemoveWordDefinitionTask"] is None))

	def test_component_class_and_module(self):
		"""
		check specified component has correct class and module name
		"""
		self.assertTrue(self._configuration_["AddWordDefinitionTask"].class_name() == "AddWordDefinitionTask" and
		                self._configuration_["AddWordDefinitionTask"].module_name() == "TestModel")

	def test_component_specifications_init_arg_list(self):
		"""
		check specified component has correct __init__ argument list
		"""
		self.assertTrue("{$AddWordTaskRepeat}" in self._configuration_["AddWordDefinitionTask"].init_args() )

	def test_component_specifications_init_arg_dict(self):
		"""
		check specified component uses dictionary argument list and that it contains contains specific argument name with specific value
		"""
		init_args = self._configuration_["RemoveWordDefinitionTask"].init_args()

		self.assertTrue(type(init_args) == dict and init_args.has_key("repeat") and init_args["repeat"] == "{$RemoveWordTaskRepeat}")

	def test_component_specification_lifetime_declaration(self):
		"""
		check that specific component specification has correct lifetime declaration
		"""
		self.assertTrue(self._configuration_["ListWordDefinitionsTask"].lifetime() == "singleton")

	def test_component_specification_lifetime_non_declaration(self):
		"""
		check that specific component specification has correct lifetime non-declaration
		"""
		self.assertTrue(self._configuration_["RemoveWordDefinitionTask"].lifetime() == "")

if __name__ == '__main__':
	unittest.main()
