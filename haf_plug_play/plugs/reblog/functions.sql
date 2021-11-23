CREATE OR REPLACE FUNCTION public.hpp_reblog_update( _begin BIGINT, _end BIGINT )
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            temprow RECORD;
            head_hive_rowid bigint;
        BEGIN
            SELECT MAX(latest_hive_rowid) INTO head_hive_rowid FROM public.plug_sync WHERE plug_name = 'reblog';
                RAISE NOTICE '%', head_hive_rowid;
                IF head_hive_rowid IS NULL THEN
                    head_hive_rowid := 0;
                    RAISE NOTICE 'head_hive_rowid is NULL';
                    IF NOT _begin = 1 THEN
                        RAISE NOTICE 'New sync needs to start at row 1';
                        RETURN;
                    END IF;
                ELSIF _end < head_hive_rowid THEN
                    RAISE NOTICE 'head: %  head + 1:  %  end:  %', head_hive_rowid, head_hive_rowid + 1, _end;
                    RETURN;
                END IF;
                RAISE NOTICE '%   %', _begin, head_hive_rowid;
                IF _begin < (head_hive_rowid + 1) THEN
                    IF _end >= (head_hive_rowid + 1) THEN
                        _begin := (head_hive_rowid + 1);
                    ELSE
                        RAISE NOTICE 'Cannot begin sync on ID less than head + 1';
                        RETURN;
                    END IF;
                END IF;
                RAISE NOTICE 'head: %  begin:  %  end:  %', head_hive_rowid, _begin, _end;

                FOR temprow IN
                SELECT
                    ppops.id AS ppop_id,
                    ppops.block_num AS block_num,
                    transaction_id AS transaction_id,
                    ARRAY(SELECT json_array_elements_text(req_auths::json))  AS req_auths,
                    ARRAY(SELECT json_array_elements_text(req_posting_auths::json)) AS req_posting_auths,
                    (ppops.op_json::json ->> 1) ::json ->> 'account' AS account,
                    (ppops.op_json::json ->> 1) ::json ->> 'author' AS author,
                    (ppops.op_json::json ->> 1) ::json ->> 'permlink' AS permlink
                FROM public.plug_play_ops ppops
                WHERE ppops.hive_rowid >= _begin
                    AND ppops.hive_rowid <= _end
                    AND ppops.op_id = 'reblog'
            LOOP
                INSERT INTO public.hpp_reblog as hppr(
                    ppop_id, block_num, transaction_id, req_auths, req_posting_auths, account, author, permlink)
                VALUES (
                    temprow.hive_rowid, temprow.block_num, temprow.transaction_id,
                    temprow.req_auths, temprow.req_posting_auths, temprow.account,
                    temprow.author, temprow.permlink
                );
                UPDATE public.plug_sync SET latest_hive_rowid = temprow.hive_rowid, latest_hive_head_block = temprow.block_num WHERE plug_name='reblog';
                PERFORM hpp_reblog_update_state(temprow.account, temprow.author, temprow.permlink);
                UPDATE public.plug_sync SET state_hive_rowid = temprow.hive_rowid WHERE plug_name='reblog';
            END LOOP;
        END;
        $function$;
