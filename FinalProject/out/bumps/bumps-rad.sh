#!/bin/sh

echo "- bumps-wvg"

if [ ! -d ./radiation ]
then
	mkdir ./radiation
fi

cd ./radiation

ctlfile="../bumps-wvg.ctl"

meep $ctlfile > radiation.out
grep ldos0: radiation.out > ldos.out
grep flux1: radiation.out > fluxes.out

mv *-eps-*.h5 eps.h5

cd ..

echo "+ bumps-wvg"