#!/bin/sh

cd air && sh air-modes-iter-k.sh
cd ..

cd straight && sh straight-modes-iter-k.sh 
cd ..

cd holes && sh holes-modes-iter-k.sh
cd ..

cd bumps && sh bumps-modes-iter-k.sh
cd ..
