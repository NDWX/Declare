__author__ = 'ND'

import unittest
import Declare


from TestModel import UserTask

class ManagerTests(unittest.TestCase):
	"""
	Declare.Manager test scenarios
	"""

	_manager_ = None

	def setUp(self):
		"""
		read configuration and create manager
		"""
		configuration = Declare.Configuration.read("configuration.json")
		self._manager_ = Declare.Manager(configuration)

	def test_singleton_by_type(self):
		"""
		check that singleton of specific type or base type exists
		"""
		tasks = self._manager_.get_components_of_type(UserTask, "singleton")

		self.assertTrue(len(tasks) == 1 and tasks[0].__task_name__ == "ListWordDefinitionsTask")

	def test_non_singleton_by_type(self):
		"""
		check that retrieving non singleton by type returns correct result
		"""
		tasks = self._manager_.get_components_of_type(UserTask, "")

		tasksFound = []

		for task in tasks:
			tasksFound.append(task.__task_name__)

		self.assertTrue(len(tasksFound) == 2 and "AddWordDefinitionTask" in tasksFound and "RemoveWordDefinitionTask" in tasksFound)

	def test_component_by_identifier(self):
		"""
		check that all components are obtainable by identifier
		"""
		addWordTask = self._manager_.get_component("AddWordDefinitionTask")
		listWordsTask = self._manager_.get_component("ListWordDefinitionsTask")
		removeWordTask = self._manager_.get_component("RemoveWordDefinitionTask")

		self.assertTrue(not (addWordTask is None or listWordsTask is None or removeWordTask is None))

	def test_component_init_argument_correctness(self):
		"""
		check that components declared with init args has correct init args
		"""
		addWordTask = self._manager_.get_component("AddWordDefinitionTask")
		removeWordTask = self._manager_.get_component("RemoveWordDefinitionTask")

		self.assertTrue(addWordTask.Repeats() == True and removeWordTask.Repeats() == False)


if __name__ == '__main__':
	unittest.main()
