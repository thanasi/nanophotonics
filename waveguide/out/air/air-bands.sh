#!/bin/sh

if [ ! -d ./bands/multi-k ]
then
	mkdir bands/multi-k
fi

cd bands/multi-k/

ctlfile="../../air-bands.ctl"

# calculate fluxes and ldos in the unit cell
meep flux-mode?=true $ctlfile > fluxmode.out
grep ldos0: fluxmode.out > ldos.out
grep flux1: fluxmode.out > fluxes.out

# calculate band structure in unit cell
meep $ctlfile > bands.out
grep freqs: bands.out > fre.out
grep freqs-im: bands.out > fim.out

# equalize row length
python ../../../../cleanCSV.py fre.out
python ../../../../cleanCSV.py fim.out

# rename epsilon file
mv *-eps-000000.00.h5 eps.h5

# separate out harminv files
for i in `seq 1 $(wc -l < fre.out)`
do
	printf -v j "%02d" $(($i-1))
	k=$(($i-1))
	grep harminv$k: bands.out > harminv$j.out
done

cd ../..