import os

from haf_plug_play.server.system_status import SystemStatus

WDIR_REBLOG = os.path.dirname(__file__)

class SearchOps:
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
                    account,
                    author,
                    permlink
                FROM hpp_reblog
                WHERE block_num BETWEEN {block_range[0]} and {block_range[1]}
        """
        if reblog_account:
            query += f"""
            AND account = '{reblog_account}'
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

class StateQuery:

    @classmethod
    def get_account_reblogs(cls, account):
        pass