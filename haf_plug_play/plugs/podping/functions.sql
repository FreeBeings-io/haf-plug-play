-- VERSION 0.3

CREATE OR REPLACE FUNCTION podping.update(_podping_id BIGINT, _block_num BIGINT, _created TIMESTAMP, _payload JSON)
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$

        DECLARE
            _version VARCHAR;
            _urls VARCHAR(500)[];
            _url VARCHAR(500);
            _reason VARCHAR;
            _medium VARCHAR;
        BEGIN
            _version := _payload ->> 'version';
            _reason := _payload ->> 'reason';
            _medium := _payload ->> 'medium';
            IF _version = '0.3' THEN
                _urls := ARRAY (SELECT json_array_elements_text((_payload ->> 'urls')::json));
                FOREACH _url IN ARRAY (_urls)
                LOOP
                    --RAISE NOTICE '%', _url;
                    INSERT INTO podping.updates(podping_id, block_num, created, url, reason, medium)
                    VALUES (_podping_id, _block_num, _created, _url, _reason, 'podcast');
                END LOOP;
            ELSIF _version = '1.0' THEN
                _urls := ARRAY (SELECT json_array_elements_text((_payload ->> 'iris')::json));
                FOREACH _url IN ARRAY (_urls)
                LOOP
                    --RAISE NOTICE '%', _url;
                    INSERT INTO podping.updates(podping_id, block_num, created, url, reason, medium)
                    VALUES (_podping_id, _block_num, _created, _url, _reason, _medium);
                END LOOP;
            END IF;
        END;
    $function$;



--- SAVE OPS
CREATE OR REPLACE FUNCTION podping.save_op(_block_num BIGINT, _created TIMESTAMP, _hash BYTEA,  _required_auths VARCHAR(16)[], _required_posting_auths VARCHAR(16)[], _op_id VARCHAR(31), _op_payload JSON)
    RETURNS BIGINT
    LANGUAGE plpgsql
    VOLATILE AS $function$

        DECLARE
            _reason VARCHAR;
            _new_id BIGINT;
        BEGIN
            WITH _ins AS (
                INSERT INTO podping.ops(
                    block_num, created, trx_id, req_auths,
                    req_posting_auths, op_id, op_payload)
                VALUES
                    (_block_num, _created, _hash, _required_auths,
                    _required_posting_auths, _op_id, _op_payload)
                RETURNING id
            )
            SELECT id INTO _new_id FROM _ins;
            RETURN _new_id;
        END;
    $function$;


-- CORE

CREATE OR REPLACE FUNCTION podping.process_cjop(_block_num INTEGER, _created TIMESTAMP, _hash BYTEA, _body JSON)
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$

        DECLARE
            _required_auths VARCHAR(16)[];
            _required_posting_auths VARCHAR(16)[];
            _op_id VARCHAR;
            _op_payload JSON;
            _version VARCHAR;
            _saved_id BIGINT;
        BEGIN
            _required_auths := ARRAY (SELECT json_array_elements_text(_body -> 'value' -> 'required_auths'));
            _required_posting_auths := ARRAY (SELECT json_array_elements_text(_body -> 'value' -> 'required_posting_auths'));
            _op_id := _body -> 'value' ->> 'id';
            _op_payload := (_body -> 'value'->>'json')::json;
            -- process by Custom JSON ID  TODO: implement defs based filters
            IF _op_id IN ('podping','pp_video_update') THEN
                -- save op
                _saved_id := podping.save_op(_block_num, _created, _hash, _required_auths, _required_posting_auths, _op_id, _op_payload);
                PERFORM podping.update(_saved_id, _block_num, _created, _op_payload);
            END IF;

        EXCEPTION WHEN SQLSTATE '22P02' THEN
            -- invalid JSON input
            RAISE NOTICE E'Got exception:
            SQLSTATE: % 
            SQLERRM: %', SQLSTATE, SQLERRM;
        END;
    $function$;