#!/bin/sh

process_bands(){
	mkdir bands/k$1
	cd bands/k$1
	meep k0=$1 ../../test-bands.ctl > bands.out
	# grep ldos0: bands.out > ldos.out
	grep flux1: bands.out > fluxes.out
	# grep freqs: bands.out > fre.out
	# grep freqs-im: bands.out > fim.out
	grep harminv0: bands.out > harminv0.out

	# python ../../../../cleanCSV.py fre.out
	# python ../../../../cleanCSV.py fim.out

	cd ../..
	echo finished k0=$1
}

for k in `seq 0 0.025 0.5`
do
	if [ ! -d ./bands/k$k ]
	then
		process_bands $k &
	fi
done

wait
