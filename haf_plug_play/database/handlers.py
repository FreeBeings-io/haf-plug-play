from haf_plug_play.database.core import DbSession

class PlugPlayDb:
    """Avails method handlers for common DB operations and also exposes direct
       DB actions through `self.db.select`, `self.db.execute` and `self.db.execute_immediate`"""

    def __init__(self):
        self.db = DbSession()

    # TOOLS

    def _populate_by_schema(self, data, fields):
        result = {}
        for i in range(len(fields)):
            result[fields[i]] = data[i]
        return result


    # ACCESS METHODS

    def _select(self, table, columns=None, col_filters=None, order_by=None, limit=None):
        if columns:
            _columns = ', '.join(columns)
        else:
            _columns = "*"

        sql = f"SELECT {_columns} FROM {table}"

        if isinstance(col_filters, dict):
            _filters = []
            for col, value in col_filters.items():
                _filters.append (f"{col} = '{value}'")
            _final_filters = ' AND '.join(_filters)
            sql += f" WHERE {_final_filters}"
        elif isinstance(col_filters, str):
            sql += f" WHERE {col_filters}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        if limit:
            sql += f" LIMIT {limit}"
        sql += ";"
        return self.db.select(sql)
    
    def _select_one(self, table, col_filters):
        sql = f"SELECT 1 FROM {table}"
        if isinstance(col_filters, dict):
            _filters = []
            for col, value in col_filters.items():
                _filters.append (f"{col} = '{value}'")
            _final_filters = ' AND '.join(_filters)
            sql += f" WHERE {_final_filters}"
        elif isinstance(col_filters, str):
            sql += f" WHERE {col_filters}"
        return bool(self.db.select(sql))

    def _insert(self, table, data):
        _columns = []
        _values = []
        for col in data:
            _columns.append(col)
            if col == 'op_json':
                _values.append(f"json(%({col})s)")
            else:
                _values.append(f"%({col})s")
        columns = ', '.join(_columns)
        values = ', '.join(_values)
        sql = f"INSERT INTO {table} ({columns}) VALUES ({values})"
        sql += ";"
        self.db.execute(sql, data)

    def _update(self, table, data, col_filters= {}):
        _values = []
        for col, value in data.items():
            if value is None: continue
            _values.append (f"{col} = %({col})s")
        _final_values = ', '.join(_values)

        sql = f"UPDATE {table} SET {_final_values}"

        if isinstance(col_filters, dict):
            _filters = []
            for col, value in col_filters.items():
                _filters.append (f"{col} = %(f_{col})s")
                data[f"f_{col}"] = col_filters[col]
            _final_filters = ' AND '.join(_filters)
            sql += f" WHERE {_final_filters}"
        sql += ";"
        self.db.execute(sql, data)
    
    def _delete(self, table, col_filters):
        sql = f"DELETE FROM {table}"
        if isinstance(col_filters, dict):
            _filters = []
            for col in col_filters:
                _filters.append (f"{col} = %({col}s")
            _final_filters = ' AND '.join(_filters)
            sql += f" WHERE {_final_filters}"
        elif isinstance(col_filters, str):
            sql += f" WHERE {col_filters}"
        sql += ";"
        self.db.execute(sql, col_filters)

    def _save(self):
        self.db.commit()

    # STATUS

    def get_global_props(self):
        cols = ['head_hive_rowid', 'head_block_num', 'head_block_time']
        _res = self.db.select("SELECT * FROM hpp.global_props;")
        res = self._populate_by_schema(_res[0], cols)
        return res
