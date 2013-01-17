__author__ = 'ND'

import abc


class UserTask(object) :
	__metaclass__ = abc.ABCMeta
	__task_name__ = "AbstractUserTask"

	__key__ = None
	__title__ = None
	__repeat__ = False

	def __init__(self, key, title, repeat=False) :
		self.__key__ = key
		self.__title__ = title
		self.__repeat__ = repeat

	def key(self):
		return self.__key__

	def title(self):
		return self.__title__

	@abc.abstractproperty
	def can_repeat(self):
		return

	def repeats(self):
		return self.__repeat__

	@abc.abstractmethod
	def begin(self, *arguments):
		return

