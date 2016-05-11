#!/bin/sh

echo "- bumps-modes-iter-k"

process_bands(){
	if [ ! -d ./bands/k$1 ]
	then
		mkdir bands/k$1
		cd bands/k$1
		meep k0=$1 ../../bumps-single-k.ctl > bands.out
		grep flux1: bands.out > fluxes.out
		grep harminv0: bands.out > harminv0.out

		cd ../..
		echo "  bumps: finished k0=$1"
	fi
}

# need to export function for child processes to be able to use
export -f process_bands

# run the function through xargs so that I can control the number of parallel processes used
seq 0 0.01 0.5 | xargs -I {} -P 4 bash -c "process_bands {}"
process_bands 0.5

wait

echo "+ bumps-modes-iter-k"
