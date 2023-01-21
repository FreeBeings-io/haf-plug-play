# Podping

**STATUS: Live**

This plug syncs data for Podping, storing all ops under the following `custom_json` IDs:

- `podping`
- `pp_video_update`
- `pp_podcast_live`
- `pp_podcast_update`

### Tables

You can view the schema in the [tables.sql](/haf_plug_play/plugs/podping/tables.sql) file. The `podping.ops` stores all the raw ops and `podping.updates` table stores the processed Podping updates.

### Functions

You can view the functions in the [functions.sql](/haf_plug_play/plugs/podping/functions.sql) file.

### Endpoints

Endpoints are defined under the folder `../server/plug_endpoints/podping.py`, where FastAPI is used in combination with PostgreSQL queries to extract required data from the `podping` schema. View it here [popding.py](/haf_plug_play/server/plug_endpoints/podping.py).

It has its own `APIRouter`, which is imported by the main server script.