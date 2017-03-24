# Python client for Phenotips API


A python browser extension for interfacing with the [Phenotips API](https://phenotips.org/DevGuide/RESTfulAPI).

## Usage

Assuming phenotips server is running on port 8080 on the local host, this is how to connect:

```python
from phenotips_python_client import PhenotipsClient
conn=PhenotipsClient(host='localhost',port=8080)
```

Retrieve all patients:
```python
patients=conn.get_patient(auth='username:password')
```

Retrieve patient with a specific external id:
```python
patient=conn.get_patient(auth='username:password',eid='Patient_XYZ')
```

Create/update patient:
```python
conn.update_patient(auth='username:password', patient={'external_id':'patient1','reporter':'Joe Bloggs','owner':'Joe Bloggs', 'features':{}}, eid='patient1')
```

Dump all patients to a Mongo database on local host running on port 27017:
```python
conn.dump_to_mongodb(auth='username:password',mongo_host='localhost',mongo_port='27017',mongo_dbname='patients')
```

### Authenticated Session 
Get a session:
```python
session=conn.get_phenotips_session(auth='username:password')
```
The session can now be used to access Phenotips with no further requirement for ```auth``` E.g. retrieve all patients:
```python
patients = conn.get_patient(session=session)
```

## Example

Write external id, HPO terms, genes and solved status to hpo.txt:

```python
from __future__ import print_function
import sys
from phenotips_python_client import PhenotipsClient

# this is passed from command line
auth=sys.argv[1]

conn=PhenotipsClient(host='localhost',port=8080)

patients=conn.get_patient(auth=auth)['patientSummaries']

hpo_file=open('hpo.txt', 'w+')

print('eid', 'hpo', 'genes', 'solved', sep='\t',file=hpo_file)

for p in patients:
    eid=p['eid']
    print(eid)
    patient=conn.get_patient(auth=auth,eid=eid)
    print(patient)
    if 'features' in patient:
        hpo=','.join([f['id'] for f in patient['features']])
    else:
        hpo=''
    if 'genes' in patient:
        genes=','.join([g['gene'] for g in patient['genes']])
    else:
        genes=''
    solved=patient['solved']['status']
    print(eid, hpo, genes, solved, sep='\t',file=hpo_file)
  ```
