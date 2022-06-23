CREATE SCHEMA IF NOT EXISTS polls;

CREATE TABLE IF NOT EXISTS polls.ops(
    id BIGSERIAL UNIQUE,
    block_num INTEGER NOT NULL,
    created TIMESTAMP NOT NULL,
    transaction_id CHAR(40) NOT NULL,
    req_auths VARCHAR(16)[],
    req_posting_auths VARCHAR(16)[],
    op_header JSON,
    op_type VARCHAR(16),
    op_payload JSON
) INHERITS( hive.plug_play );

CREATE TABLE IF NOT EXISTS polls.content(
    poll_opid BIGINT NOT NULL UNIQUE REFERENCES polls.ops(id) ON DELETE CASCADE DEFERRABLE,
    poll_id BIGSERIAL PRIMARY KEY,
    created TIMESTAMP,
    permlink VARCHAR(255),
    author VARCHAR(16),
    question VARCHAR(255),
    answers VARCHAR(128)[],
    expires TIMESTAMP,
    tag VARCHAR(500),
    deleted BOOLEAN DEFAULT false
) INHERITS( hive.plug_play );

CREATE TABLE IF NOT EXISTS polls.votes(
    pp_poll_opid BIGINT NOT NULL UNIQUE REFERENCES polls.ops(id) ON DELETE CASCADE DEFERRABLE,
    permlink VARCHAR(255),
    author VARCHAR(16),
    created TIMESTAMP,
    account VARCHAR(16),
    answer SMALLINT
) INHERITS( hive.plug_play );


CREATE INDEX IF NOT EXISTS ops_ix_op_type
    ON polls.ops (op_type);

CREATE INDEX IF NOT EXISTS content_ix_expires
    ON polls.content (expires);

CREATE INDEX IF NOT EXISTS content_ix_tag
    ON polls.content (tag);

CREATE INDEX IF NOT EXISTS votes_ix_author_permlink
    ON polls.votes (author,permlink);
