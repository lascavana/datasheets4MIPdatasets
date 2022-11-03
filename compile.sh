# compile code #
rm -r build
mkdir build
cd build
cmake .. -DSCIP_DIR=/Users/lvscavuzzomont/opt/scipoptsuite-8.0.0
make
cd ..

counter=0
for i in benchmarks/nn_verification/*.lp;
do
  if [[ "$counter" == '20' ]]
  then
    break
  fi
  ((counter++))
  echo $counter
  ./build/probe $i settingsfile.set
done