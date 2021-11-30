# Polls Plug

Endpoints for the polls protocol

**Production Server:** https://plug-play.imwatsi.com
**Dev Server:** https://plug-play-beta.imwatsi.com

---

### get_polls_ops

*Returns a list of polls ops within the specified block range (or last 24 hours if not specified)*

**Params:**

- `op_type`:      <string(16)> (optional)
- `block_range`:    [lower, upper] (optional, default=28800 blocks from latest)

Example payload:

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

Example response (WIP):

```
{}
```
