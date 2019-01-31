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


    def setUp(self):

        logged_in = self.client.login(username=username, password=password)
        self.assertIs(logged_in, True)


    def test_login_page_plus_redirect(self):

        response = self.client.post('/auth/login/', {
            'username': username, 'password': password},
        )
        self.assertEqual(response.status_code, 302)


    def test_main_page_load(self):

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)