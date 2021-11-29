CREATE TABLE IF NOT EXISTS public.hpp_polls_ops(
    ppop_id BIGINT NOT NULL UNIQUE REFERENCES public.plug_play_ops(id),
    pp_poll_id BIGSERIAL UNIQUE,
    block_num INTEGER NOT NULL,
    transaction_id CHAR(40) NOT NULL,
    op_type VARCHAR(16),
    op_payload VARCHAR
);

CREATE TABLE IF NOT EXISTS public.hpp_polls_content(
    pp_poll_id BIGINT NOT NULL UNIQUE REFERENCES public.hpp_polls_ops(pp_poll_id),
    permlink VARCHAR(255),
    author VARCHAR(16),
    question VARCHAR(255),
    answers VARCHAR(128)[],
    expires TIMESTAMP,
    tag VARCHAR(16),
    CONSTRAINT hpp_polls_ops_pkey_unique PRIMARY KEY (author,permlink)
);

CREATE TABLE IF NOT EXISTS public.hpp_polls_votes(
    pp_poll_id BIGINT NOT NULL UNIQUE REFERENCES public.hpp_polls_ops(pp_poll_id),
    account VARCHAR(16),
    answer SMALLINT
);


CREATE INDEX IF NOT EXISTS hpp_polls_ops_ix_ppop_id
    ON public.hpp_polls_ops (ppop_id);

CREATE INDEX IF NOT EXISTS hpp_polls_ops_ix_pp_poll_id
    ON public.hpp_polls_ops (pp_poll_id);

CREATE INDEX IF NOT EXISTS hpp_polls_ops_ix_op_type
    ON public.hpp_polls_ops (op_type);

CREATE INDEX IF NOT EXISTS hpp_polls_content_ix_expires
    ON public.hpp_polls_content (expires);

CREATE INDEX IF NOT EXISTS hpp_polls_content_ix_tag
    ON public.hpp_polls_content (tag);