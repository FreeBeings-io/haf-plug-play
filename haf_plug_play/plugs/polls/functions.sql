CREATE OR REPLACE FUNCTION public.hpp_polls_update( _begin BIGINT, _end BIGINT )
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            temprow RECORD;
            head_hive_rowid BIGINT;
            _block_num BIGINT;
            _hive_opid BIGINT;
            _header JSON;
            _op_type VARCHAR(16);
            _op_payload JSON;
            _json JSON;
        BEGIN
            -- Preparations
            SELECT MAX(latest_hive_opid) INTO head_hive_rowid FROM public.plug_sync WHERE plug_name = 'polls';
            RAISE NOTICE '%', head_hive_rowid;
            IF head_hive_rowid IS NULL THEN
                head_hive_rowid := 0;
                RAISE NOTICE 'head_hive_rowid is NULL';
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

            -- Sync update
            FOR temprow IN
                SELECT
                    ppops.id,
                    ppops.hive_opid,
                    ppops.block_num,
                    ppops.timestamp,
                    ppops.transaction_id,
                    ARRAY(SELECT json_array_elements_text(req_auths::json))  AS req_auths,
                    ARRAY(SELECT json_array_elements_text(req_posting_auths::json)) AS req_posting_auths,
                    ppops.op_json
                FROM public.plug_play_ops ppops
                WHERE ppops.hive_opid >= _begin
                    AND ppops.hive_opid <= _end
                    AND ppops.op_id = 'polls'
            LOOP
                _block_num := temprow.block_num;
                _hive_opid := temprow.hive_opid;
                _json := temprow.op_json::json;
                _header := (_json ->> 0)::json;
                _op_type := _json ->> 1;
                _op_payload := (_json ->> 2)::json;

                INSERT INTO public.hpp_polls_ops as hppf(
                    ppop_id, block_num, created, transaction_id, req_auths, req_posting_auths, op_header, op_type, op_payload)
                VALUES (
                    temprow.id, temprow.block_num, temprow.timestamp, temprow.transaction_id,
                    temprow.req_auths, temprow.req_posting_auths, _header, _op_type,
                    _op_payload
                );
                -- Update state tables
                PERFORM hpp_polls_update_state(temprow.id, temprow.timestamp, temprow.req_posting_auths[1], temprow.req_auths[1], _header, _op_type, _op_payload);
            END LOOP;
            IF _block_num IS NOT NULL AND _hive_opid IS NOT NULL THEN
                UPDATE public.plug_sync SET latest_block_num = _block_num, latest_hive_opid = _hive_opid, state_hive_opid = _hive_opid WHERE plug_name='polls';
            END IF;
        END;
        $function$;

CREATE OR REPLACE FUNCTION public.hpp_polls_update_state( _ppop_id BIGINT, _created TIMESTAMP, _posting_acc VARCHAR(16), _active_acc VARCHAR(16), _header JSON, _op_type VARCHAR, _op_payload JSON)
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            temprow RECORD;
            _pp_poll_opid BIGINT;
            _author VARCHAR(16);
            _permlink VARCHAR(255);
            _question VARCHAR(255);
            _answer SMALLINT;
            _answers VARCHAR(128)[];
            _tag VARCHAR(500);
            _expires TIMESTAMP;
            _op_version SMALLINT;
            _app_name VARCHAR(100);
            -- 
        BEGIN
            _op_version := _header ->> 0;
            _app_name := _header ->> 1;
            SELECT pp_poll_opid INTO _pp_poll_opid FROM public.hpp_polls_ops WHERE ppop_id = _ppop_id;

            RAISE NOTICE 'op_version: % \n app_name: %', _op_version, _app_name;

            IF _op_version = 1 THEN
                IF _op_type = 'create' THEN
                    -- new poll
                    _permlink := _op_payload ->> 'permlink';
                    _question := _op_payload ->> 'question';
                    _answers := ARRAY(SELECT json_array_elements_text((_op_payload ->> 'answers')::json));
                    _expires := _op_payload ->> 'expires';
                    _tag := _op_payload ->> 'tag';
                    SELECT * INTO temprow FROM public.hpp_polls_content WHERE author = _posting_acc and permlink = _permlink;
                    IF NOT FOUND THEN
                        INSERT INTO public.hpp_polls_content (pp_poll_opid, author, permlink, question, answers, expires, tag, created)
                        VALUES (
                            _pp_poll_opid, _posting_acc, _permlink, _question,
                            _answers, _expires, _tag, _created
                        );
                    END IF;
                ELSIF _op_type = 'vote' THEN
                    -- vote on a poll
                    _answer := _op_payload ->> 'answer';
                    _author := _op_payload ->> 'author';
                    _permlink := _op_payload ->> 'permlink';
                    INSERT INTO public.hpp_polls_votes (pp_poll_opid, permlink, author, created, account, answer)
                    VALUES (_pp_poll_opid, _permlink, _author, _created, _posting_acc, _answer);
                END IF;
            END IF;
        EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE E'Got exception:
                SQLSTATE: % 
                SQLERRM: %', SQLSTATE, SQLERRM;
        END;
        $function$;