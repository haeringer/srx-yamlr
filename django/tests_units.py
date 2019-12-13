import os
import copy
import json

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User

HOST_VAR_FILE_PATH = "host_vars/kami-kaze.yml"
USERNAME = "unittest_user"
PASSWORD = "123456"
TOKEN = os.environ.get("GIT_TOKEN")

client_glob = None


def create_client_session():

    user = User.objects.create(username=USERNAME)
    user.set_password(PASSWORD)
    user.save()

    client = Client()
    client.login(username=USERNAME, password=PASSWORD)

    client.post(
        "/settings/token/gogs/",
        {"token": TOKEN},
    )

    client.get("/srx/policybuilder/")
    client.post("/srx/policybuilder/createconfigsession/")
    client.post(
        "/srx/policybuilder/sethostvarfilepath/",
        {"host_var_file_path": HOST_VAR_FILE_PATH},
    )
    client.get("/git/clonerepo/")
    client.get(
        "/srx/policybuilder/validatecache/",
        {"srcfile_commithash": "<invalidcommithash>"},
    )
    client.get(
        "/srx/policybuilder/importobjects/",
        {"srcfile_commithash": "<somecommithash>"},
    )

    global client_glob
    client_glob = client


class Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_client_session()

        zones = client_glob.session["workingdict"]["zones"]
        cls.zone_a = zones[0]["name"]
        cls.zone_b = zones[1]["name"]
        cls.testzone = cls.zone_a

        for i in range(2):
            client_glob.post(
                "/srx/policybuilder/object/create/address/",
                {
                    "zone": cls.zone_a,
                    "name": "TEST_ADDRESS_{}".format(i),
                    "value": "10.20.30.{}/32".format(i),
                },
            )
        client_glob.post(
            "/srx/policybuilder/object/create/addrset/",
            {
                "zone": cls.zone_a,
                "name": "TEST_ADDRSET",
                "valuelist[]": ["TEST_ADDRESS_0", "TEST_ADDRESS_1"],
            },
        )
        client_glob.post(
            "/srx/policybuilder/object/create/address/",
            {"zone": cls.zone_b, "name": "TEST_ADDRESS_3", "value": "10.20.30.3/32"},
        )
        for i in range(2):
            client_glob.post(
                "/srx/policybuilder/object/create/application/",
                {
                    "name": "TEST_APPLICATION_{}".format(i),
                    "port": "123{}".format(i),
                    "protocol": "tcp",
                },
            )
        client_glob.post(
            "/srx/policybuilder/object/create/appset/",
            {
                "name": "TEST_APPSET",
                "valuelist[]": ["TEST_APPLICATION_0", "TEST_APPLICATION_1"],
            },
        )

    def test_set_git_token(self):
        response = client_glob.post(
            "/settings/token/gogs/",
            {"token": TOKEN},
        )

        response_val = response.content.decode("utf-8")
        self.assertEqual(response_val, "0")

    def test_check_git_token(self):
        self.test_set_git_token()

        response = client_glob.post("/checktoken/gogs/")

        response_string = response.content.decode("utf-8")
        self.assertEqual(response_string, "true")

    def test_set_new_password(self):
        response = client_glob.post(
            "/settings/password/change/",
            {"password": "234567"},
        )
        response_val = response.content.decode("utf-8")
        self.assertEqual(response_val, "0")

    def test_get_commithash(self):
        response = client_glob.get(
            "/git/commithash/",
            {"file_path": HOST_VAR_FILE_PATH},
        )
        response_val = response.content.decode("utf-8")
        self.assertEqual(len(response_val), 40+2)

    def test_created_objects(self):
        configdict_str = str(client_glob.session["configdict"])
        obj_list = [
            "TEST_ADDRESS_0",
            "TEST_ADDRESS_3",
            "TEST_ADDRSET",
            "TEST_APPLICATION_0",
            "TEST_APPSET",
        ]

        for obj in obj_list:
            self.assertIn(obj, configdict_str)

    def test_session_logged_in_user(self):
        self.assertEqual(client_glob.session["_auth_user_id"], "1")

    def test_session_imported_data(self):
        self.assertIn("zones", client_glob.session["workingdict"])

    def test_build_policy(self):
        self.policyname = "allow-123456789-to-123456789"

        def post_address(direction, objname, zone):
            client_glob.post(
                "/srx/policybuilder/policy/add/address/",
                {
                    "policyname": self.policyname,
                    "direction": direction,
                    "objname": objname,
                    "zone": zone,
                },
            )

        def post_application(objname):
            client_glob.post(
                "/srx/policybuilder/policy/add/application/",
                {"policyname": self.policyname, "objname": objname},
            )

        post_address("from", "TEST_ADDRESS_0", self.zone_a)
        post_address("from", "TEST_ADDRSET", self.zone_a)
        post_address("to", "TEST_ADDRESS_3", self.zone_b)
        post_application("TEST_APPLICATION_0")
        post_application("TEST_APPSET")

        policy = client_glob.session["configdict"]["policies"][self.policyname]
        self.assertIn(self.zone_a, policy["fromzone"])
        self.assertIn(self.zone_b, policy["tozone"])
        self.assertIn("TEST_ADDRSET", policy["source"])
        self.assertIn("TEST_ADDRESS_3", policy["destination"])
        self.assertIn("TEST_APPLICATION_0", policy["application"])
        self.assertIn("TEST_APPSET", policy["application"])

    def test_rename_policy(self):
        client = copy.deepcopy(client_glob)
        self.test_build_policy()

        client.post(
            "/srx/policybuilder/policy/rename/",
            {
                "previousname": "allow-123456789-to-123456789",
                "policyname": "allow-TEST_ADDRESS_3-to-TEST_ADDRSET",
            },
        )

        self.assertIn(
            "allow-TEST_ADDRESS_3-to-TEST_ADDRSET",
            client.session["configdict"]["policies"],
        )

    def test_delete_objects_from_policy(self):
        client = copy.deepcopy(client_glob)
        self.test_build_policy()

        client.post(
            "/srx/policybuilder/policy/delete/address/",
            {
                "policyname": self.policyname,
                "direction": "from",
                "objname": "TEST_ADDRSET",
                "zone": self.zone_a,
            },
        )
        client.post(
            "/srx/policybuilder/policy/delete/application/",
            {"policyname": self.policyname, "objname": "TEST_APPSET"},
        )

        policy = client.session["configdict"]["policies"][self.policyname]
        self.assertNotIn("TEST_ADDRSET", policy)
        self.assertNotIn("TEST_APPSET", policy)

    def test_write_commit_yamlconfig(self):
        self.test_set_git_token()
        self.test_build_policy()

        client_glob.post("/srx/policybuilder/writeconfig/")
        response = client_glob.get("/git/diff/")
        diff = response.content.decode("utf-8")
        lines = diff.split("\\n")

        count = 0
        for line in lines:
            if line.startswith("+ "):
                count += 1

        self.assertEqual(26, count)

        self.assertIn("+    fromzone: untrust", diff)
        self.assertIn(
            "+    source:\\n+      - TEST_ADDRESS_0\\n+      - TEST_ADDRSET",
            diff
        )
        self.assertIn("+    tozone: OfficeLAN", diff)
        self.assertIn("+    destination: TEST_ADDRESS_3", diff)
        self.assertIn(
            "+    application:\\n+      - TEST_APPLICATION_0\\n+      - TEST_APPSET",
            diff
        )
        self.assertIn("+    action: permit", diff)

        client_glob.post(
            "/git/commitconfig/",
            {"host_var_file_path": HOST_VAR_FILE_PATH},
        )

        response = client_glob.get("/git/diff/")
        self.assertEqual(response.content, b'""')

    def test_check_session_status(self):
        response = client_glob.get("/session/status/")

        response_val = response.content.decode("utf-8")
        self.assertEqual(response_val, "0")

    def test_extend_session(self):
        response = client_glob.post("/session/extend/")

        response_val = response.content.decode("utf-8")
        self.assertEqual(response_val, "0")

    def test_change_password(self):
        response = client_glob.post(
            "/settings/password/change/",
            {"password": "654321"},
        )
        response_val = response.content.decode("utf-8")
        self.assertEqual(response_val, "0")

    def test_filter_object_list(self):
        response = client_glob.get(
            "/srx/policybuilder/filterobjects/",
            {"selectedzone": self.zone_a},
        )
        response_val = response.content.decode("utf-8")

        self.assertIn("TEST_ADDRESS_0", response_val)
        self.assertNotIn("TEST_ADDRESS_3", response_val)

    def test_search_address_object(self):
        inputdata = "TEST_ADDRESS"
        response = client_glob.get(
            "/srx/policybuilder/search/object/",
            {"input": inputdata, "searchtype": "from"},
        )
        response_val = response.content.decode("utf-8")

        self.assertIn("TEST_ADDRESS_0", response_val)
        self.assertIn("TEST_ADDRESS_1", response_val)
        self.assertIn("TEST_ADDRSET", response_val)

    def test_search_application_object(self):
        inputdata = "TEST_APPLICATION"
        response = client_glob.get(
            "/srx/policybuilder/search/object/",
            {"input": inputdata, "searchtype": "app"},
        )
        response_val = response.content.decode("utf-8")

        self.assertIn("TEST_APPLICATION_0", response_val)

    def test_load_modalcontent(self):
        response = client_glob.get("/srx/policybuilder/loadcontent/createmodal/")
        response_val = response.content.decode("utf-8")

        self.assertIn('<option class="small">TEST_ADDRESS_0</option>', response_val)
        self.assertIn('<option class="small">TEST_APPLICATION_0</option>', response_val)
        self.assertIn('<option value="{0}">{0}'.format(self.zone_a), response_val)

    def test_reset_config_session(self):
        response = client_glob.post("/srx/policybuilder/resetconfigsession/")

        response_val = response.content.decode("utf-8")
        self.assertEqual(response_val, "0")

    def test_get_baseapp_page(self):
        response = client_glob.get("/")
        self.assertEquals(response.status_code, 200)
        response_val = response.content.decode("utf-8")
        htmlstring_btn = 'class="btn btn-primary btn-lg appbtn mr-3" id="policysearch"'
        self.assertIn(htmlstring_btn, response_val)
        htmlstring_modal = '<div class="form-group" id="settings-modal-form">'
        self.assertIn(htmlstring_modal, response_val)

    def test_get_policybuild_page(self):
        response = client_glob.get("/srx/policybuilder/")
        self.assertEquals(response.status_code, 200)
        response_val = response.content.decode("utf-8")
        htmlstring = 'placeholder="Search IP address or object name"'
        self.assertIn(htmlstring, response_val)

    def test_get_policysearch_page(self):
        response = client_glob.get("/srx/policysearch/")
        self.assertEquals(response.status_code, 200)
        response_val = response.content.decode("utf-8")
        htmlstring = 'placeholder="Search for source object or prefix"'
        self.assertIn(htmlstring, response_val)

    def test_policy_search(self):
        response = client_glob.get(
            "/srx/policysearch/search/",
            {"input_from": "10.", "input_to": ""},
        )
        if response.content.decode("utf-8") == "[]":
            response = client_glob.get(
                "/srx/policysearch/search/",
                {"input_from": "192.", "input_to": ""},
            )
        response_dict = json.loads(response.content)
        self.assertIsNotNone(response_dict[0]["name"])
        return response_dict[0]["policyhash"]

    def test_get_policy_yaml(self):
        policyhash = self.test_policy_search()
        response = client_glob.get(
            "/srx/policysearch/getpolicyyaml/",
            {"policyhash": policyhash},
        )
        response_val = response.content.decode("utf-8")
        self.assertIn("\\ntozone: ", response_val)

    def test_load_policy(self):
        policyhash = self.test_policy_search()
        response = client_glob.get(
            "/srx/policysearch/loadpolicy/",
            {"policyhash": policyhash},
        )
        response_val = response.content.decode("utf-8")
        self.assertEquals(response.status_code, 200)
        self.assertIn("load_existing", response_val)
