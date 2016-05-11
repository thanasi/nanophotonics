#!/bin/sh

echo "- straight-wvg"

if [ ! -d ./radiation ]
then
	mkdir ./radiation
fi

cd ./radiation

ctlfile="../straight-wvg.ctl"

meep $ctlfile > radiation.out
grep ldos0: radiation.out > ldos.out
grep flux1: radiation.out > fluxes.out

mv *-eps-*.h5 eps.h5

cd ..

echo "+ straight-wvg"