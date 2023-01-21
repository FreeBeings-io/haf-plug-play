
CREATE TABLE IF NOT EXISTS deleg.delegations_vesting(
    id BIGSERIAL PRIMARY KEY,
    block_num INTEGER NOT NULL,
    created TIMESTAMP NOT NULL,
    trx_id BYTEA NOT NULL,
    delegator VARCHAR(16) NOT NULL,
    delegatee VARCHAR(16) NOT NULL,
    amount BIGINT
);

CREATE TABLE IF NOT EXISTS deleg.delegations_vesting_returns(
    id BIGSERIAL PRIMARY KEY,
    block_num INTEGER NOT NULL,
    created TIMESTAMP NOT NULL,
    trx_id BYTEA NOT NULL,
    account VARCHAR(16) NOT NULL,
    amount BIGINT,
    UNIQUE (account)
);

CREATE TABLE IF NOT EXISTS deleg.delegations_balances(
    id BIGSERIAL PRIMARY KEY,
    account VARCHAR(16) NOT NULL,
    given BIGINT DEFAULT 0,
    received BIGINT DEFAULT 0,
    UNIQUE (account)
);


CREATE INDEX IF NOT EXISTS delegs_ix_block_num
    ON deleg.delegations_vesting (block_num);

CREATE INDEX IF NOT EXISTS delegs_return_ix_block_num
    ON deleg.delegations_vesting_returns (block_num);

CREATE INDEX IF NOT EXISTS delegs_ix_created
    ON deleg.delegations_vesting (created);

CREATE INDEX IF NOT EXISTS delegs_return_ix_created
    ON deleg.delegations_vesting_returns (created);

CREATE INDEX IF NOT EXISTS delegs_ix_accs
    ON deleg.delegations_vesting (delegator,delegatee);

CREATE INDEX IF NOT EXISTS delegs_return_ix_accs
    ON deleg.delegations_vesting_returns (account);

CREATE INDEX IF NOT EXISTS delegs_bals_ix_accs
    ON deleg.delegations_balances (account);