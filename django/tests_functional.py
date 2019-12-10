import socket

from time import sleep
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from django.contrib.auth.models import User

WAIT_DELAY = 10


class MySeleniumTests(StaticLiveServerTestCase):
    host = "0.0.0.0"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.host = socket.gethostbyname(socket.gethostname())
        cls.browser = webdriver.Remote(
            command_executor="http://selenium_chrome:4444/wd/hub",
            desired_capabilities=DesiredCapabilities.CHROME
        )
        cls.browser.implicitly_wait(WAIT_DELAY)

        User.objects.create_user(
            username="functest_user",
            email="functest_user@example.com",
            password="123456"
        )

        cls.browser.get("%s%s" % (cls.live_server_url, ""))
        cls.browser.find_element_by_id("id_username").send_keys("functest_user")
        cls.browser.find_element_by_id("id_password").send_keys("123456")
        cls.browser.find_element_by_class_name("btn-block").click()

        try:
            loading = True
            while loading is True:
                try:
                    WebDriverWait(cls.browser, 1).until(
                        EC.visibility_of_element_located((
                            By.CLASS_NAME, "pace-progress"
                        ))
                    )
                    sleep(1)
                except Exception:
                    loading = False
        except Exception:
            pass

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def find_by_id(self, id_):
        return WebDriverWait(self.browser, WAIT_DELAY).until(
            EC.presence_of_element_located((By.ID, id_))
        )

    def find_by_class(self, class_):
        return WebDriverWait(self.browser, WAIT_DELAY).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_))
        )

    def find_by_link_text(self, link_text):
        return WebDriverWait(self.browser, WAIT_DELAY).until(
            EC.presence_of_element_located((By.LINK_TEXT, link_text))
        )

    def find_by_css_selector(self, selector):
        return WebDriverWait(self.browser, WAIT_DELAY).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

    def test_srxpolbld_is_present(self):
        self.find_by_id("policybuilder").click()
        search_el = self.find_by_id("search-from")
        self.assertIsNotNone(search_el)

    def DISABLED_test_create_objects_search_and_select(self):
        """
        Disabled because of completely random failures :(
        """
        self.browser.get("%s%s" % (self.live_server_url, "/srx/policybuilder/"))

        # Create TESTADDRESS_01 (zone 1)
        self.find_by_id("create-object").click()
        self.find_by_id("create-object-dropdown-btn").click()
        self.find_by_link_text("Address").click()

        dropdown = self.find_by_id("address-form-control-zone")
        dropdown.click()
        dd_select = Select(dropdown)
        dd_select.select_by_index(1)

        self.find_by_id("address-form-control-name").send_keys("TESTADDRESS_01")
        self.find_by_id("address-form-control-ip").send_keys("10.1.1.1/24")
        self.find_by_id("create-object-save").click()
        sleep(2)

        # Create TESTADDRESS_02 (zone 1)
        self.find_by_id("create-object").click()
        sleep(1)
        self.find_by_id("create-object-dropdown-btn").click()
        self.find_by_link_text("Address").click()

        dropdown = self.find_by_id("address-form-control-zone")
        dropdown.click()
        dd_select = Select(dropdown)
        dd_select.select_by_index(1)

        self.find_by_id("address-form-control-name").send_keys("TESTADDRESS_02")
        self.find_by_id("address-form-control-ip").send_keys("10.1.1.2/24")
        self.find_by_id("create-object-save").click()
        sleep(2)

        # Create TESTADDRESS_03 (zone 2)
        self.find_by_id("create-object").click()
        sleep(1)
        self.find_by_id("create-object-dropdown-btn").click()
        self.find_by_link_text("Address").click()

        dropdown = self.find_by_id("address-form-control-zone")
        dropdown.click()
        dd_select = Select(dropdown)
        dd_select.select_by_index(2)

        self.find_by_id("address-form-control-name").send_keys("TESTADDRESS_03")
        self.find_by_id("address-form-control-ip").send_keys("10.1.2.3/24")
        self.find_by_id("create-object-save").click()
        sleep(2)

        # Create TESTADDRSET_01 (zone 1)
        self.find_by_id("create-object").click()
        sleep(1)
        self.find_by_id("create-object-dropdown-btn").click()
        self.find_by_link_text("Address Set").click()

        dd_addrzone = self.find_by_id("adrset-form-control-zone")
        dd_addrzone.click()
        dd_select = Select(dd_addrzone)
        dd_select.select_by_index(1)

        self.find_by_id("adrset-form-control-name").send_keys("TESTADDRSET_01")

        el1 = self.find_by_css_selector("option.small:nth-child(1)")
        el2 = self.find_by_css_selector("option.small:nth-child(2)")

        ActionChains(self.browser) \
            .click(el1) \
            .key_down(Keys.SHIFT) \
            .click(el2) \
            .key_up(Keys.SHIFT) \
            .perform()

        self.find_by_id("create-object-save").click()
        sleep(2)

        # Create TESTAPP_01
        self.find_by_id("create-object").click()
        sleep(1)
        self.find_by_id("create-object-dropdown-btn").click()
        self.find_by_link_text("Application").click()

        self.find_by_id("application-form-control-name").send_keys("TESTAPP_01")
        self.find_by_id("application-form-control-port").send_keys("12345")

        dropdown = self.find_by_id("application-form-control-protocol")
        dropdown.click()
        dd_select = Select(dropdown)
        dd_select.select_by_index(1)

        self.find_by_id("create-object-save").click()
        sleep(2)

        # Create TESTAPPSET_01
        self.find_by_id("create-object").click()
        sleep(1)
        self.find_by_id("create-object-dropdown-btn").click()
        self.find_by_link_text("Application Set").click()

        self.find_by_id("appset-form-control-name").send_keys("TESTAPPSET_01")

        multi = self.find_by_id("appset-form-control-objects")
        multi_select = Select(multi)
        multi_select.select_by_visible_text("TESTAPP_01")
        multi_select.select_by_visible_text("junos-icmp-ping")

        self.find_by_id("create-object-save").click()
        sleep(2)

        # Search and select created objects
        self.find_by_id("search-from").send_keys("TESTADDRESS_01")
        self.find_by_class("search-results-item").click()

        self.find_by_id("search-from").send_keys("TESTADDRSET_01")
        self.find_by_class("search-results-item").click()
