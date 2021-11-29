# Custom JSON Op Standard (CJOS-01)

### IDs

Applications or protocols use a single ID to broadcast their `custom_json` ops.

For example:

- `community`: Hivemind communities protocol
- `notify`: blockchain-wide notification protocol
- `follow`: blockchain-wide follower protocol
- `3speak`: 3Speak application

### Op JSON Data Structure

```
[
    [1, "app_name/version"],      dictionary
    "op_internal_name",         string(64)
    {} or []                    dictionary/list
]
```

Ops are broadcast using an array as the main container in the `json` field.

- The first element contains the `header` which can contain application-specific metadata such as:
    - `ver` [int]: the version of the op, within the application/protocol
    - `app` [string]: the name of the app, version info, etc

- The second element contains the internal name of the operation. [string (64)]

- The third element contains the actual data that the application/protocol uses, in one of two formats:
    - a JSON object (dictionary), or
    - an array/list
