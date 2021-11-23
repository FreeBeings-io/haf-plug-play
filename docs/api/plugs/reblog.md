# Reblog Plug

Search endpoints for the Reblog protocol

**Production Server:** https://plug-play.imwatsi.com
**Dev Server:** https://plug-play-beta.imwatsi.com

---

### get_reblog_ops

*Returns a list of global reblog ops within the specified block range (or last 24 hours if not specified)*

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


### get_account_reblogs

*Returns a list of all reblogs an account has made*

**Params:**

- `account`:      <hive_account> (optional)

Example payload:

```
{
    "jsonrpc": "2.0",
    "method": "plug_play_api.reblog.get_account_reblogs",
    "params": {
            "account": "netuoso"
        },
    "id": 1
}
```

Example response:

```