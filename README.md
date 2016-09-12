# meal-stats-backend
## Installation
This contains the backend of meal stats that support the classificatio of the images and the nutritional information retrieval. In order to run the following dependencies must be installed:

This steps assume you install tensorflow with **anaconda 2** and it creates a specific enviroment for it (called tensorflow). This should work with pip but has not been tested though.

*Before installing from 2 onwards remeber to run `source activate tensorflow`.*

1. Tensorflow, the latest commit is working with version 0.10.0. See [this](https://www.tensorflow.org/versions/r0.10/get_started/os_setup.html).
2. werkzeug, see [this](https://anaconda.org/delicb/werkzeug).
3. jsonrpc,  see [this](https://anaconda.org/auto/json-rpc).
4. PIL, see [this](https://anaconda.org/anaconda/pil).
5. MongoDB see [this](https://docs.mongodb.com/manual/installation/).
6. pymongo, see [this](https://anaconda.org/anaconda/pymongo).



## Running the server

Running the server is straightforward, just run `init_server.py` inside the conda tensorflow enviroment (or equivalent). `init_server.py` has the following command line arguments that should be provided in order to get custom behavior:

1. `--PORT` port on which the server will listen (`8080` is the default value).
2. `--DATABASE_HOST` the host of where the database is listening (`localhost` is the default value).
3. `--DATABASE_PORT` the port of where the database is listening (`27017` is the default value).
4. `--DATABASE_NAME` the name of the mongodb database (`mealStatsdb` is the default value).

Typically the default values should work just fine if the server is in the same machine as the database.

*note*: If you want to run this from PyCharm the python interpreter should point to the anaconda enviroment, typically installed in: `$ANACONDA_PATH/envs/tensorflow`.

