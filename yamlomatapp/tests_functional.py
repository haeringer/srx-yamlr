from django.test import TestCase
# from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class SeleniumTest(TestCase):

    def setUp(self):
        self.browser = webdriver.Remote(
            command_executor='http://selenium_hub:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME
        )
        self.browser.implicitly_wait(10)

    def test_visit_site_with_browser(self):
        self.browser.get('http://web:8000')
        self.assertIn("SRX YAMLr", self.browser.title)


# class MySeleniumTests(StaticLiveServerTestCase):
#     fixtures = ['user-data.json']

#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.browser = webdriver.Remote(
#             command_executor='http://selenium_hub:4444/wd/hub',
#             desired_capabilities=DesiredCapabilities.CHROME
#         )
#         cls.browser.implicitly_wait(10)

#     @classmethod
#     def tearDownClass(cls):
#         cls.browser.quit()
#         super().tearDownClass()

#     def test_login(self):
#         self.browser.get('%s%s' % (self.live_server_url, '/login/'))
#         username_input = self.browser.find_element_by_name("username")
#         username_input.send_keys('admin')
#         password_input = self.browser.find_element_by_name("password")
#         password_input.send_keys('ifmRos=')
#         self.browser.find_element_by_xpath('//input[@value="Log in"]').click()
