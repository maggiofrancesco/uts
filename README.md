# UTS
## 'Urban Transport System': optimization system for DRT ##


The aim of this work is to realize an **evolutionary algorithm** for the optimization of **demand responsive transport**. 
The project is related to the Smart City field as an optimization system for the public urban transport.

## Requirements

Python 2.5+, Flask, googlemaps, numpy, psycopg2, python-pip, virtualenv

## Installation

First, clone this repository.

    $ git clone https://github.com/maggiofrancesco/uts.git


Create a virtualenv, and activate this: 

    $ virtualenv env 
    $ source env/bin/activate

After, install all necessary to run:

    $ pip install -r requirements.txt

Than, run the application:

    $ cd flask_server
	  $ python api.py

To see your application, access this url in your browser: 

	http://localhost:5000

Each layer has his configuration file: `config_db.cfg`, `config_evol.cfg`, `config_server.cfg`

