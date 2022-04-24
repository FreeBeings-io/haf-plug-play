CREATE TABLE IF NOT EXISTS hpp.podping_ops(
    pp_podping_opid BIGSERIAL PRIMARY KEY,
    ppop_id BIGINT NOT NULL REFERENCES hpp.plug_play_ops(id) ON DELETE CASCADE DEFERRABLE,
    block_num INTEGER NOT NULL,
    created TIMESTAMP NOT NULL,
    transaction_id CHAR(40) NOT NULL,
    req_auths VARCHAR(16)[],
    req_posting_auths VARCHAR(16)[],
    op_id VARCHAR(31),
    op_payload JSON
) INHERITS( hive.plug_play );

CREATE TABLE IF NOT EXISTS hpp.podping_feed_updates(
    feed_update_id BIGSERIAL PRIMARY KEY,
    pp_podping_opid BIGINT NOT NULL REFERENCES hpp.podping_ops(pp_podping_opid) ON DELETE CASCADE DEFERRABLE,
    block_num INTEGER NOT NULL,
    created TIMESTAMP NOT NULL,
    url VARCHAR(500)
) INHERITS( hive.plug_play );


CREATE INDEX IF NOT EXISTS podping_ops_ix_pp_podping_opid
    ON hpp.podping_ops (pp_podping_opid);

CREATE INDEX IF NOT EXISTS podping_feed_updates_ix_block_num
    ON hpp.podping_feed_updates (block_num);

CREATE INDEX IF NOT EXISTS podping_feed_updates_ix_created
    ON hpp.podping_feed_updates (created);
