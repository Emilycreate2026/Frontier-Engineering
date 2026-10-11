#!/bin/bash
set -euo pipefail
cd /solution
g++ -std=c++14 -O3 -DNDEBUG -Isrc -Isrc/include src/roadef2018/lib/main.cpp src/roadef2018/lib/instance.cpp src/roadef2018/lib/solution.cpp src/roadef2018/ub_*/*.cpp -lboost_program_options -pthread -o solver
python3 solve.py
