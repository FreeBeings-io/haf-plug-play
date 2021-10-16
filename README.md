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
apt-get install -y \
    libboost-chrono-dev \
    libboost-context-dev \
    libboost-coroutine-dev \
    libboost-date-time-dev \
    libboost-filesystem-dev \
    libboost-iostreams-dev \
    libboost-locale-dev \
    libboost-program-options-dev \
    libboost-serialization-dev \
    libboost-signals-dev \
    libboost-system-dev \
    libboost-test-dev \
    libboost-thread-dev

apt install python3 python3-pip postgresql libpq-dev apt install postgresql-server-dev-all
```

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

### Give PostgreSQL permissions

```
CREATE ROLE hived LOGIN PASSWORD 'hivedpass' INHERIT IN ROLE hived_group;
CREATE ROLE application LOGIN PASSWORD 'applicationpass' INHERIT IN ROLE hive_applications_group;
```
`

### Build hived and configure the node

```
git clone https://gitlab.syncad.com/hive/hive.git
pushd hive
git checkout develop
git submodule update --init --recursive
popd
mkdir build_haf_sql_serializer
pushd build_haf_sql_serializer
cmake -DCMAKE_BUILD_TYPE=Release ../hive
make -j${nproc}
pushd programs/hived
./hived -d data --dump-config
```

### Install the fork_manager


```
git clone https://gitlab.syncad.com/hive/psql_tools.git
cd psql_tools
cmake .
make extension.hive_fork_manager
make install
```

### Add sql_serializer to params to hived config

```
nano data/config.ini

# ADD THE FOLLOWING:

plugin = sql_serializer
psql-url = dbname=haf user=postgres password=your_password hostaddr=127.0.0.1 port=5432
```

### Install HAF Plug & Play

```
git clone https://github.com/imwatsi/haf-plug-play.git
cd haf-plug-play
pip3 install -e .
```

### Run the HAF Plug & Play setup script

```
cd haf_plug_play/database
python3 haf_sync.py
```

### Donwload block log for replay

```
cd build_haf_sql_serializer/programs/hived/data
mkdir -p blockchain
wget -O blockchain/block_log https://gtg.openhive.network/get/blockchain/block_log
```

### Run hived and sync to a specific block height

```
cd build_haf_sql_serializer/programs/hived
./hived -d data --replay-blockchain --stop-replay-at-block 5000000 --exit-after-replay
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
