#!/bin/bash

# stop current process
pkill -SIGINT "run_plug_play"
sleep 10
pkill -SIGKILL "run_plug_play"

# run SQL reset script

# restart Plug & Play