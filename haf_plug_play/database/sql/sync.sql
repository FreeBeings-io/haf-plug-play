
CREATE OR REPLACE PROCEDURE hpp.sync_main()
    LANGUAGE plpgsql
    AS $$
        DECLARE
            tempplug RECORD;
            plugs VARCHAR(64)[];
            _plug VARCHAR(64);
        BEGIN
            SELECT ARRAY(SELECT plug FROM hpp.plug_state) INTO plugs;
            WHILE hpp.sync_enabled() LOOP
                FOREACH _plug IN ARRAY plugs
                LOOP
                    IF hpp.plug_enabled(_plug) = true THEN
                        RAISE NOTICE 'Attempting to sync plug: %', _plug;
                        CALL hpp.sync_plug(_plug);
                        COMMIT;
                        RAISE NOTICE 'Plug synced: %', _plug;
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
            _ops JSON;
            _op_ids SMALLINT[];
            _latest_block_num INTEGER;
            _range BIGINT[];
            _batch_size INTEGER := 10000;
            _head INTEGER;
            _end INTEGER;
        BEGIN
            SELECT defs->'ops' INTO _ops FROM hpp.plug_state WHERE plug = _plug_name;
            SELECT ARRAY (SELECT json_array_elements_text(defs->'op_ids')) INTO _op_ids FROM hpp.plug_state WHERE plug = _plug_name;

            SELECT latest_block_num INTO _latest_block_num FROM hpp.plug_state WHERE plug = _plug_name;
            -- SELECT latest_hive_opid INTO _latest_hive_opid FROM hpp.plug_state WHERE plug = _plug_name;
            -- SELECT MAX(id) INTO _head_hive_opid FROM hive.operations; -- TODO reversible if in def
            -- start process
            -- RAISE NOTICE 'Attempting to process block range: <%,%>', _next_block_range.first_block, _next_block_range.last_block;
            _head := hive.app_get_irreversible_block();
            IF _latest_block_num+1 < _head THEN
                IF _latest_block_num+_batch_size > _head THEN
                    _end := _head;
                ELSE
                    _end := _latest_block_num+_batch_size;
                END IF;
                CALL hpp.process_block_range(_plug_name, _latest_block_num+1, _end, _ops, _op_ids);
            END IF;
        END;
    $$;

CREATE OR REPLACE PROCEDURE hpp.process_block_range(_plug_name VARCHAR, _start INTEGER, _end INTEGER, _ops JSON, _op_ids SMALLINT[] )
    LANGUAGE plpgsql
    AS $$

        DECLARE
            temprow RECORD;
            _plug_schema VARCHAR;
            _done BOOLEAN;
            _first_block INTEGER;
            _last_block INTEGER;
            _last_block_time TIMESTAMP;
        BEGIN
            RAISE NOTICE '%:  Attempting to process a block range: <%, %>', _plug_name, _start, _end;
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
                        ov.body::varchar::json
                    FROM hive.operations_view ov
                    JOIN hive.transactions_view tv
                        ON tv.block_num = ov.block_num
                        AND tv.trx_in_block = ov.trx_in_block
                    WHERE ov.block_num >= $1
                        AND ov.block_num <= $2
                        AND ov.op_type_id = ANY ($3)
                    ORDER BY ov.block_num, ov.id;')
                USING _start, _end, _op_ids
            LOOP
                EXECUTE FORMAT('SELECT %s ($1,$2,$3,$4);', (_ops->>(temprow.op_type_id::varchar)))
                    USING temprow.block_num, temprow.timestamp, temprow.trx_hash, temprow.body;
                _last_block_time := temprow.timestamp;
            END LOOP;
            -- save done as run end
            RAISE NOTICE '%:  Block range: <%, %> processed successfully.', _plug_name, _start, _end;
            UPDATE hpp.plug_state
                SET check_in = (NOW() AT TIME ZONE 'UTC'), latest_block_time = _last_block_time, latest_block_num = _end
                WHERE plug = _plug_name;
        END;
    $$;