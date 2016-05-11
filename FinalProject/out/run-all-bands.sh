#!/bin/sh

cd air && sh air-bands.sh
cd ..

cd straight && sh straight-bands.sh 
cd ..

cd holes && sh holes-bands.sh
cd ..

cd bumps && sh bumps-bands.sh
cd ..
