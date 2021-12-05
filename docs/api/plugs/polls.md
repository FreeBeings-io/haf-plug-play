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
{}
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
            "block_range": [1,2500000]
        },
    "id": 1
}
```

**Example response (WIP):**

```
{}
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
{}
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
            "author": "imwatsi",
            "permlink": "my-first-poll"
        },
    "id": 1
}
```

**Example response:**

```
{}
```