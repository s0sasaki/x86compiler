#!/bin/bash

runtest(){
  python compiler.py "$1" 
  gcc -o a.out a.s
  output=$(./a.out)
  if [ "$output" != "$2" ]; then
    echo "$1: $2 expected, but got $output"
    exit 1
  fi
  rm a.out a.s
}

runtest test/a.spl 6
runtest test/b.spl 84104212
runtest test/c.spl 111123777123111123
runtest test/array.spl 123777456777123777
runtest test/if.spl 12123456789
runtest test/func.spl 777333999333777
runtest test/rec.spl 120
#runtest test/tailcall.spl 500000500000

echo OK

