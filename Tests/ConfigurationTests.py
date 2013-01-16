__author__ = 'ND'

import unittest
import Declare

class ConfigurationTestCase(unittest.TestCase):

	_configuration_ = None

	def setUp(self):
		self._configuration_ = Declare.Configuration.read("configuration.json")

	def test_successful_read(self):
		self.assertTrue(self._configuration_ is not None)

	def test_resource_exists(self):
		self.assertTrue(self._configuration_.resources().has_key("RepeatableTaskRepeat"))

	def test_resource_value(self):
		self.assertTrue(self._configuration_.resources()["RepeatableTaskRepeat"] == True)

	def test_component_specifications_exist(self):
		self.assertTrue(not (self._configuration_["AddWordDefinitionTask"] is None
		                     or self._configuration_["ListWordDefinitionsTask"] is None or
		                     self._configuration_["RemoveWordDefinitionTask"] is None))

	def test_component_class_and_module(self):
		self.assertTrue(self._configuration_["AddWordDefinitionTask"].class_name() == "AddWordDefinitionTask" and
		                self._configuration_["AddWordDefinitionTask"].module_name() == "TestModel")

	def test_component_specifications_init_arg_list(self):
		self.assertTrue("{$RepeatableTaskRepeat}" in self._configuration_["AddWordDefinitionTask"].init_args() )

	def test_component_specifications_init_arg_dict(self):
		init_args = self._configuration_["RemoveWordDefinitionTask"].init_args()
		self.assertTrue(init_args.has_key("repeat") and init_args["repeat"] == "{$RepeatableTaskRepeat}")

	def test_component_specification_lifetime_declaration(self):
		self.assertTrue(self._configuration_["ListWordDefinitionsTask"].lifetime() == "singleton")

	def test_component_specification_lifetime_non_declaration(self):
		self.assertTrue(self._configuration_["RemoveWordDefinitionTask"].lifetime() == "")

if __name__ == '__main__':
	unittest.main()
