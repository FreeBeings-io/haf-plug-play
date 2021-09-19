import json

HIVE_NODES = [
    "https://api.hive.blog", "https://anyx.io",
    "https://hive.roelandp.nl", "https://rpc.ausbit.dev", "https://api.pharesim.me",
    "https://api.deathwing.me", "https://hive-api.arcange.eu", "https://hived.emre.sh",
    "https://api.openhive.network", "https://hived.privex.io", "https://rpc.ecency.com",
    "https://api.hivekings.com"
]

UTC_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"

def check_required_keys(required, provided_keys, op_context):
    missing = []
    for k in required:
        if k not in provided_keys:
            missing.append(k)
    assert len(missing) == 0, f"missing keys for {op_context}: {missing}"

def check_allowed_keys(allowed, provided_keys, op_context):
    unsupported = []
    for k in provided_keys:
        if k not in allowed:
            unsupported.append(k)
    assert len(unsupported) == 0, f"unsupported keys provided for {op_context}: {unsupported}"

def get_cleaned_dict(og_values, keys, keep=False):
    result = {}
    for k in og_values:
        if (k in keys) == keep:
            result[k] = og_values[k]
    return result