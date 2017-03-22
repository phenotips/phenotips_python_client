
import unittest
import json
import rest

class PhenotipsTestCase(unittest.TestCase):

    def setUp(self):
        self.conn = rest.PhenotipsClient()
        self.sess = self.conn.get_phenotips_session(username='demo', password='demo123')

    def tearDown(self):
        self.conn.delete_patient('Test01', self.sess) 

    def test_login(self):
         
        phenotips_session = self.conn.get_phenotips_session(username='demo', password='demo123')
        assert(phenotips_session)

        invalid_user_session = self.conn.get_phenotips_session(username='demox', password='demo123')
        assert(not invalid_user_session)

        invalid_password_session = self.conn.get_phenotips_session(username='demo', password='demo123x')
        assert(not invalid_password_session)

   
    def test_get_patient(self):
       
        all_patients_from_phenotips = self.conn.get_patient(self.sess)
        assert(all_patients_from_phenotips)
        all_patients_from_phenotips = all_patients_from_phenotips.get('patientSummaries',[]) 
        all_eids = [p['eid'] for p in all_patients_from_phenotips if p['eid']]
        total_from_phenotips = len(all_eids)
        assert(total_from_phenotips>0)

        eid = 'P0000797'
        patient_from_phenotips = self.conn.get_patient(self.sess, eid)
        assert(patient_from_phenotips)
        eid_from_phenotips = str(patient_from_phenotips['external_id'])
        assert(eid_from_phenotips == eid)

        authorised_patient_id = 'P0000002'
        permission = self.conn.get_permissions(self.sess, authorised_patient_id)
        assert(permission)

        unauthorised_patient_id = 'P0000001'
        permission = self.conn.get_permissions(self.sess, unauthorised_patient_id)
        assert(not permission)

    def test_get_patient_auth(self):
       
        ''' 
        As used by command line functions, e.g. load_patient
        '''
        auth='demo:demo123'
        session = self.conn.get_phenotips_session(auth=auth)
        assert(session)

        all_patients_from_phenotips = self.conn.get_patient(session)
        assert(all_patients_from_phenotips)
        all_patients_from_phenotips = all_patients_from_phenotips.get('patientSummaries',[]) 
        all_eids = [p['eid'] for p in all_patients_from_phenotips if p['eid']]
        total_from_phenotips = len(all_eids)
        assert(total_from_phenotips>0)

        eid = 'P0000797'
        patient_from_phenotips = self.conn.get_patient(session, eid)
        assert(patient_from_phenotips)
        eid_from_phenotips = str(patient_from_phenotips['external_id'])
        assert(eid_from_phenotips == eid)

    @staticmethod
    def load_patient(file_location):
        with open(file_location, 'r') as json_data:
            for line in json_data:
                dataset = json.loads(line)
            return dataset
     
    def test_update_patient(self):      
        file_location = "./test_data/patient-update-name.json"
        patient = PhenotipsTestCase.load_patient(file_location)
        eid = 'P0000005'
        self.conn.update_patient(eid, self.sess, patient)
        patient_from_phenotips = self.conn.get_patient(self.sess, eid)
        assert(patient_from_phenotips)
        patient_name = patient_from_phenotips['patient_name']
        name_from_phenotips = str(patient_name['first_name'])
        assert(name_from_phenotips == 'Updated')

        unauthorised_eid = 'P0000798'
        self.conn.update_patient(unauthorised_eid, self.sess, patient)            

    def test_create_and_delete_patient(self):
        file_location = "./test_data/simple-patient-Test01.json"
        patient = PhenotipsTestCase.load_patient(file_location)
        self.conn.create_patient(self.sess, patient)
        eid = 'Test01'
        patient_retrieved = self.conn.get_patient(self.sess, eid)
        assert(patient_retrieved)
        assert(not 'patients' in patient_retrieved) # Indicates that there is more than one patient with this eid in the DB.
        patient_name = patient_retrieved['patient_name']
        name_retrieved = str(patient_name['first_name'])
        assert(name_retrieved == 'Paolo') 
        self.conn.delete_patient(eid, self.sess) 
        permissions = self.conn.get_permissions(session=self.sess, eid=eid)
        assert(not permissions)
            
    def test_get_permissions(self):      
        file_location = "./test_data/simple-patient-Test01.json"
        patient = PhenotipsTestCase.load_patient(file_location)
        self.conn.create_patient(self.sess, patient)
        eid = 'Test01'
        permissions = self.conn.get_permissions(self.sess, eid=eid)
        links = permissions['links']
        links_0 = links[0]
        allowed_methods = links_0['allowedMethods']
        assert(len(allowed_methods)==3)
        assert('GET' in allowed_methods)
        assert('PATCH' in allowed_methods)
        assert('PUT' in allowed_methods)
        self.conn.delete_patient(eid, self.sess) 

        unauthorised_ID = 'P0000001'
        permissions = self.conn.get_permissions(self.sess, ID=unauthorised_ID)
        assert(not permissions)

    def test_update_permissions(self):      
        file_location = "./test_data/simple-patient-Test01.json"
        patient = PhenotipsTestCase.load_patient(file_location)
        self.conn.create_patient(self.sess, patient)
        eid = 'Test01'
        original_permissions =  {"links":[{"allowedMethods":["GET","PATCH","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions","rel":"self"},{"allowedMethods":["GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/owner","rel":"https://phenotips.org/rel/owner"},{"allowedMethods":["DELETE","GET","PUT","PATCH"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/collaborators","rel":"https://phenotips.org/rel/collaborators"},{"allowedMethods":["GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/visibility","rel":"https://phenotips.org/rel/visibility"},{"allowedMethods":["DELETE","GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006","rel":"https://phenotips.org/rel/patientRecord"}],"owner":{"links":[{"allowedMethods":["GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/owner","rel":"https://phenotips.org/rel/owner"}],"id":"xwiki:XWiki.demo","name":"Demo Guest","email":"support@phenotips.org","type":"user"},"visibility":{"links":[{"allowedMethods":["GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/visibility","rel":"https://phenotips.org/rel/visibility"}],"level":"private","label":"private","description":"Private cases are only accessible to their owners, but they do contribute to aggregated statistics."},"collaborators":{"links":[{"allowedMethods":["DELETE","GET","PUT","PATCH"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/collaborators","rel":"https://phenotips.org/rel/collaborators"}],"collaborators":[]}}
        new_permissions =       {"links":[{"allowedMethods":["GET","PATCH","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions","rel":"self"},{"allowedMethods":["GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/owner","rel":"https://phenotips.org/rel/owner"},{"allowedMethods":["DELETE","GET","PUT","PATCH"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/collaborators","rel":"https://phenotips.org/rel/collaborators"},{"allowedMethods":["GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/visibility","rel":"https://phenotips.org/rel/visibility"},{"allowedMethods":["DELETE","GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006","rel":"https://phenotips.org/rel/patientRecord"}],"owner":{"links":[{"allowedMethods":["GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/owner","rel":"https://phenotips.org/rel/owner"}],"id":"xwiki:XWiki.demo","name":"Demo Guest","email":"support@phenotips.org","type":"user"},"visibility":{"links":[{"allowedMethods":["GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/visibility","rel":"https://phenotips.org/rel/visibility"}],"level":"public","label":"private","description":"Private cases are only accessible to their owners, but they do contribute to aggregated statistics."},"collaborators":{"links":[{"allowedMethods":["DELETE","GET","PUT","PATCH"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/collaborators","rel":"https://phenotips.org/rel/collaborators"}],"collaborators":[]}}
        self.conn.update_permissions(new_permissions, self.sess, eid=eid)
        permissions = self.conn.get_permissions(self.sess, eid=eid)
        assert(permissions['visibility']['label'] == 'public')
        self.conn.update_permissions(original_permissions, self.sess, eid=eid)
        permissions = self.conn.get_permissions(self.sess, eid=eid)
        assert(permissions['visibility']['label'] == 'private')
        self.conn.delete_patient(eid, self.sess) 

    def test_update_owner(self):        
        file_location = "./test_data/simple-patient-Test01.json"
        patient = PhenotipsTestCase.load_patient(file_location)
        self.conn.create_patient(self.sess, patient)
        eid = 'Test01' 
        original_owner =    {"links":[{"allowedMethods":["GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/owner","rel":"self"},{"allowedMethods":["GET","PATCH","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions","rel":"https://phenotips.org/rel/permissions"},{"allowedMethods":["DELETE","GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006","rel":"https://phenotips.org/rel/patientRecord"}],"id":"xwiki:XWiki.demo","name":"Demo Guest","email":"support@phenotips.org","type":"user"}
        new_owner =         {"links":[{"allowedMethods":["GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000001/permissions/owner","rel":"self"},{"allowedMethods":["GET","PATCH","PUT"],"href":"http://localhost:8080/rest/patients/P0000001/permissions","rel":"https://phenotips.org/rel/permissions"},{"allowedMethods":["DELETE","GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000001","rel":"https://phenotips.org/rel/patientRecord"}],"id":"xwiki:XWiki.Admin","name":"Administrator","email":"support@phenotips.org","type":"user"}
        self.conn.update_owner(new_owner, self.sess, eid=eid)
        permissions = self.conn.get_permissions(self.sess, eid=eid)
        assert(permissions['owner']['name'] == 'Administrator')
        self.conn.update_owner(original_owner, self.sess, eid=eid)
        permissions = self.conn.get_permissions(self.sess, eid=eid)
        assert(permissions['owner']['name'] == 'Demo Guest')
        self.conn.delete_patient(eid, self.sess) 

    def test_get_vocabularies(self):      
        vocab = 'terms/HP:0000556'
        r = self.conn.get_vocabularies(session=self.sess,vocabulary=vocab)
        assert(str(r['name']) == 'Retinal dystrophy')

if __name__ == '__main__':
    unittest.main()
