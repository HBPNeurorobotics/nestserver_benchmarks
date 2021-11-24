config=$1

repetitions=$(grep 'repetitions:' $config | cut -d: -f2 | tr -d ' ' | tr -d '"')
DATE_WITH_TIME=`date "+%Y-%m-%d_%H-%M-%S"`

for (( c=1; c<=$repetitions; c++ ))
do
		
	RUNDIR=$PWD/tmp_benchmarks_results/$DATE_WITH_TIME/$c

	echo "==== BATCHRUNNER: Starting repetition $c in $RUNDIR ==="

	salloc --constraint mc \
		-A ich004m \
		--time=200 \
		--nodes 33 \
		--ntasks 66 \
		--cpus-per-task 36 \
		--hint=multithread \
 		job.sh $config $RUNDIR
done
