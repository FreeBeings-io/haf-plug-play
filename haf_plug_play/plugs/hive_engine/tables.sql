CREATE SCHEMA IF NOT EXISTS hive_engine;

CREATE TABLE IF NOT EXISTS hive_engine.ops(
    id BIGSERIAL PRIMARY KEY,
    block_num INTEGER NOT NULL,
    created TIMESTAMP NOT NULL,
    trx_id BYTEA NOT NULL,
    req_auths VARCHAR(16)[],
    req_posting_auths VARCHAR(16)[],
    op_id VARCHAR,
    op_payload JSON,
    valid BOOLEAN
);

CREATE TABLE IF NOT EXISTS hive_engine.transfers(
    id BIGSERIAL PRIMARY KEY,
    block_num INTEGER NOT NULL,
    created TIMESTAMP NOT NULL,
    symbol VARCHAR,
    from_acc VARCHAR(16),
    to_acc VARCHAR(16),
    qty NUMERIC(18,10),
    memo VARCHAR
);

CREATE TABLE IF NOT EXISTS hive_engine.nfts(
    id BIGSERIAL PRIMARY KEY,
    he_id BIGINT NOT NULL REFERENCES hive_engine.ops(id),
    details JSON
);

CREATE TABLE IF NOT EXISTS hive_engine.transfers(
    id BIGSERIAL PRIMARY KEY,
    he_id BIGINT NOT NULL REFERENCES hive_engine.ops(id),
    details JSON -- TODO: investigate expanding
);

CREATE TABLE IF NOT EXISTS hive_engine.issuances(
    id BIGSERIAL PRIMARY KEY,
    he_id BIGINT NOT NULL REFERENCES hive_engine.ops(id),
    details JSON -- TODO: investigate expanding
);

CREATE TABLE IF NOT EXISTS hive_engine.transfers(
    id BIGSERIAL PRIMARY KEY,
    he_id BIGINT NOT NULL REFERENCES hive_engine.ops(id),
    details JSON -- TODO: investigate expanding
);

CREATE TABLE IF NOT EXISTS hive_engine.burns(
    id BIGSERIAL PRIMARY KEY,
    he_id BIGINT NOT NULL REFERENCES hive_engine.ops(id),
    details JSON -- TODO: investigate expanding
);

-- INDEXES: OPS

CREATE INDEX IF NOT EXISTS ops_ix_contract_name ON hive_engine.ops USING HASH((op_payload->'contractName'));
CREATE INDEX IF NOT EXISTS ops_ix_contract_action ON hive_engine.ops USING HASH((op_payload->'contractAction'));

-- INDEXES: TRANSFERS

CREATE INDEX IF NOT EXISTS transfers_ix_block_num
    ON hive_engine.transfers (block_num);

CREATE INDEX IF NOT EXISTS transfers_ix_created
    ON hive_engine.transfers (created);

-- INDEXES: NFTS