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
    make CC=gcc CFLAGS="-std=c99 -I ."
    if [ $? -ne 0 ]
    then
      echo "Compile failed"
      exit 1
    fi
    echo "Running Executable Program $obj_str"
    cd ..
    ./$obj_str/$obj_str $arg 1>./$obj_str.log 2>./$obj_str.err || /bin/bash ./$exe_str $arg 1>./$exe_str.log 2>./$exe_str.err
  else
    echo "Running Remote Executable Program $remote_str"
    cd
    ./$remote_str 1>./$remote_str.log 2>./$remote_str.err || /bin/bash ./$exe_str $arg 1>./$exe_str.log 2>./$exe_str.err
  fi
else
  echo "Running Executable Program $exe_str"
  ./$exe_str $arg 1>./$exe_str.log 2>./$exe_str.err || /bin/bash ./$exe_str $arg 1>./$exe_str.log 2>./$exe_str.err
fi

echo "Now exiting..."