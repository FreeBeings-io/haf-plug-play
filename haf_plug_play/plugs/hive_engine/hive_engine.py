import os

from haf_plug_play.server.system_status import SystemStatus

WDIR_HIVE_ENGINE = os.path.dirname(__file__)

class Processor:

    def __init__(self) -> None:
        pass

    def processor(self):
        """Periodically validates ops and processes valid ones."""
        while True:
            pass
        # if valid then process immediately

class SearchQuery:

    @classmethod
    def get_he_ops(cls, contract_name:str, contract_action:str, limit:int=100):
        query = f"""
            SELECT block_num, created, op_payload->'contractPayload', req_auths, req_posting_auths
            FROM hive_engine.ops
            WHERE op_payload->>'contractName' = '{contract_name}' AND op_payload->>'contractAction' = '{contract_action}'
            ORDER BY id DESC
            LIMIT {limit};
        """
        return query

class StateQuery:

    pass

