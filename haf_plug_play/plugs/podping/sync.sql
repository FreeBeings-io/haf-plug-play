-- check context


CREATE OR REPLACE FUNCTION podping.sync()
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            temprow RECORD;
            _appContext VARCHAR;
            _next_block_range hive.blocks_range;
            _head_hive_opid BIGINT;
            _latest_hive_opid BIGINT;
            _latest_block_num BIGINT;
            _range BIGINT[];
            _url VARCHAR(500);
        BEGIN

            _appContext := 'podping';

            SELECT latest_block_num INTO _latest_block_num FROM hpp.plug_sync WHERE plug = 'podping';
            IF NOT hive.app_context_is_attached(_appContext) THEN
                PERFORM hive.app_context_attach(_appContext, _latest_block_num);
            END IF;

            -- LOOP
                -- check latest hive_opid
                SELECT latest_hive_opid INTO _latest_hive_opid FROM hpp.plug_sync WHERE plug = 'podping';
                SELECT MAX(id) INTO _head_hive_opid FROM hive.operations; -- TODO reversible if in def
                SELECT 
                -- process
                WHILE hpp.plug_enabled('podping') LOOP
                    _next_block_range := hive.app_next_block(_appContext);
                    IF _next_block_range IS NULL THEN
                        RAISE WARNING 'Waiting for next block...';
                    ELSE
                        RAISE NOTICE 'Attempting to process block range: <%,%>', __next_block_range.first_block, __next_block_range.last_block;
                        IF _next_block_range.first_block != _next_block_range.last_block THEN
                            CALL podping.do_massive_processing(_appContext, _next_block_range.first_block, _next_block_range.last_block, 100, latest_block_num);
                        ELSE
                            CALL podping.process_block(_next_block_range.last_block);
                        END IF;



        END;
    $function$;