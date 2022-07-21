# Designing the schema for your plug

The schema for your plug consists of any tables/views that you need to store and process your data. The file needs to be saved as `tables.sql` and stored in your plug's subdirectory under the `../haf_plug_play/plugs` directory. For example: `../haf_plug_play/plugs/podping/tables.sql`. Note that the queries in this file are run everytime Plug & Play starts, so `IF NOT EXISTS` conditions are necessary.

First, you need to create your schema. Be sure to use the same schema_name as mentioned in your plug's `defs.json` file.

`CREATE SCHEMA IF NOT EXISTS <schema_name>;`

For most app use cases, it is recommended to develop the structure of your tables in relation to one core table for operations extracted from HAF. This gives you:

- historical data for your plug
- ability to rollback and recover from forks (because this table will be registered on HAF)
- higher-level operation data like `block_num`, `trx_hash` and `timestamp` associated with downstream operations that are relevant to your app

So an example core table for operations is from the `podping` plug:

```
CREATE TABLE IF NOT EXISTS podping.ops(
    id BIGSERIAL PRIMARY KEY,
    block_num INTEGER NOT NULL,
    created TIMESTAMP NOT NULL,
    trx_id BYTEA NOT NULL,
    req_auths VARCHAR(16)[],
    req_posting_auths VARCHAR(16)[],
    op_id VARCHAR,
    op_payload JSON
) INHERITS( hive.podping );
```

From this core table, you can go on to define tables that store the results of the individual ops and create state for your plug. For example, the `podping` plug uses the following table to store podping updates:

```
CREATE TABLE IF NOT EXISTS podping.updates(
    id BIGSERIAL PRIMARY KEY,
    podping_id BIGINT NOT NULL REFERENCES podping.ops(id) ON DELETE CASCADE DEFERRABLE,
    block_num INTEGER NOT NULL,
    created TIMESTAMP NOT NULL,
    url VARCHAR(500),
    reason VARCHAR,
    medium VARCHAR
);
```

Note the `id` REFERENCE. It links the data in the table to the individual op responsible for creating, with cascading deletes so when fork recovery removes entries, they are also removed.

Finally, you create indexes as your plug requires. The `podping` app uses these:

```
CREATE INDEX IF NOT EXISTS updates_ix_block_num
    ON podping.updates (block_num);

CREATE INDEX IF NOT EXISTS updates_ix_created
    ON podping.updates (created);

CREATE INDEX IF NOT EXISTS updates_ix_reason
    ON podping.updates (reason);

CREATE INDEX IF NOT EXISTS updates_ix_medium
    ON podping.updates (medium);
```

With all these aspects catered for, your plug is ready to store data in an accessible way.