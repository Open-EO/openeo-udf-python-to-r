VITO openEO backend image; build this docker container with
```
docker build . -t alma --build-arg SPARK_VERSION=3.2.0 --build-arg PYTHON_PACKAGE=python38-devel 
```

and run interactively with

```
docker run -ti alma
```

and then, on the shell prompt run the UDF test with

```
(cd openeo-udf-python-to-r; python3 test.py)
```
