#!/bin/bash

runtest(){
  python compiler.py "$1" > _tmp.s
  gcc -o _tmp _tmp.s
  output=$(./_tmp)
  if [ "$output" != "$2" ]; then
    echo "$1: $2 expected, but got $output"
    exit 1
  fi
  rm _tmp _tmp.s
}

runtest test/a.spl2 6
runtest test/b.spl2 84104212
runtest test/c.spl2 111123777123111123
runtest test/array.spl2 123777456777123777
runtest test/if.spl2 12123456789
runtest test/func.spl2 777333999333777
runtest test/rec.spl2 120
runtest test/tailcall.spl2 500000500000

echo OK

