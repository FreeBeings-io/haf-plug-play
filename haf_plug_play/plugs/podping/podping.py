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
                    FROM hpp.podping_feed_updates
                    WHERE block_num BETWEEN {block_range[0]} AND {block_range[1]}
                    GROUP BY url
                    ORDER BY url_count DESC
                    LIMIT {limit};
        """
        return query

    @classmethod
    def get_podping_url_latest_feed_update(cls, url: str, limit: int = 5):
        query = f"""
            SELECT po.transaction_id, fu.block_num, fu.created
            FROM hpp.podping_feed_updates fu
            JOIN hpp.podping_ops po ON po.pp_podping_opid = fu.pp_podping_opid
            WHERE url = '{url}'
            ORDER BY fu.pp_podping_opid DESC
            LIMIT {limit};
        """
        return query
