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
            _required_auths := ARRAY (SELECT json_array_elements_text(body -> 'value' -> 'required_auths')::json);
            _required_posting_auths := ARRAY (SELECT json_array_elements_text(body -> 'value' -> 'required_posting_auths')::json);
            _op_id := _body -> 'value' ->> 'id';
            _op_payload := _body -> 'value'->> 'json'::json;
            -- process by Custom JSON ID
            
        END;
    $function$;