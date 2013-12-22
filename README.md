Rift Prototypes
===============

### Linux only.

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

