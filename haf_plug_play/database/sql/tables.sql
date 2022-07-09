CREATE SCHEMA IF NOT EXISTS hpp;

CREATE TABLE IF NOT EXISTS hpp.global_props(
    head_block_num BIGINT DEFAULT 0,
    sync_enabled BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS hpp.plug_state(
    plug VARCHAR(64) PRIMARY KEY,
    defs JSON,
    latest_block_num BIGINT DEFAULT 0,
    latest_block_time TIMESTAMP,
    check_in TIMESTAMP,
    massive_synced BOOLEAN DEFAULT false
);
