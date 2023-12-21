 # Judge Model Source Type, Source Code or Executable Program
arg=$1
exe_str=$2
obj_str=$3
remote_str=$4

if [ -z $exe_str ]
then
  if [ ! -z $obj_str ]
  then
    echo "Compile Model Source Code {$obj_str}"
    cd $obj_str || exit
    if grep -q "CC = icc"
    then
      make CC = icc
    else
      make CC=gcc CFLAGS="-std=c99 -I ."
    fi
    if [ $? -ne 0 ]
    then
      echo "Compile failed"
      exit 1
    fi
    echo "Running Executable Program $obj_str"
    cd ..
    ./$obj_str/$obj_str $arg >./$obj_str.log || /bin/bash ./$exe_str $arg >./$exe_str.log
  else
    echo "Running Remote Executable Program $remote_str"
    cd
    ./$remote_str >./$remote_str.log  || /bin/bash ./$exe_str $arg >./$exe_str.log
  fi
else
  echo "Running Executable Program $exe_str"
  ./$exe_str $arg >./$exe_str.log  || /bin/bash ./$exe_str $arg >./$exe_str.log
fi

echo "Now exiting..."