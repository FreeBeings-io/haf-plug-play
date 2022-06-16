CREATE TABLE IF NOT EXISTS podping.ops(
    id BIGSERIAL PRIMARY KEY,
    block_num INTEGER NOT NULL,
    created TIMESTAMP NOT NULL,
    trx_id BYTEA NOT NULL,
    req_auths VARCHAR(16)[],
    req_posting_auths VARCHAR(16)[],
    op_id VARCHAR(31),
    op_payload JSON
) INHERITS( hive.plug_play );

CREATE TABLE IF NOT EXISTS podping.feed_updates(
    feed_update_id BIGSERIAL PRIMARY KEY,
    pp_podping_opid BIGINT NOT NULL REFERENCES podping.ops(id) ON DELETE CASCADE DEFERRABLE,
    block_num INTEGER NOT NULL,
    created TIMESTAMP NOT NULL,
    url VARCHAR(500)
) INHERITS( hive.plug_play );


CREATE INDEX IF NOT EXISTS podping.feed_updates_ix_block_num
    ON podping.feed_updates (block_num);

CREATE INDEX IF NOT EXISTS podping.feed_updates_ix_created
    ON podping.feed_updates (created);
