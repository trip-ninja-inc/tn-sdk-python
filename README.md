# TripNinja SDK

The TripNinja Python SDK is used for interacting with the TripNinjaAPI 
through a easy-to-use library and suite of tools.

## Installing

**Python 3.10 or higher is required**

### Linux/MacOS
`python3 -m pip install -U tn_sdk`

### Windows
`py -3 -m pip install -U tn_sdk`


## Quick Example

```python
import tn_sdk

tn_client = tn_sdk.TnApi()
request_data = "{}" # JSON encoded string representing the request data
compressed_data = tn_client.prepare_data_for_generate_solutions(request_data)
# Compresses the data and returns the compressed_data
```


---


# Development

## Setup

From an active virtual env, `cd` into the directory
``pip install -e .``

> `-e` installs it in [editable](https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs) mode. 
> Meaning it will update as you modify the source code without having to re-run the installation command.
