# Python client for Phenotips API


A python browser extension for interfacing with the [Phenotips API](https://phenotips.org/DevGuide/RESTfulAPI).

## Usage

Assuming phenotips server is running on port 8080 on the local host, this is how to connect:

```python
from phenotips_client import PhenotipsClient
conn=PhenotipsClient(host='localhost',port=8080)
```

Retrieve all patients:
```python
patients=conn.get_patients(auth='username:password')
```

Create/update patient:
```python
conn.update_patient(auth='username:password', patient={'external_id':'patient1','reporter':'Joe Bloggs','owner':'Joe Bloggs', 'features':{}}, eid='patient1')
```

Dump all patients to a Mongo database on local host running on port 27017:
```python
conn.dump_to_mongodb(auth='username:password',mongo_host='localhost',mongo_port='27017',mongo_dbname='patients')
```


