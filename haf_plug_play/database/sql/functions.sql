CREATE OR REPLACE FUNCTION hpp.get_op_id( _operation VARCHAR )
    RETURNS SMALLINT
    LANGUAGE plpgsql
    VOLATILE AS $function$
        BEGIN
            RETURN SELECT id FROM hive.operations_types
                WHERE name = FORMAT('hive::protocol::%s', _operation);
    $function$;

CREATE OR REPLACE FUNCTION hpp.start_plug_sync( _plug VARCHAR )
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            plug_schema VARCHAR;
            done BOOLEAN;
        BEGIN
            SELECT defs->'props'->>'schema' INTO plug_schema
                FROM hpp.plug_state
                WHERE plug = plug;
            IF plug_schema IS NOT NULL THEN
                -- record run start
                done:= EXECUTE FORMAT('SELECT %s.sync();', plug_schema);
                -- save done as run end
            ELSE
                RAISE NOTICE 'Attempted to start a missing plug: %', plug;
                RETURN;

        EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE E'Got exception:
                SQLSTATE: % 
                SQLERRM: %', SQLSTATE, SQLERRM;
        END;
    $function$;

CREATE OR REPLACE PROCEDURE hpp.process_block_range(_plug_name VARCHAR, _app_context VARCHAR, _start BIGINT, _end BIGINT, _ops JSON )
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            _plug_schema VARCHAR;
            _done BOOLEAN;
            _massive BOOLEAN;
            _first_block BIGINT;
            _last_block BIGINT;
            _step BIGINT;
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
        EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE E'Got exception:
                SQLSTATE: % 
                SQLERRM: %', SQLSTATE, SQLERRM;
        END;
    $function$;
