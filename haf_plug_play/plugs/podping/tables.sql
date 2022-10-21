CREATE TABLE IF NOT EXISTS podping.ops(
    id BIGSERIAL PRIMARY KEY,
    block_num INTEGER NOT NULL,
    created TIMESTAMP NOT NULL,
    trx_id BYTEA NOT NULL,
    req_auths VARCHAR(16)[],
    req_posting_auths VARCHAR(16)[],
    op_id VARCHAR,
    op_payload JSON
);

CREATE TABLE IF NOT EXISTS podping.updates(
    id BIGSERIAL PRIMARY KEY,
    podping_id BIGINT NOT NULL REFERENCES podping.ops(id) ON DELETE CASCADE DEFERRABLE,
    block_num INTEGER NOT NULL,
    created TIMESTAMP NOT NULL,
    trx_id BYTEA NOT NULL,
    req_auths VARCHAR(16)[],
    req_posting_auths VARCHAR(16)[],
    url VARCHAR(500),
    reason VARCHAR,
    medium VARCHAR
);

CREATE INDEX IF NOT EXISTS ops_ix_posting_auths
    ON podping.ops USING GIN(req_posting_auths);

CREATE INDEX IF NOT EXISTS updates_ix_block_num
    ON podping.updates (block_num);

CREATE INDEX IF NOT EXISTS updates_ix_created
    ON podping.updates (created);

CREATE INDEX IF NOT EXISTS updates_ix_reason
    ON podping.updates (reason);

CREATE INDEX IF NOT EXISTS updates_ix_medium
    ON podping.updates (medium);
