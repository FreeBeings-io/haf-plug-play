"""Metadata for the FastAPI instance"""

# Main

TITLE = "Hive Plug & Play (API)"

DESCRIPTION = """
    **A turnkey tool to extract and process custom data sets from the Hive blockchain and create APIs for them.**

    Each enabled "plug" has it's own root endpoint path, under `/api` and sub-endpoints under it.
"""

VERSION = "1.0"

CONTACT = {
    "name": "FreeBeings.io",
    "email": "developers@freebeings.io",
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
        "name": "podping",
        "description": "Podping is a distributed notification system for new podcast episodes based on the Hive blockchain",
    }
]