CREATE TABLE IF NOT EXISTS public.hpp_podping_ops(
    pp_podping_opid BIGSERIAL PRIMARY KEY,
    ppop_id BIGINT NOT NULL REFERENCES public.plug_play_ops(id),
    req_auths VARCHAR(16)[],
    req_posting_auths VARCHAR(16)[],
    op_id VARCHAR(31),
    op_payload JSON
);

CREATE TABLE IF NOT EXISTS public.hpp_podping_feed_updates(
    feed_update_id BIGSERIAL PRIMARY KEY,
    pp_podping_opid BIGINT NOT NULL REFERENCES public.hpp_podping_ops(pp_podping_opid),
    block_num INTEGER NOT NULL,
    created TIMESTAMP NOT NULL,
    url VARCHAR(500)
);


CREATE INDEX IF NOT EXISTS hpp_podping_ops_ix_pp_podping_opid
    ON public.hpp_podping_ops (pp_podping_opid);

CREATE INDEX IF NOT EXISTS hpp_podping_feed_updates_ix_block_num
    ON public.hpp_podping_feed_updates (block_num);

CREATE INDEX IF NOT EXISTS hpp_podping_feed_updates_ix_created
    ON public.hpp_podping_feed_updates (created);