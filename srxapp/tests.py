import uuid
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .cghelpers import queryset_to_var
from .models import SrxAddress, SrxAddrSet, SrxApplication, \
    SrxAppSet, SrxZone, SrxPolicy


username = 'testuser'
password = '123456'


class viewTests(TestCase):

    @classmethod
    def setUpTestData(cls):

        user = User.objects.create(username=username)
        user.set_password(password)
        user.save()

        c = Client()
        c.get('/ajax/loadobjects/', {'loadpolicies': 'False'})
        c.get('/ajax/loadobjects/', {'loadpolicies': 'True'})

        c.login(username=username, password=password)
        c.get('/')

        # Add new test objects to database
        z = SrxZone.objects.filter()
        zone_a = z[0].name
        zone_b = z[1].name

        for i in range(2):
            c.post('/ajax/newobject/', {
                'objtype': 'address',
                'zone': zone_a,
                'name': 'TEST_ADDRESS_{}'.format(i),
                'value': '10.20.30.{}/32'.format(i),
                },
            )
        c.post('/ajax/newobject/', {
            'objtype': 'addrset',
            'zone': zone_a,
            'name': 'TEST_ADDRSET',
            'valuelist[]': ['TEST_ADDRESS_0', 'TEST_ADDRESS_1'],
            },
        )
        c.post('/ajax/newobject/', {
            'objtype': 'address',
            'zone': zone_b,
            'name': 'TEST_ADDRESS_3',
            'value': '10.20.30.3/32',
            },
        )
        for i in range(2):
            c.post('/ajax/newobject/', {
                'objtype': 'application',
                'name': 'TEST_APPLICATION_{}'.format(i),
                'port': '123{}'.format(i),
                'protocol': 'tcp',
                },
            )
        c.post('/ajax/newobject/', {
            'objtype': 'appset',
            'name': 'TEST_APPSET',
            'valuelist[]': ['TEST_APPLICATION_0', 'TEST_APPLICATION_1'],
            },
        )

        # Build test policy with newly created objects
        cls.policyid = str(uuid.uuid4())

        obj_a = SrxAddrSet.objects.get(name='TEST_ADDRSET')
        obj_b = SrxAddress.objects.get(name='TEST_ADDRESS_3')
        obj_c = SrxApplication.objects.get(name='TEST_APPLICATION_0')
        obj_d = SrxAppSet.objects.get(name='TEST_APPSET')

        c.post('/ajax/updatepolicy/', {
            'action': 'add',
            'policyid': cls.policyid,
            'objectid': obj_a.id,
            'objtype': 'addrset',
            'source': 'from',
            },
        )
        c.post('/ajax/updatepolicy/', {
            'action': 'add',
            'policyid': cls.policyid,
            'objectid': obj_b.id,
            'objtype': 'address',
            'source': 'to',
            },
        )
        c.post('/ajax/updatepolicy/', {
            'action': 'add',
            'policyid': cls.policyid,
            'objectid': obj_c.id,
            'objtype': 'application',
            'source': 'app',
            },
        )
        c.post('/ajax/updatepolicy/', {
            'action': 'add',
            'policyid': cls.policyid,
            'objectid': obj_d.id,
            'objtype': 'appset',
            'source': 'app',
            },
        )

    def test_for_created_test_objects(self):

        o = SrxAddress.objects.filter().get(name='TEST_ADDRESS_0')
        self.assertEqual(o.name, 'TEST_ADDRESS_0')

        o = SrxAddrSet.objects.filter().get(name='TEST_ADDRSET')
        self.assertEqual(o.name, 'TEST_ADDRSET')

        o = SrxApplication.objects.filter().get(name='TEST_APPLICATION_0')
        self.assertEqual(o.name, 'TEST_APPLICATION_0')

        o = SrxAppSet.objects.filter().get(name='TEST_APPSET')
        self.assertEqual(o.name, 'TEST_APPSET')

    def test_login_page_plus_redirect(self):

        response = self.client.post('/auth/login/', {
            'username': username, 'password': password},
        )
        self.assertEqual(response.status_code, 302)

    def test_generated_policy_name(self):

        p = SrxPolicy.objects.filter(policyid=self.policyid)
        pname = queryset_to_var(p)
        self.assertEqual(pname, 'allow-TEST_ADDRSET-to-TEST_ADDRESS_3')

    def test_object_presence_in_new_policy(self):

        o = SrxApplication.objects.filter(application__policyid=self.policyid)
        oname = queryset_to_var(o)
        self.assertEqual(oname, 'TEST_APPLICATION_0')

    def test_delete_object_from_policy(self):

        obj = SrxAppSet.objects.get(name='TEST_APPSET')

        self.client.post('/ajax/updatepolicy/', {
            'action': 'delete',
            'policyid': self.policyid,
            'objectid': obj.id,
            'objtype': 'appset',
            'source': 'app',
            },
        )

        o = SrxAppSet.objects.filter(appset__policyid=self.policyid)
        oname = queryset_to_var(o)
        self.assertEqual(oname, '')
