CREATE SCHEMA IF NOT EXISTS hpp;

CREATE TABLE IF NOT EXISTS hpp.global_props(
    latest_block_num BIGINT DEFAULT 0,
    latest_hive_rowid BIGINT DEFAULT 0,
    latest_hpp_op_id BIGINT DEFAULT 0,
    latest_block_time TIMESTAMP,
    sync_enabled BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS hpp.ops(
    hpp_op_id BIGSERIAL PRIMARY KEY,
    hive_opid BIGINT UNIQUE NOT NULL,
    op_type_id SMALLINT NOT NULL,
    block_num INTEGER NOT NULL,
    created TIMESTAMP,
    transaction_id CHAR(40),
    body JSON
) INHERITS( hive.hpp );

CREATE TABLE IF NOT EXISTS hpp.plug_state(
    module VARCHAR(64) PRIMARY KEY,
    defs JSON,
    latest_hpp_op_id BIGINT DEFAULT 0
);
