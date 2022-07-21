# Defining your plug's defs.json

The `defs.json` file is used to setup your plug. Below is an example file used by the `podping` plug:

```
{
    "name": "podping",
    "props":{
        "enabled": true,
        "schema": "podping",
        "context": "podping",
        "start_block": 53690004
    },
    "ops": {"18": "podping.process_cjop"}
}
```

- `name`: your plug's internal name (must match the subdirectory name used in the codebase also)
- `props`: the properties of your plug
    - `enabled`: the default state of the plug (on or off)
    - `schema`: the name to use for the PostgreSQL schema that holds all your plug's data
    - `context`: the name to use for the HAF context
    - `start_block`: at which block should sync begin
- `ops`: HAF internal operation IDs and their mapped functions for processing
    - `18` is for `custom_json` operations
    - the name of the function should be in the format `schema`.`function_name`
    - there should be **no duplicate operation IDs** and only one function mapping per ID