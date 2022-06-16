CREATE OR REPLACE FUNCTION podping.process_cjop(_block_num BIGINT, _created TIMESTAMP, _hash BYTEA, _body JSON)
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$

        DECLARE
            _required_auths VARCHAR(16)[];
            _required_posting_auths VARCHAR(16)[];
            _op_id VARCHAR(31);
            _op_payload JSON;
            _new_id BIGINT;
        BEGIN
            
        END;
    $function$;