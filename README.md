# Hive Plug & Play (HAF) [BETA]

**A turnkey tool to extract and process custom data sets from the Hive blockchain and create APIs for them.**

*Plug & Play uses the Hive Application Framework.*

## Documentation

Documentation can be found here:

- [Podping API Documentation](https://podping.hpp.freebeings.io)

## Production Setup

A production environment to succesfully run Plug & Play requires:

### A configured HAF server populating a HAF database

- Install HAF on a server: https://gitlab.syncad.com/hive/haf
- The HAF database can be on the same server as `hived` or on another server
- Set appropriate psql-filters if needed: [HAF PSQL Filtering Examples](https://gitlab.syncad.com/hive/haf/-/tree/develop/tests/integration/replay/patterns)
- Run `hived` and allow it to run in live mode (synced to the `head_block` block)

### Plug & Play installed

- Clone the repository
- Install: `pip3 install -e .` 
- Create a config file, refer to the [sample_config](/sample_config.ini) file
- Set the config directory: for example `export PLUG_PLAY_HOME=/home/ubuntu/.config/hpp/config.ini`
- Enable the plugs you want to support by setting the `enabled` key to True in the plug's `defs.json` file. See the [Podping defs.json](/haf_plug_play/plugs/podping/defs.json) for example.
- Run Plug & Play: `haf_plug_play`

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

### Configure Hive Plug & Play (HAF)

Hive Plug & Play requires a `config.ini` file to exist in either:
  - Default file location of `/etc/hive-plug-play` 
  - Or use any custom folder by setting an environment variable: `export PLUG_PLAY_HOME=~/.config/hive-plug-play`.

To create a config file, refer to the [sample_config](/sample_config.ini) file.


### Run HAF Plug & Play

To run Plug & Play, use either:

- `haf_plug_play`
- or `python3 run_play_play.py`
