#!/bin/bash

checkret () {
    if [ ! $? -eq 0 ]; then
        echo "==== Something went wrong ===="
        exit
    fi
}


if [ ! -d python-glm ] && [ ! -f build_lock ]; then
    hg clone https://bitbucket.org/duangle/python-glm
    cd python-glm
    python setup.py develop
    cd ..
elif [ ! -f build_lock ]; then
    cd python-glm
    hg pull -u
    python setup.py develop
    cd ..
fi

build_ovr () {
    cd python-ovr/ovr-src/

    ./ConfigurePermissionsAndPackages.sh
    checkret

    make -j
    checkret

    cd ..

    python setup.py develop
    checkret

    cd ..

    touch build_lock
}

if [ -d OculusSDK ] && [ ! -f build_lock ]; then
    if [ ! -d python-ovr ]; then
        hg clone https://bitbucket.org/duangle/python-ovr
    else
        cd python-ovr
        hg pull -u
        cd ..
    fi

    cd python-ovr
    python setup.py develop
    cd ..
    echo "==== Copying OculusSDK dir to python-ovr dir and building... ===="
    cp -rf ./OculusSDK ./python-ovr/ovr-src

    build_ovr

    touch build_lock
fi

if [ -f build_lock ]; then
    echo "== To fetch and rebuild: $> rm build_lock"
fi

echo "==== Hopefully everything went OK. ==== "

