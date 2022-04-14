CREATE TABLE IF NOT EXISTS public.hpp_polls_ops(
    ppop_id BIGINT NOT NULL UNIQUE REFERENCES public.plug_play_ops(id) ON DELETE CASCADE DEFERRABLE,
    pp_poll_opid BIGSERIAL UNIQUE,
    block_num INTEGER NOT NULL,
    created TIMESTAMP NOT NULL,
    transaction_id CHAR(40) NOT NULL,
    req_auths VARCHAR(16)[],
    req_posting_auths VARCHAR(16)[],
    op_header JSON,
    op_type VARCHAR(16),
    op_payload JSON
);

CREATE TABLE IF NOT EXISTS public.hpp_polls_content(
    pp_poll_opid BIGINT NOT NULL UNIQUE REFERENCES public.hpp_polls_ops(pp_poll_opid) ON DELETE CASCADE DEFERRABLE,
    poll_id BIGSERIAL PRIMARY KEY,
    created TIMESTAMP,
    permlink VARCHAR(255),
    author VARCHAR(16),
    question VARCHAR(255),
    answers VARCHAR(128)[],
    expires TIMESTAMP,
    tag VARCHAR(500),
    deleted BOOLEAN DEFAULT false
);

CREATE TABLE IF NOT EXISTS public.hpp_polls_votes(
    pp_poll_opid BIGINT NOT NULL UNIQUE REFERENCES public.hpp_polls_ops(pp_poll_opid) ON DELETE CASCADE DEFERRABLE,
    permlink VARCHAR(255),
    author VARCHAR(16),
    created TIMESTAMP,
    account VARCHAR(16),
    answer SMALLINT
);


CREATE INDEX IF NOT EXISTS hpp_polls_ops_ix_ppop_id
    ON public.hpp_polls_ops (ppop_id);

CREATE INDEX IF NOT EXISTS hpp_polls_ops_ix_pp_poll_opid
    ON public.hpp_polls_ops (pp_poll_opid);

CREATE INDEX IF NOT EXISTS hpp_polls_ops_ix_op_type
    ON public.hpp_polls_ops (op_type);

CREATE INDEX IF NOT EXISTS hpp_polls_content_ix_expires
    ON public.hpp_polls_content (expires);

CREATE INDEX IF NOT EXISTS hpp_polls_content_ix_tag
    ON public.hpp_polls_content (tag);

CREATE INDEX IF NOT EXISTS hpp_polls_votes_ix_author_permlink
    ON public.hpp_polls_votes (author,permlink);