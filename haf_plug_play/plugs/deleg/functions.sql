CREATE OR REPLACE FUNCTION deleg.check_account( _acc VARCHAR(16))
    RETURNS BOOLEAN
    LANGUAGE plpgsql
    VOLATILE AS $function$
        BEGIN
            RETURN (
                SELECT EXISTS (
                    SELECT account FROM deleg.delegations_balances
                    WHERE account = _acc
                )
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
            -- TODO check account and create if not exists
            IF deleg.check_account(_delegatee) = false THEN
                INSERT INTO deleg.delegations_balances(account, given, received)
                VALUES (_delegatee, 0, _amount);
            ELSE
                -- add to received
                UPDATE deleg.delegations_balances SET
                    received = received + _amount
                WHERE account = _delegatee;
            END IF;
            IF deleg.check_account(_delegator) = false THEN
                INSERT INTO deleg.delegations_balances(account, given, received)
                VALUES (_delegator, _amount, 0);
            ELSE
                -- add to given
                UPDATE deleg.delegations_balances SET
                    given = given + _amount
                WHERE account = _delegator;
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
