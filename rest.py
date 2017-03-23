from __future__ import print_function
import requests
from binascii import b2a_base64, a2b_base64
import re
import os.path
import sys 
import httplib
import urllib
import urlparse
import re
import socket
import gzip
import StringIO
from StringIO import StringIO
import time
import random
from binascii import b2a_base64, a2b_base64
import json
import pandas
import hashlib
import pymongo

class PhenotipsClient():

    def __init__(self, host='localhost', port='8080',debug=True,print_requests=True):
        self.site='%s:%s'%(host,port,)

    def get_phenotips_session(self,auth=None,username=None,password=None):
        if not auth: 
            auth = '%s:%s' % (username, password,)
        encoded_auth=b2a_base64(auth).strip()
        headers={'Authorization':'Basic %s'%encoded_auth, 'Accept':'application/json'}
        url='http://%s/rest/patients?start=%d&number=%d' % (self.site,0,1)
        s = requests.Session()
        response = s.get(url, headers=headers)
        print (response.text)
        if response.status_code == 200 :
            return s
        else:
            return None

    def get_patient(self,auth=None,session=None,eid=None,number=10000,start=0):
        """
        Get patient with eid or all patients if not
        specified
        """
        if auth: 
            session = self.get_phenotips_session(auth)
        if not session:
            return None
        headers={'Accept':'application/json'} 
        if not eid:
            url='http://%s/rest/patients?start=%d&number=%d' % (self.site,start,number)
            r=session.get(url, headers=headers)
            try:
                r=r.json()
                return r
            except:
                return None
        else:
            url='http://%s/rest/patients/eid/%s' % (self.site,str(eid))
            r=session.get(url, headers=headers)
            try:
                r=r.json()
                if '_id' in r:
                    del r['_id']
                return r
            except:
                return None

    def patient_exists(self,auth=None,session=None,eid=''):
        p=self.get_patient(auth=auth,session=session,eid=eid)
        if p is None:
            return False
        else:
            return True

    def get_permissions(self,auth=None,session=None,ID=None, eid=None):
        """
        Retrieves all permissions: owner, collaborators, visibility.
        """
        if auth: 
            session = self.get_phenotips_session(auth)
        if not session:
            return None
        if not ID:
            p=self.get_patient(session=session,eid=eid)
            if not p:
                return None
            ID=p['id']
        headers={'Accept':'application/json; application/xml'}
        r=session.get('http://%s/rest/patients/%s/permissions' % (self.site,ID), headers=headers)
        if not r:
            return None
        return r.json()

    # create patient
    def create_patient(self,auth=None,session=None, patient={}):
        if auth: 
            session = self.get_phenotips_session(auth)
        if not session:
            return None
        headers={'Content-Type':'application/json', 'Accept':'application/json'}
        io=StringIO()
        json.dump(patient,io)
        json_patient=io.getvalue()
        session.post('http://%s/rest/patients' % (self.site), headers=headers, data=json_patient)

    def update_patient(self,auth=None,session=None,eid='',patient={}):
        """
        Update patient if exists, otherwise create.
        """
        if auth: 
            session = self.get_phenotips_session(auth)
        if not session:
            return None
        patient['external_id']=eid
        if self.patient_exists(session=session,eid=eid):
            io=StringIO()
            json.dump(patient,io)
            json_patient=io.getvalue()
            print('update')
            print(json_patient)
            headers={'Content-Type':'application/json', 'Accept':'application/json'}
            session.put('http://%s/rest/patients/eid/%s' % (self.site,eid), headers=headers, data=json_patient)
        else:
            print('create')
            print(patient)
            self.create_patient(session=session,patient=patient)


    def update_permissions(self,auth=None,session=None,permissions={},ID=None,eid=None):
        """
        Update permissions of patient.
        """
        #permission = { "owner" : { "id" : "xwiki:XWiki.RachelGillespie" }, "visibility" : { "level":  "private" }, "collaborators" : [{ "id" : "xwiki:XWiki.UKIRDC", "level" : "edit" }, { "id" : "xwiki:Groups.UKIRDC Administrators)", "level" : "edit" }] }
        if auth: 
            session = self.get_phenotips_session(auth)
        if not session:
            return None
        if not ID:
            p=self.get_patient(session=session,eid=eid)
            ID=p['id']
        headers={'Content-Type':'application/json', 'Accept':'application/json'}
        io=StringIO()
        json.dump(permissions,io)
        json_permissions=io.getvalue()
        p=session.put('http://%s/rest/patients/%s/permissions'% (self.site,ID), headers=headers, data=json_permissions, )
        print(p)
        return(p)


    def update_owner(self,auth=None,session=None,owner={},ID=None,eid=None):
        """
        Update owner of patient.
        """
        #permission = { "owner" : { "id" : "xwiki:XWiki.RachelGillespie" }, "visibility" : { "level":  "private" }, "collaborators" : [{ "id" : "xwiki:XWiki.UKIRDC", "level" : "edit" }, { "id" : "xwiki:Groups.UKIRDC Administrators)", "level" : "edit" }] }
        if auth: 
            session = self.get_phenotips_session(auth)
        if not session:
            return None
        if not ID:
            p=self.get_patient(session=session,eid=eid)
            ID=p['id']
        headers={'Content-Type':'application/json', 'Accept':'application/json'}
        io=StringIO()
        json.dump(owner,io)
        json_owner=io.getvalue()
        p=session.put('http://%s/rest/patients/%s/permissions/owner'%(self.site,ID), headers=headers, data=json_owner)
        print(p)
        return(p)


    def delete_patient(self,auth=None,session=None,eid=''):
        """
        Delete patient.
        """
        if auth: 
            session = self.get_phenotips_session(auth)
        if not session:
            return None
        headers={'Content-Type':'application/json', 'Accept':'application/json'}
        p=session.delete('http://%s/rest/patients/eid/%s'%(self.site,eid), headers=headers)
        print(p)

    def update_phenotips_from_csv(self, info, auth, owner_group=[], collaborators=[], contact={}):
        """
        Each column in the csv file
        represent a patient atribute.
        This only supports one feature for now
        """
        info=pandas.read_csv(info,sep=',')
        print(info.columns.values)
        session = self.get_phenotips_session(auth=auth)
        for i, r, in info.iterrows():
            print(r)
            #if r['owner']!=owner: continue
            patient=dict()
            patient['external_id']=r['sample']
            if  not isinstance(r['sample'],basestring) or len(r['sample']) < 4: continue
            if 'ethnicity' in r:
                ethnicity=r['ethnicity']
                if isinstance(ethnicity,str):
                    patient["ethnicity"]={"maternal_ethnicity":[ethnicity],"paternal_ethnicity":[ethnicity]}
                else:
                    patient["ethnicity"]={"maternal_ethnicity":[],"paternal_ethnicity":[]}
            patient["prenatal_perinatal_history"]={}
            patient["prenatal_perinatal_phenotype"]={"prenatal_phenotype":[],"negative_prenatal_phenotype":[]}
            patient['reporter']=r['owner']
            if 'gender' in r:
                gender=dict({'M':'M','m':'M','f':'F','F':'F','1':'M','2':'F'}).get(str(r['gender']),'U')
                patient['sex']=gender
            #if 'solved' in r: patient['solved']=r['solved']
            #patient['contact']={ "user_id":r['owner'], "name":r['owner'], "email":'', "institution":'' }
            patient['contact']=contact
            patient['clinicalStatus']={ "clinicalStatus":"affected" }
            #patient['disorders']=[ { "id":r['phenotype'], 'label':''} ]
            print(patient)
            r['phenotype']=str(r['phenotype'])
            patient['features']=[ { "id":hpo, 'label':'', 'type':'phenotype', 'observed':'yes' } for hpo in r['phenotype'].split(';') ]
            #update_patient(ID=r['sample'],session=session,patient=patient)
            self.update_patient(eid=patient['external_id'], session=session, patient=patient)
            #delete_patient(ID=r['sample'],session=session,patient=patient)
            # if patient exists, update patient, otherwise create patient
            #self.update_patient(eid=patient['external_id'],session=session,patient=patient)
            permissions = { "owner" : owner_group, "visibility" : { "level":  "private" }, "collaborators" : collaborators  }
            print(permissions)
            #self.update_permissions(permissions=permissions,eid=patient['external_id'],session=session)
            self.update_owner(owner=owner_group,session=session,eid=patient['external_id'])

    def patient_hpo(self,auth=None,session=None,eid=''):
        """
        Retrieve HPO terms for patient
        """
        if auth: 
            session = self.get_phenotips_session(auth)
        patient=self.get_patient(session=session,eid=eid)
        if patient:
            if 'features' in patient: return [f['id'] for f in patient['features']]
            else:  return []
        else: return []

    def dump_hpo_to_tsv(self, outFile, auth):
        """
        Dumps the HPO terms from a patient record
        to tsv file.
        """
        session = self.get_phenotips_session(auth=auth)
        patients=self.get_patient(session=session)['patientSummaries']
        #file(sprintf('uclex_hpo_%d-%d-%d.txt'),)
        hpo_file=open(outFile, 'w+')
        print('eid', 'hpo', 'genes', 'solved', sep='\t',file=hpo_file)
        for p in patients:
            eid=p['eid']
            print(eid)
            patient=self.get_patient(session=session,eid=eid)
            print(patient)
            if 'features' in patient:
                hpo=','.join([f['id'] for f in patient['features']])
            else:
                hpo=''
            if 'genes' in patient:
                genes=','.join([g['gene'] for g in patient['genes']])
            else:
                genes=''
            if 'solved' in patient:
                solved=patient['solved']['status']
            else:
                solved='unsolved'
            print(eid, hpo, genes, solved, sep='\t',file=hpo_file)


    def dump_patient_to_json(self, auth):
        """
        Dumps patient to JSON.
        """
        session = self.get_phenotips_session(auth=auth)
        patients=self.get_patient(session=session)['patientSummaries']
        for p in patients:
            eid=p['eid']
            print(eid)
            patient=self.get_patient(session=session,eid=eid)
            io=StringIO()
            json.dump(patient,io)
            json_patient=io.getvalue()
            print(json_patient)


    def dump_to_mongodb(self, auth, mongo_host='localhost', mongo_port=27016, mongo_dbname='patients'):
        """
        Dumps all patients to a Mongo database
        """
        import pymongo
        client = pymongo.MongoClient(host=mongo_host, port=int(mongo_port))
        db=client[mongo_dbname]
        db.patients.drop()
        session = self.get_phenotips_session(auth=auth)
        patients=self.get_patient(session=session)['patientSummaries']
        for p in patients:
            eid=p['eid']
            print(eid)
            p=self.get_patient(session=session,eid=eid)
            db.patients.insert(p,w=0)
        db.patients.ensure_index('external_id')
        db.patients.ensure_index('report_id')
        db.patients.ensure_index('features.id')
        db.patients.ensure_index('sex')
        db.patients.ensure_index('genes.gene')
        db.patients.ensure_index('solved')
        db.patients.ensure_index('clinicalStatus.clinicalStatus')
        db.patients.ensure_index('specificity.score')


    def update_mongodb(self, auth, mongo_host='localhost', mongo_port=27016, mongo_dbname='patients',update_fields=['features'],patient_ids=[]):
        """
        Will only update fields which have changed in Phenotips
        """
        import pymongo
        client = pymongo.MongoClient(host=mongo_host, port=int(mongo_port))
        db=client[mongo_dbname]
        session = self.get_phenotips_session(auth=auth)
        for eid in patient_ids:
            print(eid)
            p=self.get_patient(session=session,eid=eid)
            print(p)
            if p is None: raise 'patient does not exist maybe your credential are wrong?'
            # if patient does not exist in mongodb, create it
            if db.patients.find_one({'external_id':eid}) is None:
                db.patients.insert(p,w=0)
                continue
            for u in update_fields:
                print( u )
                if u not in p: p[u]=[]
                db.patients.update({'external_id':eid},{'$set':{u:p[u]}},w=0)


    def get_vocabularies(self,auth=None,session=None,vocabulary=''):
        if auth: 
            session = self.get_phenotips_session(auth)
        if not session:
            return None
        # get vocabularies
        #http://localhost:1235/rest/vocabularies/terms/HP:0000556
        headers={'Accept':'application/json; application/xml'}
        r=session.get('http://%s/rest/vocabularies/%s'%(self.site,vocabulary), headers=headers)
        if not r:
            return None
        return r.json()




