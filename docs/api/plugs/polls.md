# Polls Plug

Endpoints for the polls protocol

**Production Server:** https://plug-play.imwatsi.com

**Dev Server:** https://plug-play-beta.imwatsi.com

---

### get_poll_permlink

*Returns a valid and unique permlink to use with a new poll.*

**Params:**

- `author`:         <string (16)>
- `question`:       <string (255)>

**Example payload:**

```
{
    "jsonrpc": "2.0",
    "method": "plug_play_api.polls.get_poll_permlink",
    "params": {
            "author": "imwatsi",
            "question": "What do you think Hive's price will be next year?"
        },
    "id": 1
}
```

**Example response:**

```
{
    "jsonrpc": "2.0",
    "result": "what-do-you-think-hives-price-will-be",
    "id": 1
}
```

### get_polls_ops

*Returns a list of polls ops within the specified block range (or last 24 hours if not specified)*

**Params:**

- `op_type`:      <string(16)> (optional)
- `block_range`:    [lower, upper] (optional, default=28800 blocks from latest)

**Example payload:**

```
{
    "jsonrpc": "2.0",
    "method": "plug_play_api.polls.get_polls_ops",
    "params": {
            "block_range": [1,60129000]
        },
    "id": 1
}
```

**Example response:**

```
{
    "jsonrpc": "2.0",
    "result": [
        {
            "transaction_id": "87254b594dc80db2b8cbe6faefb380685836ce9b",
            "req_posting_auths": [
                "imwatsi.test"
            ],
            "op_type": "create",
            "op_payload": {
                "permlink": "what-do-you-think",
                "question": "What do you think Hive's price will be next year?",
                "answers": [
                    "$1.00",
                    "$2.00",
                    "$5.00",
                    "$10.00"
                ],
                "expires": "2021-12-04 13:54:06",
                "tag": "hive-133333"
            }
        },
        {
            "transaction_id": "085284295ff34dd903ddacc1f5215eab935c80df",
            "req_posting_auths": [
                "imwatsi.test"
            ],
            "op_type": "vote",
            "op_payload": {
                "author": "imwatsi.test",
                "permlink": "what-do-you-think",
                "answer": 3
            }
        }
    ],
    "id": 1
}
```

## get_polls_active

*Returns a list of active polls, within a specific tag if specified*

**Params:**

- `tag`: <string (16)> (optional)

**Example payload:**

```
{
    "jsonrpc": "2.0",
    "method": "plug_play_api.polls.get_polls_active",
    "params": {
            "tag": "hive-133333"
        },
    "id": 1
}
```

**Example response (WIP):**

```
{
    "jsonrpc": "2.0",
    "result": [
        {
            "author": "imwatsi.test",
            "permlink": "how-many-users-do-you-think-will-be",
            "question": "How many users do you think will be active on Hive next year.",
            "answers": [
                "10000",
                "200000",
                "3000000"
            ],
            "expires": "2021-12-31T13:54:06",
            "tags": "hive-133333"
        }
    ],
    "id": 1
}
```

## get_poll_votes

*Returns votes for a specified poll*

**Params:**

- `author`:     <string (16)>
- `permlink`:   <string (16)>

**Example payload:**

```
{
    "jsonrpc": "2.0",
    "method": "plug_play_api.polls.get_poll_votes",
    "params": {
            "author": "imwatsi.test",
            "permlink": "what-do-you-think"
        },
    "id": 1
}
```

**Example response:**

```
{
    "jsonrpc": "2.0",
    "result": [
        {
            "account": "imwatsi.test",
            "answer": "$5.00"
        }
    ],
    "id": 1
}
```