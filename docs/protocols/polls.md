# Polls Protocol Documentation

## Version 1


### create

*Create a new poll*

Op structure:

```
[
    [op_version <int>, app_name/app_version <string>],
    "create",
    {
        "permlink": <string> (255),
        "question": <string> (255),
        "answers": [<string> (128), <string> (128), <string> (128)],
        "expires": UTC_TIMESTAMP <string>,
        "tag": <string> (16)
    }
]
```


Example op:

```
[
    [1, "polls-app/0.01"],
    "create",
    {
        "permlink": "this-is-a-test",
        "question": "What do you think Hive's price will be next year?",
        "answers": ["$1.00", "$2.00", "$5.00", "$10.00"],
        "expires": "2021-12-04 13:54:06",
        "tag": "hive-133333"
    }
]
```

### vote

*Vote on a poll*

Op structure:

```
[
    [op_version <int>, app_name/app_version <string>],
    "vote",
    {
        "author": <string> (16),
        "permlink": <string> (255)
    }
]
```

Example op:

```
[
    [1, "polls/0.01"],
    "vote",
    {
        "author": "",
        "permlink": ""
    }
]
```