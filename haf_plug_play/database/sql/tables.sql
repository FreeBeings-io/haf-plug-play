CREATE SCHEMA IF NOT EXISTS hpp;

CREATE TABLE IF NOT EXISTS hpp.global_props(
    latest_block_num BIGINT DEFAULT 0,
    latest_hive_rowid BIGINT DEFAULT 0,
    latest_hpp_op_id BIGINT DEFAULT 0,
    latest_block_time TIMESTAMP,
    sync_enabled BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS hpp.plug_state(
    plug VARCHAR(64) PRIMARY KEY,
    defs JSON,
    latest_block_num BIGINT DEFAULT 0,
    latest_hive_opid BIGINT DEFAULT 0,
    sync_enabled BOOLEAN DEFAULT false,
    run_start BOOLEAN DEFAULT false,
    run_finish BOOLEAN DEFAULT false
);
