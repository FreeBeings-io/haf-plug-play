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
    "method": "plug_play_api.reblog.get_reblog_ops",
    "params": {
            "block_range": [1,15000000]
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
      "transaction_id": "b3569abd2900afdf6b55304d4fdc0a8034ac25ed",
      "acc_auths": [
        "test-safari"
      ],
      "account": null,
      "author": null,
      "permlink": null
    },
    {
      "transaction_id": "ae9da66ea9df2bd41b70333b1aefabd325722b67",
      "acc_auths": [
        "test-safari"
      ],
      "account": null,
      "author": null,
      "permlink": null
    },
    {
      "transaction_id": "6907aed1625ca261f065c96c265d84f553a8912c",
      "acc_auths": [
        "jamesc"
      ],
      "account": "jamesc",
      "author": "dantheman",
      "permlink": "why-do-we-fight-to-change-the-world"
    },
    {
      "transaction_id": "6e6e5c5632d35393acacdc40b7c6f1db4e3fe4a1",
      "acc_auths": [
        "nil1511"
      ],
      "account": "nil1511",
      "author": "ned",
      "permlink": "steemfest-update"
    } ...
  ],
  "id": 1
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
            "account": "lukestokes"
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
      "author": "fioprotocol",
      "permlink": "how-to-renew-your-fio-address-or-fio-domain"
    }
  ],
  "id": 1
}
```