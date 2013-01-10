# Declare

IoC container module for Python with simple programming and configuration interface

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
		    "component_specifications":
				{
			        "AddWordDefinitionTask":
              {
			            "class": "AddWordDefinitionTask",
			            "module": "StandardDictionaryUserTasks",
                  "initArgs": [true]
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
  					      "lifetime": "singleton",
  					      "initArgs": {"repeat": true}
					    }
				}
}
```

The sample above declared three components:
* *AddWordDefinitionTask* is of type `AddWordDefinitionTask` that can be found in `StandardDictionaryUserTasks` module. This component will be initialized with one argument `True`.
* *ListWordDefinitionsTask* is of type `ListWordDefinitionTask` that can be found in `StandardDictionaryUserTasks` module and it is also a singleton.
* *RemoveWordDefinitionTask* is a singleton component of of type `RemoveWordDefinitionTask` that can be found in `StandardDictionaryUserTasks` module. This component will be initialized with one named argument. 
