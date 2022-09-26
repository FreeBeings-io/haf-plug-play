-- check context

CREATE OR REPLACE PROCEDURE hpp.sync_main()
    LANGUAGE plpgsql
    AS $$
        DECLARE
            tempplug RECORD;
        BEGIN
            WHILE hpp.sync_enabled() LOOP
                FOR tempplug IN
                    SELECT * FROM hpp.plug_state 
                LOOP
                    IF tempplug.enabled = true THEN
                        RAISE NOTICE 'Attempting to sync plug: %', tempplug.plug;
                        CALL hpp.sync_plug(tempplug.plug);
                        RAISE NOTICE 'Plug synced: %', tempplug.plug;
                    END IF;
                END LOOP;
            END LOOP;
        END;
    $$;

CREATE OR REPLACE PROCEDURE hpp.sync_plug(_plug_name VARCHAR(64))
    LANGUAGE plpgsql
    AS $$
        DECLARE
            temprow RECORD;
            _app_context VARCHAR;
            _ops JSON;
            _op_ids SMALLINT[];
            _latest_block_num INTEGER;
            _range BIGINT[];
            _batch_size INTEGER := 1000;
            _head INTEGER;
            _end INTEGER;
        BEGIN
            SELECT defs->'props'->>'context' INTO _app_context FROM hpp.plug_state WHERE plug = _plug_name;
            SELECT defs->'ops' INTO _ops FROM hpp.plug_state WHERE plug = _plug_name;
            SELECT ARRAY (SELECT json_array_elements_text(defs->'op_ids')) INTO _op_ids FROM hpp.plug_state WHERE plug = _plug_name;

            SELECT latest_block_num INTO _latest_block_num FROM hpp.plug_state WHERE plug = _plug_name;
            -- SELECT latest_hive_opid INTO _latest_hive_opid FROM hpp.plug_state WHERE plug = _plug_name;
            -- SELECT MAX(id) INTO _head_hive_opid FROM hive.operations; -- TODO reversible if in def
            -- start process
            --RAISE NOTICE 'Attempting to process block range: <%,%>', _next_block_range.first_block, _next_block_range.last_block;
            _head := hpp.get_haf_head_block();
            IF _latest_block_num+1 < _head THEN
                IF _latest_block_num+_batch_size > _head THEN
                    _end := _head;
                ELSE
                    _end := _latest_block_num+_batch_size;
                END IF;
                CALL hpp.process_block_range(_plug_name, _app_context, _latest_block_num+1, _end, _ops, _op_ids);
                COMMIT;
            END IF;
        END;
    $$;

CREATE OR REPLACE PROCEDURE hpp.process_block_range(_plug_name VARCHAR, _app_context VARCHAR, _start INTEGER, _end INTEGER, _ops JSON, _op_ids SMALLINT[] )
    LANGUAGE plpgsql
    AS $$

        DECLARE
            temprow RECORD;
            _plug_schema VARCHAR;
            _done BOOLEAN;
            _first_block INTEGER;
            _last_block INTEGER;
            _last_block_time TIMESTAMP;
            _step INTEGER;
        BEGIN
            _step := 100000;
            -- determine if massive sync is needed
            -- get defs
            -- _arr := ARRAY(SELECT json_array_elements_text(_ops));
            -- _op_ids := array_agg(SELECT unnest(_arr[1:999][1]));

            -- divide range
            FOR _first_block IN _start .. _end BY _step LOOP
                _last_block := _first_block + _step - 1;

                IF _last_block > _end THEN --- in case the _step is larger than range length
                    _last_block := _end;
                END IF;

                RAISE NOTICE 'Attempting to process a block range: <%, %>', _first_block, _last_block;
                -- record run start
                    -- select records and pass records to relevant functions
                FOR temprow IN
                    EXECUTE FORMAT('
                        SELECT
                            ov.id,
                            ov.op_type_id,
                            ov.block_num,
                            ov.timestamp,
                            ov.trx_in_block,
                            tv.trx_hash,
                            ov.body::json
                        FROM hive.hpp_operations_view ov
                        LEFT JOIN hive.hpp_transactions_view tv
                            ON tv.block_num = ov.block_num
                            AND tv.trx_in_block = ov.trx_in_block
                        WHERE ov.block_num >= $1
                            AND ov.block_num <= $2
                            AND ov.op_type_id = ANY ($3)
                        ORDER BY ov.block_num, ov.id;')
                    USING _first_block, _last_block, _op_ids
                LOOP
                    EXECUTE FORMAT('SELECT %s ($1,$2,$3,$4);', (_ops->>(temprow.op_type_id::varchar)))
                        USING temprow.block_num, temprow.timestamp, temprow.trx_hash, temprow.body;
                    _last_block_time := temprow.timestamp;
                END LOOP;
                -- save done as run end
                RAISE NOTICE 'Block range: <%, %> processed successfully.', _first_block, _last_block;
                UPDATE hpp.plug_state
                    SET check_in = (NOW() AT TIME ZONE 'UTC'), latest_block_time = _last_block_time, latest_block_num = _last_block
                    WHERE plug = _plug_name;
                COMMIT;
            END LOOP;
        END;
    $$;