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

            _app_context := SELECT defs->'props'->>'context' FROM hpp.plug_state WHERE plug = _plug_name;
            _ops := SELECT defs->'defs'->'ops' FROM hpp.plug_state WHERE plug = _plug_name;

            IF _app_context IS NULL THEN
                RAISE NOTICE 'Could not start sync for plug: %. DB entry not found.', _plug_name;
                RETURN
            END IF;

            SELECT latest_block_num INTO _latest_block_num FROM hpp.plug_sync WHERE plug = _plug_name;
            IF NOT hive.app_context_is_attached(_app_context) THEN
                PERFORM hive.app_context_attach(_app_context, _latest_block_num);
            END IF;

            -- LOOP
                -- check latest hive_opid
                SELECT latest_hive_opid INTO _latest_hive_opid FROM hpp.plug_sync WHERE plug = _plug_name;
                SELECT MAX(id) INTO _head_hive_opid FROM hive.operations; -- TODO reversible if in def
                -- process
                WHILE hpp.plug_enabled(_plug_name) LOOP
                    _next_block_range := hive.app_next_block(_app_context);
                    IF _next_block_range IS NULL THEN
                        RAISE WARNING 'Waiting for next block...';
                    ELSE
                        RAISE NOTICE 'Attempting to process block range: <%,%>', _next_block_range.first_block, _next_block_range.last_block;
                        CALL hpp.process_block_range(_plug_name, _app_context, _next_block_range.first_block, _next_block_range.last_block, _ops);
                    END IF;

        END;
    $function$;