# # compile code #
# rm -r build
# mkdir build
# cd build
# cmake .. -DSCIP_DIR=/Users/lvscavuzzomont/opt/scipoptsuite-8.0.0
# make
# cd ..

# ./build/probe benchmarks/nn_verification/train/test_53.proto.lp settingsfile.set

for i in benchmarks/nn_verification/train/*.lp;
do
  ./build/probe $i settingsfile.set
done