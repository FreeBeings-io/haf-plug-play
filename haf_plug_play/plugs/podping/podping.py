import os

from haf_plug_play.server.system_status import SystemStatus

WDIR_PODPING = os.path.dirname(__file__)

class SearchQuery:

    pass

class StateQuery:

    @classmethod
    def get_podping_counts(cls, block_range=None):
        if block_range is None:
            latest = SystemStatus.get_latest_block()
            if not latest: return None # TODO: notify??
            block_range = [latest - 864000, latest] # default 30 days
        query = f"""
                    SELECT url, COUNT(url) as url_count
                    FROM hpp_podping_feed_updates
                    WHERE block_num BETWEEN {block_range[0]} AND {block_range[1]}
                    GROUP BY url
                    ORDER BY url_count DESC
                    LIMIT 20;
        """
        return query

    @classmethod
    def get_podping_url_latest_feed_update(cls, url):
        query = f"""
            SELECT block_num, created
            FROM public.hpp_podping_feed_updates
            WHERE url = '{url}'
            ORDER BY pp_podping_opid
            LIMIT 1;
        """
        return query
