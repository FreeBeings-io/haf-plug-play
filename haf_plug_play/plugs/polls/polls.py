"""SQL queries for the polls protocol."""

import os

from haf_plug_play.server.system_status import SystemStatus

WDIR_POLLS = os.path.dirname(__file__)

class SearchQuery:
    """Search related queries."""

    @classmethod
    def poll_ops(cls, op_type=None, block_range=None):
        """Retrieve poll operations."""
        if block_range is None:
            latest = SystemStatus.get_latest_block()
            if not latest: return None # TODO: notify??
            block_range = [latest - 28800, latest]
        query = f"""
                    SELECT transaction_id, req_posting_auths, op_type, op_payload
                    FROM polls.ops
                    WHERE block_num BETWEEN {block_range[0]} AND {block_range[1]}
        """
        if op_type:
            query += f"AND op_type = '{op_type}';"

        return query


class StateQuery:
    """State related queries."""

    @classmethod
    def get_polls_active(cls, tag=None):
        """Retrieve active polls."""
        query = """
            SELECT author, permlink, question,
                answers, expires, tag, created
            FROM polls.polls_content
            WHERE expires >= NOW() AT TIME ZONE 'utc'
            AND deleted = false
        """
        if tag:
            query += f" AND tag = '{tag}';"
        return query

    @classmethod
    def get_poll(cls, author, permlink):
        """Retrieve an individual poll."""
        query = f"""
            SELECT author, permlink, question
                answers, expires, tag, created
            FROM hpp.polls_content
            WHERE author = '{author}' AND permlink = '{permlink}' AND deleted = false;
        """
        return query

    @classmethod
    def get_poll_votes_summary(cls, author, permlink):
        """Retrieve the summary of votes associated with a specific poll."""
        query = f"""
            SELECT t_content.answers[t_votes.answer] AS parsed_answer, COUNT(DISTINCT t_votes.account)
            FROM hpp.polls_content t_content 
            JOIN hpp.polls_votes t_votes ON t_content.author = t_votes.author
                AND t_content.permlink = t_votes.permlink
            WHERE t_content.author = '{author}'
                AND t_content.deleted = false
                AND t_content.permlink = '{permlink}'
                AND t_votes.created <= COALESCE(
                    t_content.expires, t_content.created - INTERVAL '7 DAYS')
            GROUP BY parsed_answer;
        """
        return query

    @classmethod
    def get_poll_votes(cls, author, permlink):
        """Retrieve all votes associated with a specific poll."""
        query = f"""
            SELECT t_votes.account, t_content.answers[t_votes.answer] AS answer
            FROM hpp.polls_content t_content 
            JOIN hpp.polls_votes t_votes ON t_content.author = t_votes.author AND t_content.permlink = t_votes.permlink
            WHERE t_content.author = '{author}' AND t_content.permlink = '{permlink}' AND t_content.deleted = false;
        """
        return query
    
    @classmethod
    def get_polls_user(cls, author, active=False, tag=None):
        """Retrieve polls that a specific user has created."""
        query = f"""
            SELECT permlink, question,
                answers, expires, tag, created
            FROM hpp.polls_content
            WHERE author = '{author}'
            AND deleted = false
        """
        if active is True:
            query += " AND expires >= NOW() AT TIME ZONE 'utc'"
        if tag:
            query += f" AND tag = '{tag}'"
        query += " ORDER BY created DESC;"
        return query
