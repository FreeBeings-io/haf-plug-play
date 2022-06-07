
import json
import time
from threading import Thread
from haf_plug_play.config import Config

from haf_plug_play.database.access import alter_schema, perform, select, write
from haf_plug_play.database.handlers import get_global_latest_hpp_op_id, get_plug_latest_hpp_op_id
from haf_plug_play.server.system_status import SystemStatus
from haf_plug_play.tools import INSTALL_DIR

config = Config.config

class PlugSyncStatus:

    plug_state = {}

    @classmethod
    def set_plug_status(cls, plug, status):
        cls.plug_state[plug] = status
        SystemStatus.update_sync_status(plug_status=cls.plug_state)

class HookProcessor:

    def __init__(self, plug) -> None:
        self.plug = plug
        self.good = False
        self.start_block = None
        self.type_ids = []
        self.functions = {}
        try:
            self.wd = f'{INSTALL_DIR}/plugs/{self.plug}'
            self.functions = open(f'{self.wd}/functions.sql', 'r').read()
            self.tables = open(f'{self.wd}/tables.sql', 'r').read()
            self._defs = json.loads(open(f'{self.wd}/defs.json', 'r').read())
            self._get_plug_defs()
            alter_schema(self.functions)
            self.good = True
        except Exception as e:
            print(e)
            print(f"ERROR: ignoring incorrectly configured plug: '{self.plug}'")
            # TODO: log error
            pass

    def _get_plug_defs(self):
        self.start_block = self._defs['props']['start_block'] or config['global_start_block']
        has = select(f"SELECT plug FROM hpp.plug_state WHERE plug='{self.plug}'", ['plug'], True)
        defs = json.dumps(self._defs)
        start_op_id = select(f"SELECt hpp_op_id FROM hpp.ops WHERE block_num <= {self.start_block}", ['hpp_op_id'], True)
        if has is not None:
            # update
            sql = f"""
                UPDATE hpp.plug_state SET defs='{defs}', latest_hpp_op_id={start_op_id} WHERE plug='{self.plug}';
            """
        else:
            # insert
            sql = f"""
                    INSERT INTO hpp.plug_state (plug, hooks)
                    VALUES ('{self.plug}', '{defs}');
                """
        done = write(sql)
        if done is not True:
            raise Exception(f"Failed to save defs to DB for plug: '{self.plug}")
        
        for op in self._defs['ops']:
            _id = op[0]
            if _id not in self.type_ids:
                self.type_ids.append(_id)
            self.functions[_id] = op[1]
    
    def _get_func(self, op_type_id):
        notif_func = self.functions[op_type_id]
        return notif_func
    
    def _main_loop(self):
        while True:
            head_hpp_op_id = get_global_latest_hpp_op_id()
            cur_hpp_op_id = get_plug_latest_hpp_op_id(self.plug)
            if head_hpp_op_id - cur_hpp_op_id > 0:
                if cur_hpp_op_id == 0:
                    pass # get op id from start block
                PlugSyncStatus.set_plug_status(self.plug, 'synchronizing...')
                try:
                    done = perform('hpp.update_module', [self.plug, cur_hpp_op_id+1, head_hpp_op_id])
                    if not done:
                        # TODO: log
                        pass
                except Exception as err:
                    # TODO: log
                    print(err)
                    return
            PlugSyncStatus.set_plug_status(self.plug, 'synchronized')
            time.sleep(1)

    def start(self):
        if self.good:
            Thread(target=self._main_loop).start()
            PlugSyncStatus.set_plug_status(self.plug, 'started')
            print(f"'{self.module}' module started.")
