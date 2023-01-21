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
            
            SELECT account, SUM(round((given::numeric)/1000000, 3), SUM(round((received::numeric)/1000000, 3)
            FROM deleg.delegations_balances
            WHERE account = '{account}';
        """
        return schemafy(query, 'deleg')
