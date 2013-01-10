
#__name__ = "Declare"

__author__ = "ND"

__doc__ = "Declare is designed as, among other things, an IoC container with simple programming interface and configuration.\n\nComponentManager class provides simple interface to resolve/instantiate components configured in PluginConfiguration object.\n\nPluginConfiguration can be configured programmatically (although it wouldn't make much sense) or via a JSON file that can be read via the 'read' static method."

import string
import json
import imp
import types
import inspect

class ComponentError(StandardError) :

	def __init__(self, *args, **kwargs):
		super(StandardError, self).__init__(args, kwargs)


class ComponentSpecificationError(ComponentError) :

	def __init__(self, *args, **kwargs):
		super(StandardError, self).__init__(args, kwargs)


class ComponentDeclaration(object) :
	__module_name__ = None
	__class_name__ = None
	__identifier__ = ""
	__lifetime__ = ""
	__init_args__ = None

	def __init__(self, identifier, moduleName, className, initArgs = None, lifetime = "") :
		"""
		identifier : String identifier of the component declaration.
		moduleName : Name of the module in which the component class can be found.
		className : Name of the component class.
		initArgs : A list or dictionary of arguments to be passed to the __init__ function when constructing a new instance of the class. This argument is optional and has default of None.
		lifetime : This argument specifies the lifetime of the declared component. This argument is only required to configure the component as a 'singleton'.
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

	def init_args(self) :
		return self.__init_args__


class Configuration(object) :

	__plugin_declarations__ = {}

	__string_formatter__ = string.Formatter()

	def __init__(self, componentDeclarations):
		"""
		Configuration can be created by providing a list of ComponentDeclaration object.
		"""

		for declaration in componentDeclarations :
			self.__plugin_declarations__[declaration.identifier()] = declaration

	def __getitem__(self, item):
		return self.__plugin_declarations__[item]

	def plugins(self):
		return self.__plugin_declarations__.itervalues()

	@staticmethod
	def read(filePath):
		"""
		filePath: Full path of file which contains the JSON configuration.

		Example of configuration file content:

			{
			    "component_specifications":
				{
			        "AddWordDefinitionTask": {
			            "class": "AddWordDefinitionTask",
			            "module": "StandardDictionaryUserTasks",
						"initArgs": {"repeat": true}
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
					}
				}
			}
		"""

		pluginDeclarations = []

		file = open(filePath, "r")

		try :
			configurationObject = json.load(file)
		except :
			raise
		finally :
			file.close()

		for identifier, specification in configurationObject["component_specifications"].iteritems() :

			className = specification["class"]
			moduleName = specification["module"]

			if specification.has_key("lifetime") :
				lifetime = specification["lifetime"]
			else :
				lifetime = ""

			if specification.has_key("initArgs") :
				initArgs = specification["initArgs"]
			else :
				initArgs = None

			pluginDeclarations.append(ComponentDeclaration(identifier, moduleName, className, initArgs, lifetime))

		return Configuration(pluginDeclarations)

class __Specification__(object) :

	__init_args__ = None
	__class__ = None

	def __init__(self, type, initArgs) :
		self.__class__ = type
		self.__init_args__ = initArgs

	def type(self) :
		return self.__class__

	def init_args(self) :
		return self.__init_args__


class Manager(object) :

	__configuration__ = None
	__plugin_modules__ = {}

	__singleton_components__ = {}
	__named_singleton_components__ = {}

	__plugin_specifications__ = {}
	__named_component_specifications__ = {}

	__format_string__ = string.Formatter().vformat

	def __is_reference_to_component__(self, value) :
		if type(value) is string :
			return value.startswith("{") and value.endswith("}")
		else :
			return False

	def __create_instance__(self, specification) :
		"""
		Create instance of a type based on a specification.
		"""
		instance = None

		expectedArguments = inspect.getargspec(specification.type().__init__)

		defaultsCount = len(expectedArguments.defaults) if expectedArguments.defaults != None else 0
		argumentsCount = len(specification.init_args()) if specification.init_args() != None else 0
		requiredArgumentsCount = len(expectedArguments.args) - (defaultsCount + 1)

		# raise an error if the number of arguments declared in specification is less than the number of non optional arguments required by the __init__ function
		if argumentsCount < requiredArgumentsCount :
			raise StandardError("Component declaration does not have enough init arguments")


		# Evaluate declared arguments.
		# Each declared argument can be evaluated to one of the following:
		# - None, which is represented by "{None}"
		# - Component, which is represented by "{componentDeclarationIdentifier}".
		#   The identified component will be resolved by either referencing a singleton component or creating a new instance of non singleton component
		#   An error will be raised if the no declaration can be found the the specified identifier
		# - Primitive types

		if type(specification.init_args()) == list : # if arguments are declared as list
			arguments = []

			for index in range(argumentsCount) : # evaluate each declared argument
				argument = specification.init_args()[index]

				if self.__is_reference_to_component__(argument) : # check that the argument is reference to another component
					componentName = argument.strip(["{", "}"])

					if componentName == "None" :
						arguments.append(None)
					elif self.__named_singleton_components__.has_key(componentName) : # check if singleton with specified identifier exists
						arguments.append(self.__named_singleton_components__[componentName])
					elif self.__named_component_specifications__.has_key(componentName) : # check if specification with specified identifier exists
						arguments.append(self.__create_instance__(self.__named_component_specifications__[componentName]))
					else :
						raise ComponentSpecificationError(self.__format_string__("Unable to find component '{componentName}' as init argument for {specification.__class__.__name__}, {specification.__class__.__module__}.", [], {"componentName": componentName, "specification": specification}))
				else:
					arguments.append(argument)

			instance = specification.type()(*arguments)

		elif type(specification.init_args()) == dict : # if arguments are declared as dictionary
			arguments = {}

			for name, value in specification.init_args().iteritems() : # evaluate each declared argument
				if not name in expectedArguments.args :
					raise ComponentError()

				if self.__is_reference_to_component__(value) : # check that the argument is reference to another component
					componentName = value.strip(["{", "}"])

					if componentName == "None" :
						arguments[name] = None
					elif self.__named_singleton_components__.has_key(componentName) :# check if singleton with specified identifier exists
						arguments[name] = self.__named_singleton_components__[componentName]
					elif self.__named_component_specifications__.has_key(componentName) : # check if specification with specified identifier exists
						arguments[name] = self.__create_instance__(self.__named_component_specifications__[componentName])
					else :
						raise ComponentSpecificationError(self.__format_string__("Unable to find component '{componentName}' as init argument for {specification.__class__.__name__}, {specification.__class__.__module__}.", [], {"componentName": componentName, "specification": specification}))
				else:
					arguments[name] = value

			instance = specification.type()(**arguments)
		else : # if (presumed) no arguments are specified
			instance = specification.type()()

		return instance

	def __registerSingleton__(self, type, instance) :

		if self.__singleton_components__.has_key(type) :
			pluginInstances = self.__singleton_components__[type]
		else :
			pluginInstances = []
			self.__singleton_components__[type] = pluginInstances

		pluginInstances.append(instance)

	def __registerSpecification__(self, type, specification) :

		if self.__plugin_specifications__.has_key(type) :
			specifications = self.__plugin_specifications__[type]
		else :
			specifications = []
			self.__plugin_specifications__[type] = specifications

		if not specification in specifications :
			specifications.append(specification)

	def __processSingletonDeclaration__(self, declaration, pluginClass) :
		"""
		Create and register component specification for future instantiation
		"""
		pluginInstance = self.__create_instance__(__Specification__(pluginClass, declaration.init_args()))

		self.__named_singleton_components__[declaration.identifier] = pluginInstance
		self.__registerSingleton__(pluginClass, pluginInstance)

		for base in pluginClass.__bases__ :
			if base == object :
				continue

			self.__registerSingleton__(base, pluginInstance)

	def __processNonSingletonDeclaration__(self, declaration, pluginClass) :
		"""
		Create and register instance of the component
		"""
		specification = __Specification__(pluginClass, declaration.init_args())
		self.__named_component_specifications__[declaration.identifier] = specification

		self.__registerSpecification__(pluginClass, specification)

		for base in pluginClass.__bases__ :
			if base == object :
				continue

			self.__registerSpecification__(base, specification)

	def __processDeclaration__(self, declaration) :
		"""
		Create specification or component instance based on declaration

		"""
		if self.__plugin_modules__.has_key(declaration.module_name()) : # if module has been loaded before
			pluginModule = self.__plugin_modules__[declaration.module_name()]
		else : # otherwise load and cache module
			moduleInfo = imp.find_module(declaration.module_name()) #possible ImportError
			pluginModule = imp.load_module(declaration.module_name(), moduleInfo[0], moduleInfo[1], moduleInfo[2]) #possible exception
			self.__plugin_modules__[declaration.module_name()] = pluginModule

		if not hasattr(pluginModule, declaration.class_name()) : # check that module has attribute with name equals to declared class name
			raise ComponentError(self.__format_string__("Unable to find class '{class}' in modules '{module}' for plugin: '{plugin}'", [], {"class": declaration.class_name(), "module": declaration.module_name(), "plugin": declaration.identifier()}) )

		componentClass = getattr(pluginModule, declaration.class_name())

		if not isinstance(componentClass, (type, types.ClassType)) : # check that the identified module attribute is a class
			raise ComponentError(self.__format_string__("'{class}' is not a class in modules '{module}' for plugin: '{plugin}'", [], {"class": declaration.class_name(), "module": declaration.module_name(), "plugin": declaration.identifier()}) )

		if declaration.lifetime() == "singleton" :
			self.__processSingletonDeclaration__(declaration, componentClass)
		else:
			self.__processNonSingletonDeclaration__(declaration, componentClass)

	def __init__(self, configuration) :
		"""
		Initiate ComponentManager with a Configuration object
		"""
		self.__configuration__ = configuration

		for declaration in configuration.plugins() :
			self.__processDeclaration__(declaration)

	def get_components_of_type(self, type, lifetime="all") :
		"""
		Get components which are instances of or inherits specified type.

		Lifetime can be one of the following:
		- all
		- singleton
		- <empty string>
		"""
		components = []

		if (lifetime == "all" or lifetime == "singleton") and self.__singleton_components__.has_key(type ):
			for component in self.__singleton_components__[type] :
				components.append(component)

		if (lifetime == "all" or lifetime != "singleton") and self.__plugin_specifications__.has_key(type) :
			for specification in self.__plugin_specifications__[type] :
				components.append(self.__create_instance__(specification))

		return components

	def get_component(self, identifier) :
		"""
		Get component with specified identifier
		"""
		component = None

		if self.__named_singleton_components__.has_key(identifier) :
			component = self.__named_singleton_components__[identifier]
		elif self.__named_component_specifications__.has_key(identifier) :
			component = self.__create_instance__(self.__named_component_specifications__[identifier])

		return component