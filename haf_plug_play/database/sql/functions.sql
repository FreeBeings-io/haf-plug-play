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
