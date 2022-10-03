CREATE OR REPLACE FUNCTION hpp.get_haf_head_block()
    RETURNS INTEGER
    LANGUAGE plpgsql
    VOLATILE AS $function$
        BEGIN
            RETURN (SELECT MAX(block_num) FROM hive.hpp_operations_view);
        END;
    $function$;

CREATE OR REPLACE FUNCTION hpp.get_op_id( _operation VARCHAR )
    RETURNS SMALLINT
    LANGUAGE plpgsql
    VOLATILE AS $function$
        BEGIN
            RETURN (SELECT id FROM hive.operations_types
                WHERE name = FORMAT('hive::protocol::%s', _operation));
        END;
    $function$;

CREATE OR REPLACE FUNCTION hpp.plug_enabled( _plug VARCHAR)
    RETURNS BOOLEAN
    LANGUAGE plpgsql
    VOLATILE AS $function$
        BEGIN
            RETURN (SELECT defs->'props'->>'enabled' FROM hpp.plug_state WHERE plug=_plug);
        END;
    $function$;

CREATE OR REPLACE FUNCTION hpp.plug_running( _plug VARCHAR)
    RETURNS BOOLEAN
    LANGUAGE plpgsql
    VOLATILE AS $function$
        BEGIN
            RETURN (
                SELECT EXISTS (
                    SELECT pid FROM pg_stat_activity
                    WHERE query = FORMAT('CALL hpp.sync_plug( ''%s'' );', _plug)
                )
            );
        END;
    $function$;

CREATE OR REPLACE FUNCTION hpp.plug_long_running( _plug VARCHAR)
    RETURNS BOOLEAN
    LANGUAGE plpgsql
    VOLATILE AS $function$
        BEGIN
            RETURN (
                SELECT EXISTS (
                    SELECT * FROM hpp.plug_state
                    WHERE plug = _plug
                    AND check_in >= NOW() - INTERVAL '1 min'
                )
            );
        END;
    $function$;

CREATE OR REPLACE FUNCTION hpp.sync_enabled()
    RETURNS BOOLEAN
    LANGUAGE plpgsql
    VOLATILE AS $function$
        BEGIN
            RETURN (SELECT sync_enabled FROM hpp.global_props);
        END;
    $function$;


CREATE OR REPLACE FUNCTION hpp.plug_massive_synced( _plug VARCHAR)
    RETURNS BOOLEAN
    LANGUAGE plpgsql
    VOLATILE AS $function$
        BEGIN
            RETURN (SELECT massive_synced FROM hpp.plug_state WHERE plug=_plug);
        END;
    $function$;

CREATE OR REPLACE FUNCTION hpp.plug_flag_massive_synced( _plug VARCHAR)
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        BEGIN
            UPDATE hpp.plug_state SET massive_synced = true WHERE plug=_plug;
        END;
    $function$;

CREATE OR REPLACE FUNCTION hpp.terminate_main_sync(app_desc VARCHAR)
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            _pid INTEGER;
        BEGIN
            SELECT pid INTO _pid FROM pg_stat_activity
                WHERE application_name = app_desc;
            IF _pid IS NOT NULL THEN
                PERFORM pg_cancel_backend(_pid);
            END IF;
        END;
    $function$;

CREATE OR REPLACE FUNCTION hpp.is_sync_running(app_desc VARCHAR)
    RETURNS BOOLEAN
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
        BEGIN
            RETURN (
                SELECT EXISTS (
                    SELECT * FROM pg_stat_activity
                    WHERE application_name = app_desc
                )
            );
        END;
    $function$;