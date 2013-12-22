The Larch
=========
Quick prototyping of VR (games | apps | "experiences") in python.

![alt tag](http://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/M%C3%A9l%C3%A8ze_en_Automne.JPG/180px-M%C3%A9l%C3%A8ze_en_Automne.JPG)

*Status:* _Linux only. WIP. Not of much use to anyone right now.._

Setup
-----
1. Setup a virtualenv and activate it. (pypy recommended)
```
$> virtualenv -p PATH_TO_PYTHON ENV_DIR
... lots of output ...
$> source ENV_DIR/bin/activate
```

2. OPTIONAL: copy OculusSDK into this dir to build deps.

3. run ```./get_stuff.sh``` to get dependencies and build libraries.
```
$> ./get_stuff.sh
```

Running
-------

### Run cube demo:
```
python larch --game cube
```
With the Rift:
```
python larch --game cube
```

### Get help:
```
python larch
```

