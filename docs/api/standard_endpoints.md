# Standard endpoints

**Production Server:** https://plug-play.imwatsi.com
**Dev Server:** https://plug-play-beta.imwatsi.com

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

Example curl:

`curl -s --data '{"jsonrpc": "2.0", "method": "plug_play_api.ping", "id": 1}' https://plug-play.imwatsi.com`

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
          "sync": "Massive sync in progress: 1 to 1000001",
          "system": {
              "head_hive_rowid": 0,
              "head_block_num": null,
              "head_block_time": null
          }
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

Example curl:

`curl -s --data '{"jsonrpc": "2.0", "method": "plug_play_api.get_ops_by_block", "params": {"block_num": 2232411}, "id": 1}' https://plug-play.imwatsi.com`