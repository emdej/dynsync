#!/bin/bash

MAINDIR=$(readlink -f $(readlink -f $0 | xargs dirname)/..)
DYNSYNCDIR=${MAINDIR}/dynsync
TESTDIR_L=$(mktemp -d)
TESTDIR_R=$(mktemp -d)

set -e

cd ${DYNSYNCDIR}
python2.7 dynsync.py ${TESTDIR_L}/ localhost:${TESTDIR_R}/ --remote-username=${USER} --remote-python=$(which python) &
PID=$!

function cleanup
{
    rm -rf ${TESTDIR_L}
    rm -rf ${TESTDIR_R}
    kill -9 ${PID}
}

trap cleanup EXIT

function make_dirs
{
    for i in {1..10}
    do
        mkdir -p ${TESTDIR_L}/d${i}
    done
}

function make_files
{
    for i in {1..10}
    do
        echo "test" > ${TESTDIR_L}/f${i}
    done
}

function make_files_in_dirs
{
    for i in {1..10}
    do
        for j in {1..5}
        do
            echo "test" > ${TESTDIR_L}/d${i}/f${j}
        done
    done
}

function chmod_files
{
    chmod a+x ${TESTDIR_L}/d4/f3
}

function remote_add_files
{
    for i in {1..10}
    do
        echo "rf$i" > ${TESTDIR_R}/d5/rf${i}
    done
}

function remote_move_files
{
    mv ${TESTDIR_R}/d5/rf1 ${TESTDIR_R}/d6/rf_1
}

function remote_remove_dir
{
    rm -rf ${TESTDIR_R}/d7
}

function move_dirs
{
    mv ${TESTDIR_L}/d1 ${TESTDIR_L}/d_1
}

function move_files
{
    mv ${TESTDIR_L}/d2/f1 ${TESTDIR_L}/f_1
}

function remove_files
{
    rm ${TESTDIR_L}/d3/f1
}

function remove_dirs
{
    rm -rf ${TESTDIR_L}/d4
}

function remove_all
{
    rm -rf ${TESTDIR_L}/*
}

function verify
{
    ls -l ${TESTDIR_L}
    ls -l ${TESTDIR_R}
    echo "local:"
    tar --sort=name -cm -f - -C ${TESTDIR_L} . | tar -tv
    echo "remote:"
    tar --sort=name -cm -f - -C ${TESTDIR_R} . | tar -tv
    SL=$(tar --sort=name -cm -f - -C ${TESTDIR_L} . | sha256sum | cut -d' ' -f1)
    SR=$(tar --sort=name -cm -f - -C ${TESTDIR_R} . | sha256sum | cut -d' ' -f1)
    if [ "${SL}" == "${SR}" ]
    then
        echo "verification: OK"
        return 0
    else
        echo "verification: FAIL"
        return 1
    fi
}

sleep 1

rsync --delete -e 'ssh -o StrictHostKeyChecking=no' -avzP --temp-dir=/tmp ${TESTDIR_L}/ localhost:${TESTDIR_R}/

echo "initial verification"
verify

echo "make files"
make_files; sleep 2
verify

echo "make dirs"
make_dirs; sleep 2
verify

echo "make files in dirs"
make_files_in_dirs; sleep 2
verify

echo "move dirs"
move_dirs; sleep 2
verify

echo "move files"
move_files; sleep 2
verify

echo "chmod files"
chmod_files; sleep 2
verify

echo "remote add files"
remote_add_files; sleep 3
verify

echo "remote move files"
remote_move_files; sleep 3
verify

echo "remote remove dirs"
remote_remove_dir; sleep 3
verify

echo "remove files"
remove_files; sleep 2
verify

echo "remove dirs"
remove_dirs; sleep 2
verify

echo "remove all"
remove_all; sleep 2
verify
