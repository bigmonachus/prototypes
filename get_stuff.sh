#!/bin/bash

checkret () {
    if [ ! $? -eq 0 ]; then
        echo "==== Something went wrong ===="
        exit
    fi
}


if [ ! -d python-ovr ]; then
    hg clone https://bitbucket.org/duangle/python-ovr
fi

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

echo "==== Hopefully everything went OK. ==== "

