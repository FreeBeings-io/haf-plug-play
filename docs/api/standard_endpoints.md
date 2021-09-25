# Standard endpoints

**Dev Server:** https://beta.plug-play.imwatsi.com/

### ping

*Ping endpoint*

Example payload:

```
{
    "jsonrpc": "2.0",
    "method": "plug_play_api.ping",
    "id": 1
}
```

Example response:

```
{
    "jsonrpc": "2.0",
    "result": "pong",
    "id": 1
}
```

### get_sync_status

*Retrieves the node's sync status*

Example payload:

```
{
    "jsonrpc": "2.0",
    "method": "plug_play_api.get_sync_status",
    "id": 1
}
```

Example response:

```
{
    "jsonrpc": "2.0",
    "result": {
      "latest_block": 2999999,
      "latest_block_time": "2016-07-07 21:24:54",
      "behind": false
    },
    "id": 1
}
```

---

### get_ops_by_block

*Retrieves all custom_json ops within a specified block number*

Example payload:

```
{
    "jsonrpc": "2.0",
    "method": "plug_play_api.get_ops_by_block",
    "params": {"block_num": 2232411},
    "id": 1
}
```


Example repsonse:

```
{
  "jsonrpc": "2.0",
  "result": [
    {
      "transaction_id": "6da8f390791cfdcb21a60a46300a8f9c45577631",
      "req_auths": [],
      "req_posting_auths": [
        "pixellated"
      ],
      "op_id": "follow",
      "op_json": "\"{\\\"follower\\\":\\\"pixellated\\\",\\\"following\\\":\\\"arhag\\\",\\\"what\\\":[\\\"blog\\\"]}\""
    }
  ],
  "id": 1
}
```