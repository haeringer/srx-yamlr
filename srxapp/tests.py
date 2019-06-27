from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User


class Tests(TestCase):

    def setUp(self):
        username = 'testuser'
        password = '123456'

        user = User.objects.create(username=username)
        user.set_password(password)
        user.save()

        client = self.client = Client()
        client.login(username=username, password=password)
        client.get('/ajax/loadobjects/')
        client.get('/')

        # Add new test objects to database
        zones = self.client.session['workingdict']['zones']
        zone_a = zones[0]['name']
        zone_b = zones[1]['name']
        self.testzone = zone_a

        for i in range(2):
            client.post('/ajax/object/create/address/', {
                'zone': zone_a,
                'name': 'TEST_ADDRESS_{}'.format(i),
                'value': '10.20.30.{}/32'.format(i),
                },
            )
        client.post('/ajax/object/create/addrset/', {
            'zone': zone_a,
            'name': 'TEST_ADDRSET',
            'valuelist[]': ['TEST_ADDRESS_0', 'TEST_ADDRESS_1'],
            },
        )
        client.post('/ajax/object/create/address/', {
            'zone': zone_b,
            'name': 'TEST_ADDRESS_3',
            'value': '10.20.30.3/32',
            },
        )
        for i in range(2):
            client.post('/ajax/object/create/application/', {
                'name': 'TEST_APPLICATION_{}'.format(i),
                'port': '123{}'.format(i),
                'protocol': 'tcp',
                },
            )
        client.post('/ajax/object/create/appset/', {
            'name': 'TEST_APPSET',
            'valuelist[]': ['TEST_APPLICATION_0', 'TEST_APPLICATION_1'],
            },
        )

    def test_created_objects(self):
        self.assertIn('TEST_ADDRESS_0', str(self.client.session['configdict']))

    def test_session_logged_in_user(self):
        self.assertEqual(self.client.session['_auth_user_id'], '1')

    def test_session_imported_data(self):
        self.assertIn('zones', self.client.session['workingdict'])

    # def test_build_policy(self):
    #     self.policyid = '123456789'
    #     client = self.client

    #     obj_a = SrxAddrSet.objects.get(name='TEST_ADDRSET')
    #     obj_b = SrxAddress.objects.get(name='TEST_ADDRESS_3')
    #     obj_c = SrxApplication.objects.get(name='TEST_APPLICATION_0')
    #     obj_d = SrxAppSet.objects.get(name='TEST_APPSET')

    #     client.post('/ajax/policy/add/address/', {
    #         'policyid': self.policyid,
    #         'objectid': obj_a.id,
    #         'direction': 'from',
    #         },
    #     )
    #     client.post('/ajax/policy/add/address/', {
    #         'policyid': self.policyid,
    #         'objectid': obj_b.id,
    #         'direction': 'to',
    #         },
    #     )
    #     client.post('/ajax/policy/add/application/', {
    #         'policyid': self.policyid,
    #         'objectid': obj_c.id,
    #         },
    #     )
    #     client.post('/ajax/policy/add/application/', {
    #         'policyid': self.policyid,
    #         'objectid': obj_d.id,
    #         },
    #     )
