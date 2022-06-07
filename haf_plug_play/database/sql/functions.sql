CREATE OR REPLACE FUNCTION hpp.update_ops( _first_block BIGINT, _last_block BIGINT )
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            temprow RECORD;
            _hive_opid BIGINT;
            _block_num INTEGER;
            _block_timestamp TIMESTAMP;
            _hive_op_type_id SMALLINT;
            _transaction_id VARCHAR(40);
            _body JSON;
            _hash VARCHAR;
            _new_id BIGINT;
        BEGIN
            FOR temprow IN
                SELECT
                    hppov.id AS hive_opid,
                    hppov.op_type_id,
                    hppov.block_num,
                    hppov.timestamp,
                    hppov.trx_in_block,
                    hppov.body
                FROM hive.hpp_operations_view hppov
                WHERE hppov.block_num >= _first_block
                    AND hppov.block_num <= _last_block
                ORDER BY hppov.block_num, trx_in_block, hppov.id
            LOOP
                _hive_opid := temprow.hive_opid;
                _block_num := temprow.block_num;
                _block_timestamp = temprow.timestamp;
                _hash := (
                    SELECT hpptv.trx_hash FROM hive.hpp_transactions_view hpptv
                    WHERE hpptv.block_num = temprow.block_num
                    AND hpptv.trx_in_block = temprow.trx_in_block);
                _transaction_id := encode(_hash::bytea, 'escape');
                _hive_op_type_id := temprow.op_type_id;
                _body := (temprow.body)::json;

                WITH _ins AS (
                    INSERT INTO hpp.ops(
                        hive_opid, op_type_id, block_num, created, transaction_id, body)
                    VALUES
                        (_hive_opid, _hive_op_type_id, _block_num, _block_timestamp, _transaction_id, _body)
                    RETURNING hpp_op_id
                )
                SELECT hpp_op_id INTO _new_id FROM _ins;
            END LOOP;
            UPDATE hpp.global_props 
            SET latest_block_num = _block_num,
                latest_hive_rowid = _hive_opid,
                latest_hpp_op_id = _new_id,
                latest_block_time = _block_timestamp;
        END;
    $function$;

CREATE OR REPLACE FUNCTION hpp.update_module( _module VARCHAR(128), _start_hpp_op_id BIGINT, _end_hpp_op_id BIGINT )
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$
        DECLARE
            temprow RECORD;
            _hooks JSON;
            _code VARCHAR(3);
            _funct VARCHAR;
            _op_ids INT[];
        BEGIN
            SELECT hooks INTO _hooks FROM hpp.module_state WHERE module = _module;
            _op_ids := ARRAY(SELECT json_array_elements_text(_hooks->'ids'));
            IF _hooks IS NOT NULL THEN
                FOR temprow IN
                    SELECT
                        hpp_op_id, op_type_id, created,
                        transaction_id, body
                    FROM hpp.ops
                    WHERE op_type_id = ANY (_op_ids)
                    AND hpp_op_id >= _start_hpp_op_id
                    AND hpp_op_id <= _end_hpp_op_id
                ORDER BY hpp_op_id ASC
                LOOP
                    _code := _hooks->temprow.op_type_id::varchar->>'code';
                    _funct := _hooks->temprow.op_type_id::varchar->>'func';
                    EXECUTE FORMAT('SELECT %s ($1,$2,$3,$4,$5);', _funct) USING temprow.hpp_op_id, temprow.transaction_id, temprow.created, temprow.body, _code;
                END LOOP;
                UPDATE hpp.module_state
                SET latest_hpp_op_id = _end_hpp_op_id
                WHERE module = _module;
            END IF;
        EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE E'Got exception:
                SQLSTATE: % 
                SQLERRM: %', SQLSTATE, SQLERRM;
        END;
    $function$;
