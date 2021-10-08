### Documentation
#### API
Up to date documentation of this api is provided via openapi specification. The documentation can be mounted inside a docker container running swagger UI with the followin commands:

```
docker run -p 8080:8080 -e SWAGGER_JSON=/openapi.json -v $PWD/docs/openapi.json:/openapi.json swaggerapi/swagger-ui
```

Browse to http://localhost:8080 to view the documentation

#### Client
A libary of wrapper functions is provided to ease the integration of connecting clients with the AirView api. This allows developers to produce feeds into the system without having to aquire a low level understanding of the api structure. See [airview client handler documentation](docs/airviewclient.md#class-clientairviewclientclienthandlerbackend) for details.

##### Usage
A how to guide is provided [here](docs/airviewclienthowto.md)

Examples of how to use the client can be found at [in the ccf connector](https://github.com/AirWalk-Digital/terraform-aws-airview-ccf/tree/main/lambda_code)


### Running debug server
```CREATE_DB=True``` Will perform initialisation against an empty database

```
cd ./app
FLASK_APP=./utils/debug.py FLASK_DEBUG=True DATABASE_URI=sqlite:///mydb.sqlite3 CREATE_DB=True flask run
```
The initialisation of the database with test data can also be done independently of the debug server:
```
DATABASE_URI=sqlite:////tmp/new.sqlite3 python -m data_loader.load_all
```

### Performing database migration
SQLAlchemy can automatically roll forward the database to match the api codebase
The development codebase can be used to initiate the tracking of schema changes
```
cd ./app/utils
FLASK_APP=./migrate.py DATABASE_URI=sqlite:///dev.sqlite3 flask db init
FLASK_APP=./migrate.py DATABASE_URI=sqlite:///dev.sqlite3 flask db migrate -m "My Message"
FLASK_APP=./migrate.py DATABASE_URI=sqlite:///dev.sqlite3 flask db upgrade
```
Then the app can be run in the debug server without creating the db first
```
FLASK_APP=./utils/debug.py FLASK_DEBUG=True DATABASE_URI=sqlite:///dev.sqlite3 flask run
```
The same schema tracking can then be used to roll forward a prod/uat/etc instance to the same version
```
FLASK_APP=./migrate.py DATABASE_URI=sqlite:///prod.sqlite3 flask db upgrade
```

### Postgres as a db backend
SQLite is ok for dev, but for a more representative environment postgres should be used

```
docker run --name some-postgres -e POSTGRES_PASSWORD=password -d -p 5432:5432 postgres
FLASK_APP=./utils/debug.py FLASK_DEBUG=True DATABASE_URI=postgresql://postgres:password@192.168.231.111/airview CREATE_DB=True flask run
```
