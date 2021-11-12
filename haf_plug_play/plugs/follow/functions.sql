CREATE OR REPLACE FUNCTION public.hpp_follow_update( _begin INT, _end INT )
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            temprow RECORD;
            head_hive_rowid int;
        BEGIN
            SELECT MAX(latest_hive_rowid) INTO head_hive_rowid FROM public.plug_sync WHERE plug_name = 'follow';
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
                    ppops.op_json::json ->>'follower' AS follower,
                    ppops.op_json::json ->>'following' AS following,
                    ARRAY(SELECT json_array_elements_text(ppops.op_json::json ->'what')) AS what
                FROM public.plug_play_ops ppops
                WHERE ppops.hive_rowid >= _begin
                    AND ppops.hive_rowid <= _end
                    AND ppops.op_id = 'follow'
            LOOP
                INSERT INTO public.hpp_follow as hppf(
                    ppop_id, block_num, transaction_id, req_auths, req_posting_auths, account, following, what)
                VALUES (
                    temprow.ppop_id, temprow.block_num, temprow.transaction_id,
                    temprow.req_auths, temprow.req_posting_auths, temprow.follower,
                    temprow.following, temprow.what
                );
                UPDATE public.plug_sync SET latest_hive_rowid = temprow.hive_rowid AND latest_hive_head_block = temprow.block_num WHERE plug_name='follow';
                IF temprow.follower IS NOT NULL AND temprow.following IS NOT NULL THEN
                    PERFORM hpp_follow_update_state(temprow.follower, temprow.following, temprow.what);
                END IF;
                UPDATE public.plug_sync SET state_hive_rowid = temprow.hive_rowid WHERE plug_name='follow';
            END LOOP;
        END;
        $function$;

CREATE OR REPLACE FUNCTION public.hpp_follow_update_state( _follower VARCHAR, _following VARCHAR, _what TEXT ARRAY )
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            temprow RECORD;
            in_what boolean;
            to_add text array;
            final text array;
            x text;
        BEGIN
            SELECT * INTO temprow FROM hpp_follow_state WHERE account = _follower AND following = _following;
            IF NOT FOUND THEN
                INSERT INTO public.hpp_follow_state(account, following, what)
                VALUES (_follower, _following, _what);
            ELSE
                in_what := false;
                IF array_length(_what, 1) > 0 THEN
                    FOREACH x IN ARRAY _what
                    LOOP
                        IF NOT (x = ANY (temprow.what)) THEN
                            to_add := array_append(to_add, x);
                        END IF;
                    END LOOP;
                    UPDATE public.hpp_follow_state SET what = temprow.what || to_add WHERE account = _follower AND following = _following;
                ELSE
                    UPDATE public.hpp_follow_state SET what = '{}' WHERE account = _follower AND following = _following;
                END IF;
            END IF;
        END;
        $function$;