-- TOKENS OPS

CREATE OR REPLACE FUNCTION hive_engine.nfts(_he_id BIGINT, _block_num BIGINT, _created TIMESTAMP, _acc VARCHAR(16), _payload JSON)
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$

        DECLARE
            _action VARCHAR;
            _symbol VARCHAR(10);
            _to VARCHAR(16);
            _quantity 
        BEGIN
            IF _action = 'create' THEN
                INSERT INTO hive_engine.nfts(he_id, block_num, created, owners, issuer_accs, issuer_conts)
                VALUES (_he_id, _block_num, _created, );
        END;
    $function$;

--- SAVE OPS

CREATE OR REPLACE FUNCTION hive_engine.save_op(_block_num BIGINT, _created TIMESTAMP, _hash BYTEA,  _required_auths VARCHAR(16)[], _required_posting_auths VARCHAR(16)[], _op_id VARCHAR(31), _op_payload JSON)
    RETURNS BIGINT
    LANGUAGE plpgsql
    VOLATILE AS $function$

        DECLARE
            _reason VARCHAR;
            _urls VARCHAR(500)[];
            _new_id BIGINT;
        BEGIN
            WITH _ins AS (
                INSERT INTO hive_engine.ops(
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

CREATE OR REPLACE FUNCTION hive_engine.process_cjop(_block_num INTEGER, _created TIMESTAMP, _hash BYTEA, _body JSON)
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$

        DECLARE
            _required_auths VARCHAR(16)[];
            _required_posting_auths VARCHAR(16)[];
            _op_id VARCHAR;
            _op_payload JSON;
            _contract VARCHAR;
            _saved_id BIGINT;
        BEGIN
            _required_auths := ARRAY (SELECT json_array_elements_text(_body -> 'value' -> 'required_auths'));
            _required_posting_auths := ARRAY (SELECT json_array_elements_text(_body -> 'value' -> 'required_posting_auths'));
            _op_id := _body -> 'value' ->> 'id';
            _op_payload := (_body -> 'value'->>'json')::json;
            -- process by Custom JSON ID  TODO: implement defs based filters
            IF _op_id = 'ssc-mainnet-hive' THEN
                -- save op
                _saved_id := hive_engine.save_op(_block_num, _created, _hash, _required_auths, _required_posting_auths, _op_id, _op_payload);
                _contract := _op_payload ->> 'contractName';
                IF _contract = 'tokens' THEN
                    PERFORM hive_engine.tokens(_saved_id, _block_num, _created, _op_payload);
                ELSIF _contract = 'nft' THEN
                    PERFORM hive_engine.nfts(_saved_id, _block_num, _created, _op_payload);
                END IF;
            END IF;
        END;
    $function$;