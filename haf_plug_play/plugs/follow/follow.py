from haf_plug_play.server.system_status import SystemStatus

class SearchOps:

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
    
    @classmethod
    def reblog(cls, reblog_account=None, blog_author=None, blog_permlink=None, block_range=None):
        """
            "reblog" | {
                "account":"nataly2317",
                "author":"coininstant",
                "permlink":"it-s-time-to-buy-sats-satoshin-token-on-uniswap-to-the-moon"
            }
        """
        if block_range is None:
            latest = SystemStatus.get_latest_block()
            if not latest: return None # TODO: notify??
            block_range = [latest - 28800, latest]
        query = f"""
            SELECT *  
            FROM (
                SELECT req_posting_auths,
                    op_json::json -> 'account'::text,
                    op_json::json -> 'author'::text,
                    op_json::json -> 'permlink'::text
                FROM plug_play_ops
                WHERE op_id = 'follow'
                    AND block_num BETWEEN {block_range[0]} and {block_range[1]}
        """
        if reblog_account:
            query += f"""
            AND (op_json::json -> 1 -> 'account'):: text = '"{reblog_account}"'
            """
        if blog_author:
            query += f"""
            AND (op_json::json -> 1 -> 'author'):: text = '"{blog_author}"'
            """
        if blog_permlink:
            query += f"""
            AND (op_json::json -> 1 -> 'blog_permlink'):: text = '"{blog_permlink}"'
            """
        query += ")AS reblog_ops;"

        return query

class StateOps:

    @classmethod
    def followers(cls, account):
        query = f"""
            SELECT account, what
                FROM hpp_follow_state
                WHERE following = {account};
        """
        return query