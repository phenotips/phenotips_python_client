
import unittest
import json
import rest

class PhenotipsLoginTestCase(unittest.TestCase):

    def setUp(self):
        self.conn = rest.PhenotipsClient()
        self.sess = self.conn.request_phenotips_session('demo', 'demo123')

    def tearDown(self):
        pass

    def test_login(self):
         
        phenotips_session = self.conn.request_phenotips_session('demo', 'demo123')
        assert(phenotips_session)

        invalid_user_session = self.conn.request_phenotips_session('demox', 'demo123')
        assert(not invalid_user_session)

        invalid_password_session = self.conn.request_phenotips_session('demo', 'demo123x')
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

        patient_from_cache = self.conn.get_patient(self.sess, eid)
        assert(patient_from_cache)
        eid_from_cache = str(patient_from_cache['external_id'])
        assert(eid_from_cache == eid_from_phenotips)

        authorised_patient_id = 'P0000002'
        permission = self.conn.get_permissions(self.sess, authorised_patient_id)
        assert(permission)

        unauthorised_patient_id = 'P0000001'
        permission = self.conn.get_permissions(self.sess, unauthorised_patient_id)
        assert(not permission)

    #def test_get_patient_auth(self):
       
    #    ''' 
    #    As used by command line functions, e.g. load_patient
    #    '''
    #    self.conn = PhenotipsClient()
    #    auth='demo:demo123'
    #    session_phenotips = self.conn.create_session_with_phenotips(auth=auth)
    #    assert(session_phenotips)

    #    all_patients_from_phenotips = self.conn.get_patient(session_phenotips)
    #    assert(all_patients_from_phenotips)
    #    all_patients_from_phenotips = all_patients_from_phenotips.get('patientSummaries',[]) 
    #    all_eids = [p['eid'] for p in all_patients_from_phenotips if p['eid']]
    #    total_from_phenotips = len(all_eids)
    #    assert(total_from_phenotips>0)

    #    eid = 'P0000797'
    #    patient_from_phenotips = self.conn.get_patient(session_phenotips, eid)
    #    assert(patient_from_phenotips)
    #    eid_from_phenotips = str(patient_from_phenotips['external_id'])
    #    assert(eid_from_phenotips == eid)

    #@staticmethod
    #def load_patient(file_location):
    #    with open(file_location, 'r') as json_data:
    #        for line in json_data:
    #            dataset = json.loads(line)
    #        return dataset
     
    #def test_update_patient(self):      
    #    self.conn = PhenotipsClient()
    #    with self.app.session_transaction() as sess:
    #        file_location = "./test_data/patient-update-name.json"
    #        patient = PhenotipsLoginTestCase.load_patient(file_location)
    #        eid = 'P0000005'
    #        self.conn.update_patient(eid, sess, patient)
    #        patient_from_phenotips = self.conn.get_patient(sess, eid)
    #        assert(patient_from_phenotips)
    #        patient_name = patient_from_phenotips['patient_name']
    #        name_from_phenotips = str(patient_name['first_name'])
    #        assert(name_from_phenotips == 'Updated')

    #        unauthorised_eid = 'P0000798'
    #        self.conn.update_patient(unauthorised_eid, sess, patient)            

    #def test_create_and_delete_patient(self):
    #    self.conn = PhenotipsClient()
    #    with self.app.session_transaction() as sess:
    #        file_location = "./test_data/simple-patient-Test01.json"
    #        patient = PhenotipsLoginTestCase.load_patient(file_location)
    #        self.conn.create_patient(sess, patient)
    #        eid = 'Test01'
    #        patient_retrieved = self.conn.get_patient(sess, eid)
    #        assert(patient_retrieved)
    #        patient_name = patient_retrieved['patient_name']
    #        name_retrieved = str(patient_name['first_name'])
    #        assert(name_retrieved == 'Paolo') 
    #        self.conn.delete_patient(eid, sess) 
    #        permissions = self.conn.get_permissions(session=session, eid=eid)
    #        assert(not permissions)
            
    #def test_get_permissions(self):      
    #    self.conn = PhenotipsClient()

    #    with self.app.session_transaction() as sess:  
    #        file_location = "./test_data/simple-patient-Test01.json"
    #        patient = PhenotipsLoginTestCase.load_patient(file_location)
    #        self.conn.create_patient(sess, patient)
    #        eid = 'Test01'
    #        permissions = self.conn.get_permissions(sess, eid=eid)
    #        links = permissions['links']
    #        links_0 = links[0]
    #        allowed_methods = links_0['allowedMethods']
    #        assert(len(allowed_methods)==3)
    #        assert(str(allowed_methods[0]) == 'GET')
    #        assert(str(allowed_methods[1]) == 'PATCH')
    #        assert(str(allowed_methods[2]) == 'PUT')
    #        self.conn.delete_patient(eid, sess) 

    #        unauthorised_ID = 'P0000001'
    #        permissions = self.conn.get_permissions(sess, ID=unauthorised_ID)
    #        assert(not permissions)

    #def test_update_permissions(self):      
    #    self.conn = PhenotipsClient()

    #    with self.app.session_transaction() as sess:  
    #        file_location = "./test_data/simple-patient-Test01.json"
    #        patient = PhenotipsLoginTestCase.load_patient(file_location)
    #        self.conn.create_patient(sess, patient)
    #        eid = 'Test01'
    #        original_permissions =  {"links":[{"allowedMethods":["GET","PATCH","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions","rel":"self"},{"allowedMethods":["GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/owner","rel":"https://phenotips.org/rel/owner"},{"allowedMethods":["DELETE","GET","PUT","PATCH"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/collaborators","rel":"https://phenotips.org/rel/collaborators"},{"allowedMethods":["GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/visibility","rel":"https://phenotips.org/rel/visibility"},{"allowedMethods":["DELETE","GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006","rel":"https://phenotips.org/rel/patientRecord"}],"owner":{"links":[{"allowedMethods":["GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/owner","rel":"https://phenotips.org/rel/owner"}],"id":"xwiki:XWiki.demo","name":"Demo Guest","email":"support@phenotips.org","type":"user"},"visibility":{"links":[{"allowedMethods":["GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/visibility","rel":"https://phenotips.org/rel/visibility"}],"level":"private","label":"private","description":"Private cases are only accessible to their owners, but they do contribute to aggregated statistics."},"collaborators":{"links":[{"allowedMethods":["DELETE","GET","PUT","PATCH"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/collaborators","rel":"https://phenotips.org/rel/collaborators"}],"collaborators":[]}}
    #        new_permissions =       {"links":[{"allowedMethods":["GET","PATCH","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions","rel":"self"},{"allowedMethods":["GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/owner","rel":"https://phenotips.org/rel/owner"},{"allowedMethods":["DELETE","GET","PUT","PATCH"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/collaborators","rel":"https://phenotips.org/rel/collaborators"},{"allowedMethods":["GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/visibility","rel":"https://phenotips.org/rel/visibility"},{"allowedMethods":["DELETE","GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006","rel":"https://phenotips.org/rel/patientRecord"}],"owner":{"links":[{"allowedMethods":["GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/owner","rel":"https://phenotips.org/rel/owner"}],"id":"xwiki:XWiki.demo","name":"Demo Guest","email":"support@phenotips.org","type":"user"},"visibility":{"links":[{"allowedMethods":["GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/visibility","rel":"https://phenotips.org/rel/visibility"}],"level":"public","label":"private","description":"Private cases are only accessible to their owners, but they do contribute to aggregated statistics."},"collaborators":{"links":[{"allowedMethods":["DELETE","GET","PUT","PATCH"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/collaborators","rel":"https://phenotips.org/rel/collaborators"}],"collaborators":[]}}
    #        self.conn.update_permissions(new_permissions, sess, eid=eid)
    #        permissions = self.conn.get_permissions(sess, eid=eid)
    #        assert(permissions['visibility']['label'] == 'public')
    #        self.conn.update_permissions(original_permissions, sess, eid=eid)
    #        permissions = self.conn.get_permissions(sess, eid=eid)
    #        assert(permissions['visibility']['label'] == 'private')
    #        self.conn.delete_patient(eid, sess) 

    #def test_update_owner(self):        

    #    with self.app.session_transaction() as sess: 
    #        file_location = "./test_data/simple-patient-Test01.json"
    #        patient = PhenotipsLoginTestCase.load_patient(file_location)
    #        self.conn.create_patient(sess, patient)
    #        eid = 'Test01' 
    #        original_owner =    {"links":[{"allowedMethods":["GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions/owner","rel":"self"},{"allowedMethods":["GET","PATCH","PUT"],"href":"http://localhost:8080/rest/patients/P0000006/permissions","rel":"https://phenotips.org/rel/permissions"},{"allowedMethods":["DELETE","GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000006","rel":"https://phenotips.org/rel/patientRecord"}],"id":"xwiki:XWiki.demo","name":"Demo Guest","email":"support@phenotips.org","type":"user"}
    #        new_owner =         {"links":[{"allowedMethods":["GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000001/permissions/owner","rel":"self"},{"allowedMethods":["GET","PATCH","PUT"],"href":"http://localhost:8080/rest/patients/P0000001/permissions","rel":"https://phenotips.org/rel/permissions"},{"allowedMethods":["DELETE","GET","PUT"],"href":"http://localhost:8080/rest/patients/P0000001","rel":"https://phenotips.org/rel/patientRecord"}],"id":"xwiki:XWiki.Admin","name":"Administrator","email":"support@phenotips.org","type":"user"}
    #        self.conn.update_owner(new_owner, sess, eid=eid)
    #        permissions = self.conn.get_permissions(sess, eid=eid)
    #        assert(permissions['owner']['name'] == 'Administrator')
    #        self.conn.update_owner(original_owner, sess, eid=eid)
    #        permissions = self.conn.get_permissions(sess, eid=eid)
    #        assert(permissions['owner']['name'] == 'Demo Guest')
    #        self.conn.delete_patient(eid, sess) 

    #def test_get_vocabularies(self):      

    #    with self.app.session_transaction() as sess: 
    #        vocab = 'terms/HP:0000556'
    #        r = self.conn.get_vocabularies(session=sess,vocabulary=vocab)
    #        assert(str(r['name']) == 'Retinal dystrophy')

if __name__ == '__main__':
    unittest.main()
