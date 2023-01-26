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
