# Follow Plug

Search endpoints for the Follow protocol

**Dev Server:** https://plug-play-beta.imwatsi.com

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
            "block_range": [1,2500000]
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
      "transaction_id": "544c84cf09333b77ebffc76c8ab3180041bf6739",
      "acc_auths": [
        "steemit"
      ],
      "follower": "steemit",
      "following": "steem",
      "what": [
        "posts"
      ]
    },
    {
      "transaction_id": "bc81ed5d7d689d1aed10796e04d9bcb304ad2c07",
      "acc_auths": [
        "red"
      ],
      "follower": "red",
      "following": "piedpiper",
      "what": [
        "posts"
      ]
    },
    {
      "transaction_id": "9e442eca18cef91bdbd75af1b409da790ecd8d2b",
      "acc_auths": [
        "red"
      ],
      "follower": "red",
      "following": "piedpiper",
      "what": [
        "posts"
      ]
    },
    ...
}
```

---

### get_reblog_ops (WIP)

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
      "account": "hr1",
      "what": [
        "blog"
      ]
    },
    {
      "account": "steemit200",
      "what": [
        "blog"
      ]
    },
    {
      "account": "ash",
      "what": [
        "blog"
      ]
    },
    {
      "account": "infovore",
      "what": [
        "posts"
      ]
    },
    ...
}
```