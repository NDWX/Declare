# Declare
IoC container module for Python with simple programming and configuration interface.

Declare enables implementation of extension-point/plugin in Python applications.

## Features

* Simple configuration file with JSON
* Specification of __init__ parameters in configuration
* Support of component/object reference by identifier for __init__ parameters
* Resolve components/objects by identifier
* Resolve components/objects by type, including class type and base types
* Singleton support

## Configuration file

Sample configuration file:

```json
{
	"resources" :
	{
		"RepeatableTaskRepeat": true
	},
	"component_specifications":
	{
		"AddWordDefinitionTask": {
			"class": "AddWordDefinitionTask",
			"module": "StandardDictionaryUserTasks",
			"initArgs": ["{$RepeatableTaskRepeat}"]
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
			"module": "StandardDictionaryUserTasks",
			"initArgs": 
			{
				"repeat": "{$RepeatableTaskRepeat}"
			}
		}
	}
}
```

The sample above declared three components:
* *AddWordDefinitionTask* is of type `AddWordDefinitionTask` that can be found in `StandardDictionaryUserTasks` module. This component will be initialized with one argument `True`.
* *ListWordDefinitionsTask* is of type `ListWordDefinitionTask` that can be found in `StandardDictionaryUserTasks` module and it is also a singleton.
* *RemoveWordDefinitionTask* is a singleton component of of type `RemoveWordDefinitionTask` that can be found in `StandardDictionaryUserTasks` module. This component will be initialized with one named argument. 

## Usage

Objects declared in the configuration file can be resolved through an instance of `Manager` object which can be instantiated by passing an instance of `Configuration` object as follow:
```python
import Declare

configuration = Declare.Configuration.Read(pathToJsonFile)
manager = Declare.Manager(configuration)
```

To resolve components of a type or components that inherits/implement a type :
```python
components = manager.get_components_of_type(type=UserTask, lifetime="all")
```

The `get_components_of_type` function returns a list of objects that are either instance of or instance of a type that inherits/implements specified type. This function takes two arguments:
* `type` : type of class or base class
* `lifetime` : optional component lifetime filter. This argument defaults to `"all"`. Other options include `"singleton"` and `""`

To obtain a component by its identifier:
```python
component = manager.get_component(identifier="RemoveWordDefinitionTask")
```

The `get_component` function accepts an identifier of an object as declared in the configuration file and return an object or `None` if the identifier is not found.
