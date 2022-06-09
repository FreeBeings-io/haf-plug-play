CREATE OR REPLACE FUNCTION podping.podping_update( _begin BIGINT, _end BIGINT )
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            temprow RECORD;
            head_hive_rowid BIGINT;
            -- 
            _id BIGINT;
            _hive_opid BIGINT;
            _block_num BIGINT;
            _block_timestamp TIMESTAMP;
            _required_auths VARCHAR(16)[];
            _required_posting_auths VARCHAR(16)[];
            _op_id VARCHAR(31);
            _op_payload JSON;
            _transaction_id VARCHAR(40);
            _new_id BIGINT;

        BEGIN
            -- Preparations
            SELECT MAX(latest_hive_opid) INTO head_hive_rowid FROM hpp.plug_sync WHERE plug_name = 'podping';
            RAISE NOTICE '%', head_hive_rowid;
            IF head_hive_rowid IS NULL THEN
                head_hive_rowid := 0;
                RAISE NOTICE 'head_hive_block_num is NULL';
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
                    ppops.transaction_id,
                    ppops.timestamp,
                    ppops.req_auths,
                    ppops.req_posting_auths,
                    ppops.op_id,
                    ppops.op_json
                FROM hpp.plug_play_ops ppops
                WHERE ppops.hive_opid >= _begin
                    AND ppops.hive_opid <= _end
                    AND ppops.op_id = 'podping'
                ORDER BY ppops.block_num, ppops.id
            LOOP
                _id := temprow.id;
                _hive_opid := temprow.hive_opid;
                _block_num := temprow.block_num;
                _block_timestamp := temprow.timestamp;
                _required_auths := ARRAY (SELECT json_array_elements_text(temprow.req_auths));
                _required_posting_auths := ARRAY (SELECT json_array_elements_text(temprow.req_posting_auths));
                _op_id := temprow.op_id;
                _op_payload := (temprow.op_json)::json;
                _transaction_id := temprow.transaction_id;
                -- Make new entry
                WITH _ins AS (
                    INSERT INTO hpp.podping_ops(
                        ppop_id, block_num, created, transaction_id, req_auths,
                        req_posting_auths, op_id, op_payload)
                    VALUES
                        (_id, _block_num, _block_timestamp, _transaction_id, _required_auths,
                        _required_posting_auths, _op_id, _op_payload)
                    RETURNING pp_podping_opid
                )
                SELECT pp_podping_opid INTO _new_id FROM _ins;
                PERFORM hpp.podping_process_op(_new_id, _block_num, _block_timestamp, _required_posting_auths[1], _op_id, _op_payload);
            END LOOP;
            UPDATE hpp.plug_sync SET latest_hive_opid = _end WHERE plug_name='podping';
        END;
    $function$;

CREATE OR REPLACE FUNCTION hpp.podping_process_op(_pp_podping_opid BIGINT, _block_num BIGINT, _created TIMESTAMP, _posting_acc VARCHAR(16), _op_id VARCHAR(31), _payload JSON)
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            temprow RECORD;
            _url VARCHAR(500);
        BEGIN
            IF _op_id = 'podping' THEN
                PERFORM hpp.podping_process_podping(_pp_podping_opid, _block_num, _created, _posting_acc, _payload);
            END IF;
        END;
    $function$;

CREATE OR REPLACE FUNCTION hpp.podping_process_podping(_pp_podping_opid BIGINT, _block_num BIGINT, _created TIMESTAMP, _posting_acc VARCHAR(16), _payload JSON)
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            temprow RECORD;
            _reason VARCHAR;
            -- feed_update
            _url VARCHAR(500);
            _urls VARCHAR(500)[];
        BEGIN
            _reason := _payload ->> 'reason';
            IF _reason = 'feed_update' THEN
                _urls := ARRAY (SELECT json_array_elements_text((_payload ->> 'urls')::json));
                FOREACH _url IN ARRAY (_urls)
                LOOP
                    --RAISE NOTICE '%', _url;
                    INSERT INTO hpp.podping_feed_updates(pp_podping_opid, block_num, created, url)
                    VALUES (_pp_podping_opid, _block_num, _created, _url);
                END LOOP;
            END IF;
        END;
    $function$;