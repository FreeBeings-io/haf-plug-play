import os

from haf_plug_play.server.system_status import SystemStatus

WDIR_PODPING = os.path.dirname(__file__)

class SearchQuery:

    pass

class StateQuery:

    @classmethod
    def get_podping_counts(cls, block_range=None, limit: int = 20):
        if block_range is None:
            latest = SystemStatus.get_latest_block()
            if not latest: return None # TODO: notify??
            block_range = [latest - 864000, latest] # default 30 days
        query = f"""
                    SELECT url, COUNT(url) as url_count
                    FROM podping.feed_updates
                    WHERE block_num BETWEEN {block_range[0]} AND {block_range[1]}
                    GROUP BY url
                    ORDER BY url_count DESC
                    LIMIT {limit};
        """
        return query

    @classmethod
    def get_podping_url_latest_feed_update(cls, url: str, limit: int = 5):
        query = f"""
            SELECT po.transaction_id, fu.block_num, fu.created, po.req_auths, po.req_posting_auths
            FROM podping.feed_updates fu
            JOIN podping.ops po ON po.id = fu.podping_id
            WHERE url = '{url}'
            ORDER BY fu.podping_id DESC
            LIMIT {limit};
        """
        return query
