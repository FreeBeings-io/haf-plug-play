from haf_plug_play.database.core import DbSession
from haf_plug_play.tools import populate_by_schema, normalize_types

_read_db = DbSession("read")

def select(sql:str, schema:list, one:bool = False):
    _res = _read_db.select(sql)
    res = []
    if _res:
        assert len(schema) == len(_res[0]), 'invalid schema'
        for x in _res:
            res.append(populate_by_schema(x,schema))
        if one:
            return normalize_types(res)[0]
        else:
            return normalize_types(res)
