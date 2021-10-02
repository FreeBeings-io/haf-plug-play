# Follow Plug

Search endpoints for the Follow protocol

**Dev Server:** https://beta.plug-play.imwatsi.com/

---

### get_follow_ops

*Returns a list of global follow ops within the specified block range (or last 24 hours if not specified)*

**Params:**

- `follower`:      <hive_account> (optional)
- `followed`:      <hive_account> (optional)
- `block_range`:    [lower, upper] (optional, default=28800 blocks from latest)

Example payload:

```
{
    "jsonrpc": "2.0",
    "method": "plug_play_api.follow.get_follow_ops",
    "params": {
        "follower": "tommyl33",
        "followed": "taskmaster4450"
        },
    "id": 1
}
```

Example response:

```
{
    "jsonrpc": "2.0",
    "result": [
        {
            "acc_auths": ['tommyl33'],
            "following": "taskmaster4450",
            "follower": "tommyl33"
        },
        ...
    ],
    "id": 1
}
```

---

### get_reblog_ops

*Returns a list of global reblog ops within the specified block (or last 24 hours if not specified)*

**Params:**

- `reblog_account`: <hive_account> (optional)
- `author`:         <hive_account> (optional)
- `permlink`:       <post_permlink> (optional)
- `block_range`:    [lower, upper] (optional, default=28800 blocks from latest)

Example payload:

```
{
    "jsonrpc": "2.0",
    "method": "plug_play_api.follow.get_reblog_ops",
    "params": {
        "author": "taskmaster4450le"
        },
    "id": 1
}
```

Example response:

```
{
    "jsonrpc": "2.0",
    "result": [
        {
            "acc_auths": ["playhighcard"],
            "account": "playhighcard",
            "author": "taskmaster4450le",
            "permlink": "focus-not-now-the-future"
        },
        {
            "acc_auths": ["playpoker"],
            "account": "playpoker",
            "author": "taskmaster4450le",
            "permlink": "focus-not-now-the-future"
        },
        ...
    ]
}
```

---

### get_account_followers

*Returns a list of Hive accounts that are following the provided Hive account*

**Params:**

- `account`: <hive_account>

Example payload:

```
{
    "jsonrpc": "2.0",
    "method": "plug_play_api.follow.get_account_followers",
    "params": {
        "account": "dan"
        },
    "id": 1
}
```

Example response:

```
{
  "jsonrpc": "2.0",
  "result": [
    {
      "account": "thedashguy",
      "what": [
        "posts",
        "blog"
      ]
    },
    {
      "account": "infovore",
      "what": [
        "posts",
        "blog"
      ]
    },
    {
      "account": "samtoland",
      "what": [
        "posts",
        "blog"
      ]
    },
    {
      "account": "sonsy",
      "what": [
        "posts",
        "blog"
      ]
    },
    {
      "account": "abit",
      "what": [
        "posts",
        "blog"
      ]
    },...
}
```