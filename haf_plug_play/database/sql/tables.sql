CREATE TABLE IF NOT EXISTS hpp.global_props(
    sync_enabled BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS hpp.plug_state(
    plug VARCHAR(64) PRIMARY KEY,
    defs JSON,
    enabled BOOLEAN,
    latest_block_num BIGINT DEFAULT 0,
    latest_block_time TIMESTAMP,
    check_in TIMESTAMP,
    massive_synced BOOLEAN DEFAULT false
);
