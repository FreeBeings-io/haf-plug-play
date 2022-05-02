#!/bin/bash

# stop current process
pkill -SIGINT "plug_play"
sleep 10
pkill -SIGKILL "plug_play"

# restart Plug & Play
haf_plug_play