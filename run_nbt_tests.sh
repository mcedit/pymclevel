rm _nbt.pyd
sh run_tests.sh test/nbt_test.py
python setup_nbt.py build_ext --inplace
sh run_tests.sh test/nbt_test.py

