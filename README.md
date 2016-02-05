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

Retrieve patient with a specific external id:
```python
patient=conn.get_patients(auth='username:password',eid='Patient_XYZ')
```

Create/update patient:
```python
conn.update_patient(auth='username:password', patient={'external_id':'patient1','reporter':'Joe Bloggs','owner':'Joe Bloggs', 'features':{}}, eid='patient1')
```

Dump all patients to a Mongo database on local host running on port 27017:
```python
conn.dump_to_mongodb(auth='username:password',mongo_host='localhost',mongo_port='27017',mongo_dbname='patients')
```

## Example

```python
from __future__ import print_function
import sys
import rest
import datetime


now = datetime.datetime.now()

auth=sys.argv[1]

patients=rest.get_patient(auth)['patientSummaries']

#file(sprintf('uclex_hpo_%d-%d-%d.txt'),)
hpo_file=open('uclex-hpo.txt', 'w+')

print('eid', 'hpo', 'genes', 'solved', sep='\t',file=hpo_file)

for p in patients:
    eid=p['eid']
    print(eid)
    patient=rest.get_patient(auth,eid)
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
