CREATE TABLE IF NOT EXISTS public.hpp_reblog(
    ppop_id bigint NOT NULL UNIQUE,
    block_num integer NOT NULL,
    transaction_id char(40) NOT NULL,
    req_auths text array,
    req_posting_auths text array,
    account varchar(16),
    author varchar(16),
    permlink varchar(255)
);

CREATE INDEX IF NOT EXISTS hpp_reblog_ix_ppop_id
    ON hpp_reblog (ppop_id);

CREATE INDEX IF NOT EXISTS hpp_reblog_ix_account
    ON hpp_reblog (account);
