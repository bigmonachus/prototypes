#!/bin/bash

checkret () {
    if [ ! $? -eq 0 ]; then
        echo "==== Something went wrong ===="
        exit
    fi
}


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

if [ ! -d python-glm ]; then
    hg clone https://bitbucket.org/duangle/python-glm
else
    cd python-glm
    hg pull -u
    cd ..
fi
cd python-glm
python setup.py develop
cd ..

if [ -d OculusSDK ] && [ ! -f oculus_lock ]; then
    echo "==== Copying OculusSDK dir to python-ovr dir and building... ===="
    cp -rf ./OculusSDK ./python-ovr/ovr-src
    cd python-ovr/ovr-src/

    ./ConfigurePermissionsAndPackages.sh
    checkret

    make -j
    checkret

    cd ..

    python setup.py develop
    checkret

    cd ..

    touch oculus_lock
fi

if [ -f oculus_lock ]; then
    echo "== To rebuild oculus: $> rm oculus_lock"
fi

echo "==== Hopefully everything went OK. ==== "

