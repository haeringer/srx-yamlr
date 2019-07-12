import git

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User


class Tests(TestCase):
    def setUp(self):
        username = "testuser"
        password = "123456"

        user = User.objects.create(username=username)
        user.set_password(password)
        user.save()

        self.client = Client()
        self.client.login(username=username, password=password)
        self.client.get("/ajax/loadobjects/")
        self.client.get("/")

        zones = self.client.session["workingdict"]["zones"]
        self.zone_a = zones[0]["name"]
        self.zone_b = zones[1]["name"]
        self.testzone = self.zone_a

        for i in range(2):
            self.client.post(
                "/ajax/object/create/address/",
                {
                    "zone": self.zone_a,
                    "name": "TEST_ADDRESS_{}".format(i),
                    "value": "10.20.30.{}/32".format(i),
                },
            )
        self.client.post(
            "/ajax/object/create/addrset/",
            {
                "zone": self.zone_a,
                "name": "TEST_ADDRSET",
                "valuelist[]": ["TEST_ADDRESS_0", "TEST_ADDRESS_1"],
            },
        )
        self.client.post(
            "/ajax/object/create/address/",
            {"zone": self.zone_b, "name": "TEST_ADDRESS_3", "value": "10.20.30.3/32"},
        )
        for i in range(2):
            self.client.post(
                "/ajax/object/create/application/",
                {
                    "name": "TEST_APPLICATION_{}".format(i),
                    "port": "123{}".format(i),
                    "protocol": "tcp",
                },
            )
        self.client.post(
            "/ajax/object/create/appset/",
            {
                "name": "TEST_APPSET",
                "valuelist[]": ["TEST_APPLICATION_0", "TEST_APPLICATION_1"],
            },
        )

    def test_set_git_token(self):
        token = "ka2bjlhPlVnATs2OrcAB8mg1JeRXBDO03yxZlz3c"
        response = self.client.post(
            "/ajax/settings/token/gogs/",
            {"token": token},
        )

        response_val = response.content.decode("utf-8")
        self.assertEqual(response_val, "0")

    def test_check_git_token(self):
        self.test_set_git_token()

        response = self.client.post("/ajax/checktoken/gogs/")

        response_string = response.content.decode("utf-8")
        self.assertEqual(response_string, "true")

    def test_set_new_password(self):
        response = self.client.post(
            "/ajax/settings/password/change/",
            {"password": "234567"},
        )
        response_val = response.content.decode("utf-8")
        self.assertEqual(response_val, "0")

    def test_created_objects(self):
        configdict_str = str(self.client.session["configdict"])
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
        self.assertEqual(self.client.session["_auth_user_id"], "1")

    def test_session_imported_data(self):
        self.assertIn("zones", self.client.session["workingdict"])

    def test_build_policy(self):
        self.policyname = "allow-123456789-to-123456789"

        def post_address(direction, objname, zone):
            self.client.post(
                "/ajax/policy/add/address/",
                {
                    "policyname": self.policyname,
                    "direction": direction,
                    "objname": objname,
                    "zone": zone,
                },
            )

        def post_application(objname):
            self.client.post(
                "/ajax/policy/add/application/",
                {"policyname": self.policyname, "objname": objname},
            )

        post_address("from", "TEST_ADDRESS_0", self.zone_a)
        post_address("from", "TEST_ADDRSET", self.zone_a)
        post_address("to", "TEST_ADDRESS_3", self.zone_b)
        post_application("TEST_APPLICATION_0")
        post_application("TEST_APPSET")

        policy = self.client.session["configdict"]["policies"][self.policyname]
        self.assertIn(self.zone_a, policy["fromzone"])
        self.assertIn(self.zone_b, policy["tozone"])
        self.assertIn("TEST_ADDRSET", policy["source"])
        self.assertIn("TEST_ADDRESS_3", policy["destination"])
        self.assertIn("TEST_APPLICATION_0", policy["application"])
        self.assertIn("TEST_APPSET", policy["application"])

    def test_rename_policy(self):
        self.test_build_policy()

        self.client.post(
            "/ajax/policy/rename/",
            {
                "previousname": "allow-123456789-to-123456789",
                "policyname": "allow-TEST_ADDRESS_3-to-TEST_ADDRSET",
            },
        )

        self.assertIn(
            "allow-TEST_ADDRESS_3-to-TEST_ADDRSET",
            self.client.session["configdict"]["policies"],
        )

    def test_delete_objects_from_policy(self):
        self.test_build_policy()

        self.client.post(
            "/ajax/policy/delete/address/",
            {
                "policyname": self.policyname,
                "direction": "from",
                "objname": "TEST_ADDRSET",
                "zone": self.zone_a,
            },
        )
        self.client.post(
            "/ajax/policy/delete/application/",
            {"policyname": self.policyname, "objname": "TEST_APPSET"},
        )

        policy = self.client.session["configdict"]["policies"][self.policyname]
        self.assertNotIn("TEST_ADDRSET", policy)
        self.assertNotIn("TEST_APPSET", policy)

    def test_write_yamlconfig(self):
        self.test_build_policy()
        self.client.post("/ajax/writeyamlconfig/")

        local_repo = git.Repo("workspace/testuser")
        diff = local_repo.git.diff()

        self.assertIn("TEST_ADDRSET", diff)
        self.assertIn("TEST_APPLICATION_0", diff)

    def test_commit_config(self):
        self.test_set_git_token()
        self.test_build_policy()
        self.test_write_yamlconfig()
        self.client.post("/ajax/commitconfig/")

        local_repo = git.Repo("workspace/testuser")
        diff = local_repo.git.diff()

        self.assertEqual(diff, "")

    def test_check_session_status(self):
        response = self.client.get("/ajax/session/status/")

        response_val = response.content.decode("utf-8")
        self.assertEqual(response_val, "0")

    def test_extend_session(self):
        response = self.client.post("/ajax/session/extend/")

        response_val = response.content.decode("utf-8")
        self.assertEqual(response_val, "0")
