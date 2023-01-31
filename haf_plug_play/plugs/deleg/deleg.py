import os

from haf_plug_play.server.system_status import SystemStatus
from haf_plug_play.tools import schemafy

WDIR_DELEG = os.path.dirname(__file__)

class SearchQuery:

    pass

class StateQuery:

    @classmethod
    def get_deleg_account_bals(cls, account:str):
        query = f"""
            SELECT deleg.get_acc_bals('{account}')
        """
        return schemafy(query, 'deleg')

    @classmethod
    def get_deleg_in(cls, account:str):
        query = f"""
            SELECT id, created, delegator, round((amount::numeric)/1000000, 6)
            FROM deleg.delegations_vesting
            WHERE amount > 0 AND delegatee = '{account}'
            ORDER BY id ASC
        """
        return schemafy(query, 'deleg')
    
    @classmethod
    def get_deleg_out(cls, account:str):
        query = f"""
            SELECT id, created, delegatee, round((amount::numeric)/1000000, 6)
            FROM deleg.delegations_vesting
            WHERE amount > 0 AND delegator = '{account}'
            ORDER BY id ASC
        """
        return schemafy(query, 'deleg')