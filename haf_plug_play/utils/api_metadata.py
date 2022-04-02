"""Metadata for the FastAPI instance"""

# Main

TITLE = "Hive Plug & Play (API)"

DESCRIPTION = """
    **A customizable layer 2 microservice that simplifies buidling custom_json centric dApps on the Hive blockchain.**

    Each "plug" has it's own root endpoint path, under `/api` and sub-endpoints under it.
"""

VERSION = "1.0"

CONTACT = {
    "name": "imwatsi",
    "url": "https://hive.blog/@imwatsi",
    "email": "imwatsi@outlook.com",
}

LICENSE = {
    "name": "MIT License"
}


# Tags for Plugs

TAGS_METADATA = [
    {
        "name": "system",
        "description": "System endpoints"
    },
    {
        "name": "polls",
        "description": "Endpoints for `polls`, a decentralized protocol for polls on the Hive blockchain",
        "externalDocs": {
            "description": "Broadcast Ops",
            "url": "https://github.com/imwatsi/haf-plug-play/blob/master/docs/protocols/polls.md"
        }
    },
    {
        "name": "podping",
        "description": "Podping is a distributed notification system for new podcast episodes based on the Hive blockchain",
    }
]