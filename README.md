# Hive Plug & Play (HAF) [BETA]

**A turnkey tool to extract and process custom data sets from the Hive blockchain and create APIs for them.**

*Plug & Play uses the Hive Application Framework.*

## Documentation

Documentation can be found here:

- [API Documentation](https://plug-play.imwatsi.com/docs)

## Development

### Install PostgreSQL Debugger

`sudo apt install postgresql-12-pldebugger`

Then, in PSQL Tool, run `CREATE EXTENSION pldbgapi;`


### Install dependencies


```
# HAF and Plug & Play

sudo apt install \
    python3 \
    python3-dev \
    python3-pip \
    postgresql \
    libpq-dev \
    libssl-dev \
    libreadline-dev \
    libpqxx-dev \
    postgresql-server-dev-12 \
    postgresql-server-dev-all

# hived packages

sudo apt-get install \
    autoconf \
    automake \
    cmake \
    g++ \
    git \
    zlib1g-dev \
    libbz2-dev \
    libsnappy-dev \
    libssl-dev \
    libtool \
    make \
    pkg-config \
    doxygen \
    libncurses5-dev \
    libreadline-dev \
    perl \
    python3 \
    python3-jinja2

# Boost packages (hived)

sudo apt-get install \
    libboost-chrono-dev \
    libboost-context-dev \
    libboost-coroutine-dev \
    libboost-date-time-dev \
    libboost-filesystem-dev \
    libboost-iostreams-dev \
    libboost-locale-dev \
    libboost-program-options-dev \
    libboost-serialization-dev \
    libboost-system-dev \
    libboost-test-dev \
    libboost-thread-dev

```

### Install HAF and hived

- Clone the HAF repository: https://gitlab.syncad.com/hive/haf
- `cd haf`
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

```
\c haf
CREATE EXTENSION hive_fork_manager CASCADE;
```

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

Visit https://plug-play.imwatsi.com/docs#/system/root_api_get or
