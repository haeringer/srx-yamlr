import uuid
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .views import *



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

        z = SrxZone.objects.filter()
        zone = z[0].name

        for i in range(3):
            c.post('/ajax/newobject/', {
                'objtype': 'address',
                'zone': zone,
                'name': 'TEST_ADDRESS_{}'.format(i),
                'value': '10.20.30.{}/32'.format(i),
                },
            )
        c.post('/ajax/newobject/', {
            'objtype': 'addrset',
            'zone': zone,
            'name': 'TEST_ADDRSET',
            'valuelist[]': ['TEST_ADDRESS_0','TEST_ADDRESS_1'],
            },
        )
        for i in range(3):
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
            'valuelist[]': ['TEST_APPLICATION_0','TEST_APPLICATION_1'],
            },
        )


    def test_for_created_test_objects(self):

        a = SrxAddress.objects.filter().get(name='TEST_ADDRESS_0')
        self.assertEqual(a.name, 'TEST_ADDRESS_0')

        a = SrxAddrSet.objects.filter().get(name='TEST_ADDRSET')
        self.assertEqual(a.name, 'TEST_ADDRSET')

        a = SrxApplication.objects.filter().get(name='TEST_APPLICATION_0')
        self.assertEqual(a.name, 'TEST_APPLICATION_0')

        a = SrxAppSet.objects.filter().get(name='TEST_APPSET')
        self.assertEqual(a.name, 'TEST_APPSET')


    def test_login_page_plus_redirect(self):

        response = self.client.post('/auth/login/', {
            'username': username, 'password': password},
        )
        self.assertEqual(response.status_code, 302)
