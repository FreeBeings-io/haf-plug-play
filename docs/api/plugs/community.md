# Community Plug (Not available yet - WIP)

Search endpoints for the Hivemind Communities protocol

**Production Server:** https://plug-play.imwatsi.com
**Dev Server:** https://plug-play-beta.imwatsi.com

### get_subscribe_ops

*Returns a list of subscribe ops made for a community within a specified block range (or last 24 hours if not specified)*

**Params:**

- `community`:      <hive_account> (optional)
- `block_range`:    [lower, upper] (optional, default=28800 blocks from latest)

Example payload:

```
{
    "jsonrpc": "2.0",
    "method": "plug_play_api.community.get_subscribe_ops",
    "params": {"community": "hive-167922"},
    "id": 1
}
```

Example response:

```
{
    "jsonrpc": "2.0",
    "result": [
        {"account": "hivebuzz"},
        {"account": "eii"},
        {"account": "geeklania"},
        {"account": "hostioso"}
    ], 
    "id": 1
}
```

### get_unsubscribe_ops

*Returns a list of unsubscribe ops made for a community within a specified block range (or last 24 hours if not specified)*

**Params:**

- `community`:      <hive_account> (optional)
- `block_range`:    [lower, upper] (optional, default=28800 blocks from latest)

Example payload:

```
{
    "jsonrpc": "2.0",
    "method": "plug_play_api.community.get_unsubscribe_ops",
    "params": {"community": "hive-167922"},
    "id": 1
}
```

Example response:

```
{
    "jsonrpc": "2.0",
    "result": [
        {"account": "chukshive"},
        {"account": "adeleke08"},
        {"account": "tricksterlogos"},
        {"account": "andreasalas"},
        {"account": "castleberry"},
        ...
    ],
    "id": 1
}
```