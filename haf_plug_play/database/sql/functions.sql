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

CREATE OR REPLACE FUNCTION hpp.terminate_sync( _plug VARCHAR)
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            _pid INTEGER;
        BEGIN
            _pid := SELECT pid FROM pg_stat_activity
                    WHERE query = FORMAT('CALL hpp.sync_plug( ''%s'' );', _plug)
            IF _pid IS NOT NULL THEN
                SELECT pg_cancel_backend(_pid);
            END IF;
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
