-- check context

CREATE OR REPLACE FUNCTION hpp.sync_plug(_plug_name VARCHAR(64))
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            temprow RECORD;
            _app_context VARCHAR;
            _ops JSON;
            _next_block_range hive.blocks_range;
            _head_hive_opid BIGINT;
            _latest_hive_opid BIGINT;
            _latest_block_num BIGINT;
            _range BIGINT[];
        BEGIN
            SELECT defs->'props'->>'context' INTO _app_context FROM hpp.plug_state WHERE plug = _plug_name;
            SELECT defs->'defs'->'ops' INTO _ops FROM hpp.plug_state WHERE plug = _plug_name;

            IF _app_context IS NULL THEN
                RAISE NOTICE 'Could not start sync for plug: %. DB entry not found.', _plug_name;
                RETURN;
            END IF;

            SELECT latest_block_num INTO _latest_block_num FROM hpp.plug_state WHERE plug = _plug_name;
            IF NOT hive.app_context_is_attached(_app_context) THEN
                PERFORM hive.app_context_attach(_app_context, _latest_block_num);
            END IF;
            -- check latest hive_opid
            -- SELECT latest_hive_opid INTO _latest_hive_opid FROM hpp.plug_state WHERE plug = _plug_name;
            -- SELECT MAX(id) INTO _head_hive_opid FROM hive.operations; -- TODO reversible if in def
            -- start process
            WHILE hpp.plug_enabled(_plug_name) LOOP
                _next_block_range := hive.app_next_block(_app_context);
                IF _next_block_range IS NULL THEN
                    RAISE WARNING 'Waiting for next block...';
                ELSE
                    RAISE NOTICE 'Attempting to process block range: <%,%>', _next_block_range.first_block, _next_block_range.last_block;
                    CALL hpp.process_block_range(_plug_name, _app_context, _next_block_range.first_block, _next_block_range.last_block, _ops);
                END IF;
            END LOOP;
            UPDATE hpp.plug_state SET run_start = false WHERE plug = _plug_name;
            UPDATE hpp.plug_state SET run_finish = false WHERE plug = _plug_name;
        END;
    $function$;

CREATE OR REPLACE PROCEDURE hpp.process_block_range(_plug_name VARCHAR, _app_context VARCHAR, _start BIGINT, _end BIGINT, _ops JSON )
    LANGUAGE plpgsql
    AS
        $$
        DECLARE
            _plug_schema VARCHAR;
            _done BOOLEAN;
            _massive BOOLEAN;
            _first_block BIGINT;
            _last_block BIGINT;
            _step BIGINT;
            _op_ids SMALLINT[];
        BEGIN
            _step := 1000;
            -- determine if massive sync is needed
            IF _end - _start > 0 THEN
                -- detach context
                PERFORM hive.app_context_detach(_app_context);
                _massive := true;
            END IF;
            -- get defs
            -- _arr := ARRAY(SELECT json_array_elements_text(_ops));
            -- _op_ids := array_agg(SELECT unnest(_arr[1:999][1]));
            _op_ids := json_object_keys(_ops);

            -- divide range
            FOR _first_block IN _start .. _end BY _step LOOP
                _last_block := _first_block + _step - 1;

                IF _last_block > _end THEN --- in case the _step is larger than range length
                _last_block := _end;
                END IF;

                RAISE NOTICE 'Attempting to process a block range: <%, %>', _first_block, _last_block;
                -- record run start
                UPDATE hpp.plug_state SET run_start = true WHERE plug = _plug_name;
                    -- select records and pass records to relevant functions
                    EXECUTE FORMAT('
                        FOR temprow IN
                            SELECT
                                %1$sov.id,
                                %1$sov.op_type_id,
                                %1$sov.block_num,
                                %1$sov.timestamp,
                                %1$sov.trx_in_block,
                                %1$stv.trx_hash,
                                %1$sov.body
                            FROM hive.%1$s_operations_view %1$sov
                            LEFT JOIN hive.%1$s_transactions_view %1$stv
                                ON %1$stv.block_num = %1$sov.block_num
                                AND %1$stv.trx_in_block = %1$sov.trx_in_block
                            WHERE %1$sov.block_num >= $1
                                AND %1$sov.block_num <= $2
                                AND %1$sov.op_type_id = ANY ($1)
                            ORDER BY %1$sov.block_num, trx_in_block, %1$sov.id
                        LOOP
                            PERFORM ( block_num, timestamp, trx_hash, body, $3->op_type_id::varchar );
                        END LOOP;
                        ;', _app_context) USING _first_block, _last_block, _op_ids;
                -- save done as run end
                COMMIT;
                RAISE NOTICE 'Block range: <%, %> processed successfully.', _first_block, _last_block;
            END LOOP;
            IF _massive = true THEN
                -- attach context
                PERFORM hive.app_context_attach(_app_context, _last_block);
            END IF;
        END;
        $$;