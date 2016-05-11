#!/bin/sh

cd air && sh air-rad.sh &
cd straight && sh straight-rad.sh &
cd holes && sh holes-rad.sh &
cd bumps && sh bumps-rad.sh &

wait