# Hive Plug & Play (HAF) [ALPHA]

**Customizable streaming and parsing microservice for custom_json ops on Hive.**

*This project is under heavy development and is not stable enough to run in production.*

## HAF

Plug & Play uses the Hive Application Framework to retrieve `custom_json` ops from Hive blocks.

For an overview of how HAF works read this post: https://hive.blog/hive-139531/@mickiewicz/what-is-haf


## Documentation

Documentation can be found here:

- [API Documentation](docs/api/api.md)

## Development


### Install dependencies


```
sudo apt install python3 \
    python3-pip \
    postgresql \
    libpq-dev \
    libssl-dev \
    libreadline-dev \
    libpqxx-dev \
    postgresql-server-dev-12 \
    postgresql-server-dev-all
```

### Install HAF and hived

- Clone the HAF repository: https://gitlab.syncad.com/hive/haf
- `git submodule update --init --recursive`
- Create a build directory: `mkdir build`
- `cd build`
- `cmake -DCMAKE_BUILD_TYPE=Release ..`
- `make`
- `make install`
- `cd hive/programs/hived/`
- Create data dir for hived: `./hived -d data --dump-config`


### Setup PostgreSQL

Once you have your PostgreSQL installation, setup the username and password access. For example:

```
sudo -u postgres psql template1
ALTER USER postgres with encrypted password 'your_password';
\q          #quit psql
sudo systemctl restart postgresql.service
```
Edit the file `/etc/postgresql/12/main/pg_hba.conf` to use MD5 authentication: `local   all         postgres                          md5`

After that, create the `haf` database:

```
psql -U postgres
CREATE DATABASE haf;
```
### Connect to the database and create the extension

'''
\c haf
CREATE EXTENSION hive_fork_manager;
'''

### Give PostgreSQL permissions

```
CREATE ROLE hived LOGIN PASSWORD 'hivedpass' INHERIT IN ROLE hived_group;
CREATE ROLE application LOGIN PASSWORD 'applicationpass' INHERIT IN ROLE hive_applications_group;
```


### Add sql_serializer params to hived config

```
nano data/config.ini

# ADD THE FOLLOWING:

plugin = sql_serializer
psql-url = dbname=haf user=postgres password=your_password hostaddr=127.0.0.1 port=5432
```

### Download block log for replay

```
cd haf/build/hive/programs/hived/data
mkdir -p blockchain
wget -O blockchain/block_log https://gtg.openhive.network/get/blockchain/block_log
```

### Install HAF Plug & Play

```
git clone https://github.com/imwatsi/haf-plug-play.git
cd haf-plug-play
pip3 install -e .
```

### Run hived and sync to a specific block height

```
cd haf/build/hive/programs/hived
./hived -d data --replay-blockchain --stop-replay-at-block 45000000 --exit-after-replay
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
  db_password=your_password
  server_host=127.0.0.1
  server_port=8080
  ssl_cert=
  ssl_key=
  ```

  This config works well with an Nginx reverse-proxy server setup to route traffic to the HAF Plug & Play server.

### Run HAF Plug & Play

Run HAF Plug & Play: `haf_plug_play`

### Check HAF Plug & Play sync status

- Visiting https://plug-play-beta.imwatsi.com/ or
- Making this call on the API - https://github.com/imwatsi/haf-plug-play/blob/master/docs/api/standard_endpoints.md#get_sync_status
