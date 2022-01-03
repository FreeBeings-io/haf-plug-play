import os

from haf_plug_play.server.system_status import SystemStatus

WDIR_POLLS = os.path.dirname(__file__)

class SearchQuery:

    @classmethod
    def poll_ops(cls, op_type=None, block_range=None):
        if block_range is None:
            latest = SystemStatus.get_latest_block()
            if not latest: return None # TODO: notify??
            block_range = [latest - 28800, latest]
        query = f"""
                    SELECT transaction_id, req_posting_auths, op_type, op_payload
                    FROM hpp_polls_ops
                    WHERE block_num BETWEEN {block_range[0]} AND {block_range[1]}
        """
        if op_type:
            query += f"AND op_type = '{op_type}';"

        return query


class StateQuery:

    @classmethod
    def get_polls_active(cls, tag=None):
        query = f"""
            SELECT author, permlink, question,
                answers, expires, tag
            FROM hpp_polls_content
            WHERE expires >= NOW() AT TIME ZONE 'utc'
        """
        if tag:
            query += f" AND tag = '{tag}';"
        return query

    @classmethod
    def get_poll(cls, author, permlink):
        query = f"""
            SELECT author, permlink, question
                answers, expires, tag
            FROM hpp_polls_content
            WHERE author = '{author}' AND permlink = '{permlink}';
        """
        return query

    @classmethod
    def get_poll_votes_summary(cls, author, permlink):
        query = f"""
            SELECT t_content.answers[t_votes.answer] AS parsed_answer, COUNT(DISTINCT t_votes.account)
            FROM hpp_polls_content t_content 
            JOIN hpp_polls_votes t_votes ON t_content.author = t_votes.author
                AND t_content.permlink = t_votes.permlink
            WHERE t_content.author = '{author}'
                AND t_content.permlink = '{permlink}'
                AND t_votes.created <= COALESCE(
                    t_content.expires, t_content.created - INTERVAL '7 DAYS')
            GROUP BY parsed_answer;
        """
        return query

    @classmethod
    def get_poll_votes(cls, author, permlink):
        query = f"""
            SELECT t_votes.account, t_content.answers[t_votes.answer] AS answer
            FROM hpp_polls_content t_content 
            JOIN hpp_polls_votes t_votes ON t_content.author = t_votes.author AND t_content.permlink = t_votes.permlink
            WHERE t_content.author = '{author}' AND t_content.permlink = '{permlink}';
        """
        return query