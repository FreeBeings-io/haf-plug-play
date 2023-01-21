# Hive Plug & Play (HAF) [BETA]

**A turnkey tool to extract and process custom data sets from the Hive blockchain and create APIs for them.**

*Plug & Play uses the Hive Application Framework.*

---

## Available Plugs

Available plugs that can be run:

- [Podping](docs/plugs/podping.md)
- [Delegations](docs/plugs/deleg.md)

---

## WIP Plugs

Plugs still under development:

- Hive Engine

---

## Production Deployment

A production environment to succesfully run Plug & Play requires:

### A configured HAF server populating a HAF database

- Install HAF on a server: https://gitlab.syncad.com/hive/haf
- Setup the HAF database according to instructions on the repo above
- The HAF database can be on the same server as `hived` or on another server
- Set appropriate psql-filters if needed: [HAF PSQL Filtering Examples](https://gitlab.syncad.com/hive/haf/-/tree/develop/tests/integration/replay/patterns)
- Run `hived` and allow it to run in live mode (synced to `head_block`)

### Build from Docker

Simply build from the Dockerfile and run the container with the following variables passed:

```
DB_HOST=ip_address_of_haf_db_server
DB_NAME=your_haf_db_name
DB_USERNAME=username
DB_PASSWORD=password
SERVER_HOST=127.0.0.1
SERVER_PORT=8080
SCHEMA=hpp
PLUGS=podping
RESET=false
```

**Example**

Create `.env` file with the above variables in the root folder of the repo and run:

```
docker build -t hpp-podping .
docker run -d -p 8080:8080 --env-file .env hpp-podping
```

The configuration above runs a Plug & Play service, with only the `podping` plug enabled. To enable multiple plugs, use something like this: `PLUGS=podping,hive_engine`.

To reset the database on startup, set the `RESET` variable to true.

---

## Development Setup

### Install HAF and PostgreSQL Debugger

- Install HAF: https://gitlab.syncad.com/hive/haf

- Install the PostgreSQL Debugger:
  - `sudo apt install postgresql-12-pldebugger`
  - then, in PSQL Tool, run `CREATE EXTENSION pldbgapi;`

- Install PgAdmin

### Install Plug & Play dependencies

```
sudo apt install \
    python3 \
    python3-dev \
    python3-pip \
    postgresql \
    libpq-dev \
    libssl-dev \
    libreadline-dev \
    libpqxx-dev \
    postgresql-server-dev-14

```

### Install Plug & Play

```
git clone https://github.com/imwatsi/haf-plug-play.git
cd haf-plug-play
pip3 install -e .
```

