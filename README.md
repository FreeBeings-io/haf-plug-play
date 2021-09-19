# Hive Plug & Play (HAF) [ALPHA]

**Customizable streaming and parsing microservice for custom_json ops on Hive.**

*This project is under heavy development and is not stable enough to run in production.*

## Development

### Dependencies:
- Python 3.6 required (with pip,  libpq-dev, and Psycopg2)
- PostgreSQL 10+<br/>

**Install depencencies**<br/>
- Python3 and PostgreSQL : 
```
sudo apt install python3 python3-pip libpq-dev python3-psycopg2 postgresql
```


### Configure Hive Plug & Play (HAF)
  1. Hive Plug & Play requires a `config.ini` file to exist in either:
    - Default file location of `/etc/hive-plug-play` 
    - Or use any custom folder by setting an environment variable: `export PLUG_PLAY_HOME=~/.config/hive-plug-play`.
  2. Build the file directory:
  ```
  mkdir -p ~/.config/hive-plug-play
  ```
  3. Create the `config.ini` file 
    - Any text editor should do:
  ```
  db_username=postgres
  db_password=password
  server_host=127.0.0.1
  server_port=5432
  ssl_cert=
  ssl_key=
  ```


### Installation:

  ```
  cd ~/
  git clone git@github.com:imwatsi/haf-plug-play.git
  cd ~/hive-plug-play
  pip3 install -e .
  ```

### Run:

*From command:*

`haf_plug_play`

*Or from dir:*

- `cd hive_plug_play`
- `python3 run_plug_play.py`
