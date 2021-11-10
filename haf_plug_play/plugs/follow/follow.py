import os

from haf_plug_play.server.system_status import SystemStatus

WDIR_FOLLOW = os.path.dirname(__file__)

class SearchQuery:

    @classmethod
    def follow(cls, follower_account=None, followed_account=None, block_range=None):
        """
            "follow" | {"follower":"idwritershive","following":"olgavita","what":["blog"]}
        """
        if block_range is None:
            latest = SystemStatus.get_latest_block()
            if not latest: return None # TODO: notify??
            block_range = [latest - 28800, latest]
        query = f"""
            SELECT *  
            FROM (
                SELECT
                    req_posting_auths,
                    op_json::json
                FROM plug_play_ops
                    WHERE block_num BETWEEN {block_range[0]} and {block_range[1]}
        """
            #WHERE op_id = '"follow"'
        #AND (op_json::json -> 0)::text = '"follow"'
        if follower_account:
            query += f"""
            AND (op_json::json -> 1 -> 'follower'):: text = '"{follower_account}"'
            """
        if followed_account:
            query += f"""
            AND (op_json::json -> 1 -> 'following'):: text = '"{followed_account}"'
            """
        query += ")AS follow_ops;"

        return query

    

class StateQuery:

    @classmethod
    def get_account_followers(cls, account):
        query = f"""
            SELECT account, what
                FROM hpp_follow_state
                WHERE following = '{account}';
        """
        return query
