#__name__ = "Declare"

__author__ = "ND"

__doc__ = 'Declare is designed as, among other things, an IoC container with simple programming interface and configuration.ComponentManager class provides simple interface to resolve/instantiate components configured inPluginConfiguration object. PluginConfiguration can be configured programmatically (although it would not make much sense) or via a JSON file that can be read via the \'read\' static method.'

import string
import json
import imp
import types
import inspect


class ComponentError(StandardError):
	def __init__(self, *args, **kwargs):
		super(StandardError, self).__init__(args, kwargs)


class ComponentSpecificationError(ComponentError):
	def __init__(self, *args, **kwargs):
		super(StandardError, self).__init__(args, kwargs)


class ComponentDeclaration(object):

	def __init__(self, identifier, moduleName, className, initArgs=None, lifetime=""):
		"""
		identifier: String identifier of the component declaration.
		moduleName: Name of the module in which the component class can be found.
		className: Name of the component class.
		initArgs : A list or dictionary of arguments to be passed to the __init__ function when
		constructing a new instance of the class. This argument is optional and has default of None.
		lifetime : This argument specifies the lifetime of the declared component.
		This argument is only required to configure the component as a 'singleton'.
		"""
		self.__module_name__ = moduleName
		self.__class_name__ = className
		self.__identifier__ = identifier
		self.__init_args__ = initArgs
		self.__lifetime__ = lifetime

	def identifier(self):
		return self.__identifier__

	def module_name(self):
		return self.__module_name__

	def class_name(self):
		return self.__class_name__

	def lifetime(self):
		return self.__lifetime__

	def init_args(self):
		return self.__init_args__


class Configuration(object):
	__string_formatter__ = string.Formatter()

	def __init__(self, resourceDeclarations, componentDeclarations):
		"""
		Configuration can be created by providing a list of ComponentDeclaration object.
		"""
		self.__resource_declarations__ = resourceDeclarations
		self.__plugin_declarations__ = {}

		for declaration in componentDeclarations:
			self.__plugin_declarations__[declaration.identifier()] = declaration

	def __getitem__(self, item):
		plugin = None

		if item in self.__plugin_declarations__.keys():
			plugin = self.__plugin_declarations__[item]

		return plugin

	def plugins(self):
		return self.__plugin_declarations__.itervalues()

	def resources(self):
		return self.__resource_declarations__

	@staticmethod
	def read(filePath):
		"""
		filePath: Full path of file which contains the JSON configuration.

		Example of configuration file content:

		{
			"resources":
			{
				"RepeatableTaskRepeat": true
			},
			"component_specifications":
			{
				"AddWordDefinitionTask":
				{
					"class": "AddWordDefinitionTask",
					"module": "StandardDictionaryUserTasks",
					"initArgs": "{$RepeatableTaskRepeat}"
				},
				"ListWordDefinitionsTask":
				{
					"class": "ListWordDefinitionsTask",
					"module": "StandardDictionaryUserTasks",
					"lifetime": "singleton"
				},
				"RemoveWordDefinitionTask":
				{
					"class": "RemoveWordDefinitionTask",
					"module": "StandardDictionaryUserTasks"
					"initArgs": "{$RepeatableTaskRepeat}"
				}
			}
		}
		"""
		resourceDeclarations = {}
		pluginDeclarations = []

		file = open(filePath, "r")

		try:
			configurationObject = json.load(file)
		except:
			raise
		finally:
			file.close()

		if "resources" in configurationObject.keys():
			resourceDeclarations = configurationObject["resources"]

		for identifier, specification in configurationObject["component_specifications"].iteritems():
			className = specification["class"]
			moduleName = specification["module"]

			if "lifetime" in specification.keys():
				lifetime = specification["lifetime"]
			else:
				lifetime = ""

			if "initArgs" in specification.keys():
				initArgs = specification["initArgs"]
			else:
				initArgs = None

			pluginDeclarations.append(ComponentDeclaration(identifier, moduleName, className, initArgs, lifetime))

		return Configuration(resourceDeclarations, pluginDeclarations)


class __Specification__(object):

	def __init__(self, type, initArgs):
		self.__plugin_class__ = type
		self.__init_args__ = initArgs

	def type(self):
		return self.__plugin_class__

	def init_args(self):
		return self.__init_args__


class Manager(object):

	__format_string__ = string.Formatter().vformat

	def __is_reference_to_component__(self, value):
		# component is identified by the following format: {name}
		return value.startswith("{") and value.endswith("}")

	def __is_reference_to_resource__(self, value):
		# resource is identified by the following format: {$name}
		return value.startswith("{$") and value.endswith("}")

	def __resolve_init_argument__(self, value, specification):
		# default resolved argument to 'value' as is
		resolvedArgument = value

		# if resource value is string, it could be just a string or reference to either resource or component
		if type(value) == unicode:
			if self.__is_reference_to_resource__(value):

				resourceName = value.strip('{$}')

				if resourceName == "None":
					# if resource value is {$None}
					resolvedArgument = None
				if resourceName in self.__configuration__.resources().keys():
					# if resource with specified identifier exists (was declared)
					resolvedArgument = self.__configuration__.resources()[resourceName]
				else:
					# if specified resource not found
					raise ComponentSpecificationError(self.__format_string__(
								"Unable to find resource '{resourceName}'"
								"as init argument for {specification.__class__.__name__},"
								"{specification.__class__.__module__}.",
								[], {"resourceName": resourceName, "specification": specification}))

			elif self.__is_reference_to_component__(value):

				componentName = value.strip(['{}'])

				# if singleton with specified identifier exists
				if componentName in self.__named_singleton_components__.keys():
					resolvedArgument = self.__named_singleton_components__[componentName]
				elif componentName in self.__named_component_specifications__.keys():
					# if specification with specified identifier exists
					resolvedArgument = self.__create_instance__(self.__named_component_specifications__[componentName])
				else:
					raise ComponentSpecificationError(self.__format_string__(
						"Unable to find component '{componentName}' as"
						"init argument for {specification.__class__.__name__}, {specification.__class__.__module__}.",
						[], {"componentName": componentName, "specification": specification}))

		return resolvedArgument

	def __create_instance__(self, specification):
		"""
		Create instance of a type based on a specification.
		:rtype: object
		"""
		#instance = None

		expectedArguments = inspect.getargspec(specification.type().__init__)

		defaultsCount = len(expectedArguments.defaults) if expectedArguments.defaults is not None else 0
		argumentsCount = len(specification.init_args()) if specification.init_args() is not None else 0
		requiredArgumentsCount = len(expectedArguments.args) - (defaultsCount + 1)

		# raise an error if the number of arguments declared in specification is less than the number of
		# non optional arguments required by the __init__ function
		if argumentsCount < requiredArgumentsCount:
			raise StandardError("Component declaration does not have enough init arguments")

		# Evaluate declared arguments.
		# Each declared argument can be evaluated to one of the following:
		# - None, which is represented by "{$None}"
		# - Component, which is represented by "{componentDeclarationIdentifier}".
		#   The identified component will be resolved by either referencing a singleton component or
		#   creating a new instance of non singleton component
		#   An error will be raised if the no declaration can be found the the specified identifier
		# - Primitive types

		# if arguments are declared as list
		if type(specification.init_args()) == list:
			arguments = []

			# evaluate each declared argument
			for index in range(argumentsCount):
				argument = specification.init_args()[index]
				arguments.append(self.__resolve_init_argument__(argument, specification))

			instance = specification.type()(*arguments)

		elif type(specification.init_args()) == dict:
			# if arguments are declared as dictionary
			arguments = {}

			# evaluate each declared argument
			for name, value in specification.init_args().iteritems():
				# if declared argument name is not in init argument list
				if not name in expectedArguments.args:
					raise ComponentError()

				arguments[name] = self.__resolve_init_argument__(value, specification)

			instance = specification.type()(**arguments)
		else:
			# if (presumed) no arguments are specified
			instance = specification.type()()

		return instance

	def __register_singleton__(self, type, instance):
		# get list (object) of singletons for 'type'
		if type in self.__singleton_components__.keys():
			pluginInstances = self.__singleton_components__[type]
		else:
			pluginInstances = []
			self.__singleton_components__[type] = pluginInstances

		pluginInstances.append(instance)

	def __register_specification__(self, type, specification):
		# get list (object) of specifications for 'type'
		if type in self.__plugin_specifications__.keys():
			specifications = self.__plugin_specifications__[type]
		else:
			specifications = []
			self.__plugin_specifications__[type] = specifications

		# if specification is not known for type
		if not specification in specifications:
			specifications.append(specification)

	def __register_singleton_by_type__(self, component, pluginClass, knownTypes=None):

		if knownTypes is None:
			knownTypes = []
		else:
			if pluginClass in knownTypes:
				return

		self.__register_singleton__(pluginClass, component)

		knownTypes.append(pluginClass)

		for base in pluginClass.__bases__:
			if base == object:
				continue

			self.__register_singleton_by_type__(component, base, knownTypes)

	def __processSingletonDeclaration__(self, declaration, pluginClass):
		"""
		Create and register component specification for future instantiation
		"""
		pluginInstance = self.__create_instance__(__Specification__(pluginClass, declaration.init_args()))

		self.__named_singleton_components__[declaration.identifier()] = pluginInstance

		self.__register_singleton_by_type__(pluginInstance, pluginClass)

#		self.__registerSingleton__(pluginClass, pluginInstance)
#
#		for base in pluginClass.__bases__:
#			if base == object:
#				continue
#
#			self.__registerSingleton__(base, pluginInstance)

	def __processNonSingletonDeclaration__(self, declaration, pluginClass):
		"""
		Create and register instance of the component
		"""
		specification = __Specification__(pluginClass, declaration.init_args())
		self.__named_component_specifications__[declaration.identifier()] = specification

		self.__register_specification__(pluginClass, specification)

		for base in pluginClass.__bases__:
			if base == object:
				continue

			self.__register_specification__(base, specification)

	def __processDeclaration__(self, declaration):
		"""
		Create specification or component instance based on declaration
		"""
		self.__plugin_specifications__.values()

		# if module has been loaded before
		if declaration.module_name() in self.__plugin_modules__.keys():
			pluginModule = self.__plugin_modules__[declaration.module_name()]
		else:
		# otherwise load and cache module
			moduleInfo = imp.find_module(declaration.module_name())
			pluginModule = imp.load_module(declaration.module_name(), moduleInfo[0], moduleInfo[1], moduleInfo[2])
			self.__plugin_modules__[declaration.module_name()] = pluginModule

		# check that module has attribute with name equals to declared class name
		if not hasattr(pluginModule, declaration.class_name()):
			raise ComponentError(
				self.__format_string__("Unable to find class '{class}' in modules '{module}' for plugin: '{plugin}'",
					[], {"class": declaration.class_name(), "module": declaration.module_name(),
						"plugin": declaration.identifier()}))

		componentClass = getattr(pluginModule, declaration.class_name())

		# check that the identified module attribute is a class
		if not isinstance(componentClass, (type, types.ClassType)):
			raise ComponentError(
				self.__format_string__("'{class}' is not a class in modules '{module}' for plugin: '{plugin}'", [],
				{"class": declaration.class_name(), "module": declaration.module_name(),
					"plugin": declaration.identifier()}))

		if declaration.lifetime() == "singleton":
			self.__processSingletonDeclaration__(declaration, componentClass)
		else:
			self.__processNonSingletonDeclaration__(declaration, componentClass)

	def __init__(self, configuration):
		"""
		Initiate ComponentManager with a Configuration object
		"""
		self.__configuration__ = configuration
		self.__plugin_modules__ = {}

		self.__singleton_components__ = {}
		self.__named_singleton_components__ = {}

		self.__plugin_specifications__ = {}
		self.__named_component_specifications__ = {}

		for declaration in configuration.plugins():
			self.__processDeclaration__(declaration)

	def register(self, component, identifier=""):
		"""
		Register singleton component with specified optional identifier
		"""
		if len(identifier) > 0:
			self.__singleton_components__[identifier] = component

		self.__register_singleton_by_type__(component, component.__class__)


	def get_components_of_type(self, type, lifetime="all"):
		"""
		Get components which are instances of or inherits specified type.

		Lifetime can be one of the following:
		- all
		- singleton
		- <empty string>
		"""
		components = []

		# if singleton is requested and identified component is singleton
		if lifetime == "all" or lifetime == "any" or lifetime == "singleton":
			if type in self.__singleton_components__.keys():
				# gather all instances of specified type or types inheriting specified type
				for component in self.__singleton_components__[type]:
					components.append(component)

		if lifetime == "all" or lifetime == "any" or lifetime != "singleton":
			if type in self.__plugin_specifications__.keys():
				# create and gather instances of specified type or types inheriting specified type
				for specification in self.__plugin_specifications__[type]:
					components.append(self.__create_instance__(specification))

		return components

	def get_component(self, identifier):
		"""
		Get component with specified identifier
		"""
		component = None

		# if identified component is singleton
		if identifier in self.__named_singleton_components__.keys():
			# retrieve component from singleton dictionary
			component = self.__named_singleton_components__[identifier]
		elif identifier in self.__named_component_specifications__.keys():
			# create instance of identified component
			component = self.__create_instance__(self.__named_component_specifications__[identifier])

		return component
