__author__ = 'ND'

from TestModel import UserTask

class ListWordDefinitionsTask(UserTask) :

	__task_name__ = "ListWordDefinitionsTask"

	def __init__(self) :
		super(ListWordDefinitionsTask, self).__init__("l", "List word definitions", False)
		self.name = "ListWordDefinitionTask"

	def begin(self, wordDefinitions, *arguments) :
		if len(wordDefinitions) == 0 :
			print "No definition found"
		else :
			for word in wordDefinitions.keys() :
				print word, ": ", wordDefinitions[word]

	def can_repeat(self):
		return False


class AddWordDefinitionTask(UserTask) :

	__task_name__ = "AddWordDefinitionTask"

	def __init__(self, repeat = False) :
		super(AddWordDefinitionTask, self).__init__("a", "Add word definition", repeat)
		self.name = "AddWordDefinitionTask"

	def can_repeat(self):
		return True

	def begin(self, wordDefinitions, *arguments) :
		newWord = raw_input("Word : ")

		if newWord != "" :
			definition = raw_input("Definition : ")
			wordDefinitions[newWord] = definition


class RemoveWordDefinitionTask(UserTask) :

	__task_name__ = "RemoveWordDefinitionTask"

	def __init__(self, repeat = False) :
		super(RemoveWordDefinitionTask, self).__init__("r", "Remove word definition", repeat)
		self.name = "RemoveWordDefinitionTask"

	def can_repeat(self):
		return True

	def begin(self, wordDefinitions, *arguments) :

		wordToDelete = raw_input("Word : ")

		if wordToDelete != "" :
			if wordDefinitions.has_key(wordToDelete) :
				del wordDefinitions[wordToDelete]
				print "\"" + wordToDelete + "\"", "has been deleted"
			else :
				print "\"" + wordToDelete + "\"", "is not defined"

