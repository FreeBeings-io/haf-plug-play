CREATE OR REPLACE FUNCTION deleg.check_account_pair(_delegator VARCHAR(16), _delegatee VARCHAR(16))
    RETURNS BOOLEAN
    LANGUAGE plpgsql
    VOLATILE AS $function$
        BEGIN
            RETURN (
                SELECT EXISTS (
                    SELECT amount FROM deleg.delegations_balances
                    WHERE delegator = _delegator AND delegatee = _delegatee
                )
            );
        END;
    $function$;

CREATE OR REPLACE FUNCTION deleg.get_acc_bals(_acc VARCHAR(16))
    RETURNS JSONB
    LANGUAGE plpgsql
    VOLATILE AS $function$

        DECLARE
            _received BIGINT;
            _given BIGINT;
        BEGIN
            SELECT SUM(amount)
            INTO _received
            FROM deleg.delegations_balances
            WHERE delegatee = _acc;

            SELECT SUM(amount)
            INTO _given
            FROM deleg.delegations_balances
            WHERE delegator = _acc;
            
            RETURN jsonb_build_object(
                'in',COALESCE(round((_received::numeric)/1000000, 6),0),
                'out',COALESCE(round((_given::numeric)/1000000, 6),0)
            );
        END;
    $function$;

CREATE OR REPLACE FUNCTION deleg.process_create_deleg(_block_num INTEGER, _created TIMESTAMP, _hash BYTEA, _body JSON)
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$

        DECLARE
            _delegator VARCHAR(16);
            _delegatee VARCHAR(16);
            _amount BIGINT;
        BEGIN
            _delegator := _body -> 'value' ->> 'delegator';
            _delegatee := _body -> 'value' ->> 'delegatee';
            _amount := _body -> 'value' -> 'vesting_shares' ->> 'amount';

            INSERT INTO deleg.delegations_vesting(
                block_num, created, trx_id, delegator, delegatee, amount)
            VALUES (
                _block_num, _created, _hash, _delegator, _delegatee, _amount
            );
/*
            -- update received balance
            UPDATE deleg.delegations_balances SET
                    received = received + _amount
                WHERE account = _delegatee
            ON CONFLICT (account)
                INSERT INTO deleg.delegations_balances(account, given, received)
                VALUES (_delegatee, 0, _amount);

            -- update given balance
            UPDATE deleg.delegations_balances SET
                    given = given + _amount
                WHERE account = _delegator
            ON CONFLICT (account)
                INSERT INTO deleg.delegations_balances(account, given, received)
                VALUES (_delegator, _amount, 0);
*/
            -- TODO check account pair and create if not exists
            IF deleg.check_account_pair(_delegator, _delegatee) = false THEN
                INSERT INTO deleg.delegations_balances(delegator, delegatee, amount)
                VALUES (_delegator, _delegatee, _amount);
            ELSE
                -- update amount
                UPDATE deleg.delegations_balances SET
                    amount = _amount
                WHERE delegator = _delegator AND delegatee = _delegatee;
            END IF;
        END;
    $function$;

CREATE OR REPLACE FUNCTION deleg.process_return_deleg(_block_num INTEGER, _created TIMESTAMP, _hash BYTEA, _body JSON)
    RETURNS void
    LANGUAGE plpgsql
    VOLATILE AS $function$

        DECLARE
            _account VARCHAR(16);
            _amount BIGINT;
        BEGIN
            _account := _body -> 'value' ->> 'account';
            _amount := _body -> 'value' -> 'vesting_shares' ->> 'amount';

            INSERT INTO deleg.delegations_vesting_returns(
                block_num, created, trx_id, account)
            VALUES (
                _block_num, _created, _hash, _delegator, _delegatee, _amount
            );

            -- TODO: check if acc exists, create if not

            UPDATE deleg.delegations_balances SET
                given = given - _amount
            WHERE account = _account;
            -- TODO: deduct from received account

        END;
    $function$;
