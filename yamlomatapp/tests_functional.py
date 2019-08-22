import socket

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from django.contrib.auth.models import User


class MySeleniumTests(StaticLiveServerTestCase):
    host = "0.0.0.0"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.host = socket.gethostbyname(socket.gethostname())
        cls.browser = webdriver.Remote(
            command_executor='http://selenium_chrome:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME
        )
        cls.browser.implicitly_wait(5)

        User.objects.create_user(
            username="functest_user",
            email="functest_user@example.com",
            password="123456"
        )

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def test_login_fail(self):
        self.browser.get('%s%s' % (self.live_server_url, ''))
        self.browser.find_element_by_id("id_username").send_keys('functest_user')
        self.browser.find_element_by_id("id_password").send_keys('invalid')
        self.browser.find_element_by_class_name("btn-block").click()
        error_class = self.browser.find_element_by_class_name("errorlist")
        self.assertIn("Please enter a correct username and password", error_class.text)

    def test_login(self):
        self.browser.get('%s%s' % (self.live_server_url, ''))
        self.browser.find_element_by_id("id_username").send_keys('functest_user')
        self.browser.find_element_by_id("id_password").send_keys('123456')
        self.browser.find_element_by_class_name("btn-block").click()
        search_el = self.browser.find_element_by_id("search-from")
        self.assertIsNotNone(search_el)
