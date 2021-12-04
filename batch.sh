configfile=$1

repetitions=$(grep 'repetitions:' $configfile | cut -d: -f2 | tr -d ' ' | tr -d '"')
testcase=$(grep 'testcase:' $configfile | cut -d: -f2 | tr -d ' ' | tr -d '"')

DATE_WITH_TIME=`date "+%Y-%m-%d_%H-%M-%S"`
resultsdir=$PWD/tmp_benchmarks_results/$DATE_WITH_TIME-$testcase/results
mkdir -p $resultsdir

cp $configfile $resultsdir/config.yaml

for (( c=1; c<=$repetitions; c++ ))
do
		
	RUNDIR=$resultsdir/$c

	echo "==== BATCHRUNNER: Starting repetition $c in $RUNDIR ==="

	salloc --constraint mc \
		-A ich004m \
		--time=200 \
		--nodes 33 \
		--ntasks 66 \
		--cpus-per-task 36 \
		--hint=multithread \
 		job.sh $configfile $RUNDIR
done
