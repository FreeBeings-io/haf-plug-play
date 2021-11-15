import os

from haf_plug_play.server.system_status import SystemStatus

WDIR_COMMUNITY = os.path.dirname(__file__)

class SearchOps:

    @classmethod
    def subscribe(cls, community, block_range=None):
        """
            "subscribe"    | {"community":"hive-178179"}
        """
        if block_range is None:
            latest = SystemStatus.get_latest_block()
            if not latest: return None # TODO: notify??
            block_range = [latest - 28800, latest]
        query = f"""
            SELECT *  
            FROM (
                SELECT req_posting_auths [1]
                FROM custom_json_ops
                WHERE op_id = 'community'
                    AND (op_json -> 0)::text = '"subscribe"'
                    AND block_num BETWEEN {block_range[0]} and {block_range[1]} 
            )AS subscribe_ops;
        """
        return query
    
    @classmethod
    def unsubscribe(cls, community, block_range=None):
        """
            :unsubscribe"  | {"community":"hive-152200"}
        """
        if block_range is None:
            latest = SystemStatus.get_latest_block()
            if not latest: return None # TODO: notify??
            block_range = [latest - 28800, latest]
        query = f"""
            SELECT *  
            FROM (
                SELECT req_posting_auths [1]
                FROM custom_json_ops
                WHERE op_id = 'community'
                    AND (op_json -> 0)::text = '"unsubscribe"'
                    AND block_num BETWEEN {block_range[0]} and {block_range[1]} 
            )AS unsubscribe_ops;
        """
        return query
    
    @classmethod
    def flag_post(cls, community=None, account=None, permlink=None, notes=None, block_range=None):
        """Populates query to retrieve `flagPost` ops"""
        if block_range is None:
            latest = SystemStatus.get_latest_block()
            if not latest: return None # TODO: notify??
            block_range = [latest - 28800, latest]
        query = f"""
            SELECT *  
            FROM (
                SELECT req_posting_auths [1],
                    op_json -> 1 -> 'account'::text,
                    op_json -> 1 -> 'permlink'::text,
                    op_json -> 1 -> 'notes'::text
                FROM custom_json_ops
                WHERE op_id = 'community'
                    AND (op_json -> 0)::text = '"flagPost"'
                    AND block_num BETWEEN {block_range[0]} and {block_range[1]} 
        """
        if community:
            query += f"""
            AND (op_json -> 1 -> 'community'):: text = '"{community}"'
            """
        if account:
            query += f"""
            AND (op_json -> 1 -> 'account'):: text = '"{account}"'
            """
        if permlink:
            query += f"""
            AND (op_json -> 1 -> 'permlink'):: text = '"{permlink}"'
            """
        if notes:
            query += f"""
            AND (op_json -> 1 -> 'notes'):: text = '"{notes}"'
            """
        query += ")AS flag_post_ops;"
        return query