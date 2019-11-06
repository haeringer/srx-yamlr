from copy import deepcopy
from uuid import uuid4

from baseapp import helpers


class srxPolicy:
    def __init__(self, request):
        self.configdict = request.session["configdict"]
        # Debug issue with disappearing config statements
        helpers.log_config(self.configdict)
        self.workingdict = request.session["workingdict"]
        self.direction = request.POST.get("direction", None)
        self.name = request.POST.get("objname", None)
        self.zone = request.POST.get("zone", None)
        self.policyname = request.POST.get("policyname", None)
        self.previousname = request.POST.get("previousname", None)

    def get_direction_variables(self):
        if self.direction == "from":
            zone, direction = "fromzone", "source"
        elif self.direction == "to":
            zone, direction = "tozone", "destination"
        return zone, direction

    def extract_policy_from_configdict(self):
        policydict = deepcopy(
            self.configdict.setdefault("policies", {}).setdefault(self.policyname, {})
        )
        return policydict

    def update_configdict_with_policy(self, policydict):
        configdict = deepcopy(self.configdict)
        configdict.setdefault("policies", {}).setdefault(self.policyname, {})

        if policydict != {}:
            policy = {self.policyname: policydict}
            configdict["policies"].update(policy)
        else:
            configdict["policies"].pop(self.policyname)
            if configdict["policies"] == {}:
                configdict.pop("policies")

        helpers.log_config(configdict)
        return configdict

    def check_for_policy_existing(self, policydict):
        p_existing = None

        if "source" not in policydict or "destination" not in policydict:
            return

        sorted_dict_for_hash = helpers.dict_with_sorted_list_values(
            fromzone=policydict["fromzone"],
            tozone=policydict["tozone"],
            source=policydict["source"],
            destination=policydict["destination"]
        )
        newpolicyhash = helpers.get_hash(sorted_dict_for_hash)

        for p in self.workingdict["policies"]:
            if newpolicyhash == p["policyhash"]:
                p_existing = deepcopy(p)

        return p_existing

    def get_existing_policy_subvalues(self, p_existing):
        pe_detail = dict(
            srcaddresses=[],
            srcaddrsets=[],
            destaddresses=[],
            destaddrsets=[],
            applications=[],
            appsets=[],
            action=[],
        )

        def get_objects(workingdict, obj_type):
            objects = []
            p_part = p_existing[obj_type]

            for obj in workingdict:
                if ((isinstance(p_part, list) and obj["name"] in p_part)
                        or (isinstance(p_part, str)
                            and helpers.in_string(obj["name"])(p_part))):
                    if ((obj_type == "source" and obj["zone"] == p_existing["fromzone"])
                        or (obj_type == "destination"
                            and obj["zone"] == p_existing["tozone"])
                            or (obj_type == "application")):
                        objects.append(obj)
            return objects

        wd = self.workingdict
        pe_detail["srcaddresses"] = get_objects(wd["addresses"], "source")
        pe_detail["srcaddrsets"] = get_objects(wd["addrsets"], "source")
        pe_detail["destaddresses"] = get_objects(wd["addresses"], "destination")
        pe_detail["destaddrsets"] = get_objects(wd["addrsets"], "destination")
        pe_detail["applications"] = get_objects(wd["applications"], "application")
        pe_detail["appsets"] = get_objects(wd["appsets"], "application")
        pe_detail["pname"] = p_existing["name"]
        pe_detail["action"] = p_existing["action"]

        return pe_detail

    def format_existing_policy(self, p_existing):
        pname = str(p_existing["name"])

        del p_existing["name"]
        del p_existing["policyhash"]

        pe_fmt = dict(policies={pname: p_existing})

        return pe_fmt

    def update_policyname(self):
        cd = self.configdict
        cd["policies"][self.policyname] = cd["policies"].pop(self.previousname)
        helpers.log_config(cd)
        return cd

    def add_address(self):
        p = self.extract_policy_from_configdict()
        zone, direction = self.get_direction_variables()

        p[zone] = self.zone
        if direction not in p:
            p[direction] = self.name
        else:
            if isinstance(p[direction], str):
                p[direction] = [p[direction]]
            p[direction].append(self.name)

        p_existing = self.check_for_policy_existing(p)
        if p_existing:
            pe_detail = self.get_existing_policy_subvalues(p_existing)
            pe_fmt = self.format_existing_policy(p_existing)

            return dict(p_exists=True, pe_detail=pe_detail, p_existing=pe_fmt)

        return self.update_configdict_with_policy(p)

    def delete_address(self):
        p = self.extract_policy_from_configdict()
        zone, direction = self.get_direction_variables()

        if isinstance(p[direction], list):
            p[direction].remove(self.name)
            if len(p[direction]) == 1:
                p[direction] = p[direction][0]
        else:
            p.pop(direction)
            p.pop(zone)

        return self.update_configdict_with_policy(p)

    def add_application(self):
        p = self.extract_policy_from_configdict()

        if "application" not in p:
            p["application"] = self.name
            p["action"] = "permit"
        else:
            if isinstance(p["application"], str):
                p["application"] = [p["application"]]
            p["application"].append(self.name)

        return self.update_configdict_with_policy(p)

    def delete_application(self):
        p = self.extract_policy_from_configdict()

        if isinstance(p["application"], list):
            p["application"].remove(self.name)
            if len(p["application"]) == 1:
                p["application"] = p["application"][0]
        else:
            p.pop("application")
            p.pop("action")

        return self.update_configdict_with_policy(p)


class srxObject:
    def __init__(self, request):
        self.configdict = request.session["configdict"]
        self.workingdict = request.session["workingdict"]
        self.name = request.POST.get("name", None)
        self.zone = request.POST.get("zone", None)
        self.protocol = request.POST.get("protocol", None)
        port = request.POST.get("port", None)
        self.port = int(port) if port else None
        self.value = request.POST.get("value", None)
        self.valuelist = request.POST.getlist("valuelist[]", None)

    def extract_zone_from_configdict(self):
        zonedict = deepcopy(
            self.configdict.setdefault("zones", {}).setdefault(self.zone, {})
        )
        return zonedict

    def update_configdict_with_zone(self, zonedict):
        configdict = deepcopy(self.configdict)
        configdict.setdefault("zones", {}).setdefault(self.zone, {})
        configdict["zones"][self.zone].update(zonedict)
        helpers.log_config(configdict)
        return configdict

    def create_address(self):
        self.workingdict["addresses"].append(
            {"name": self.name, "val": self.value, "zone": self.zone, "id": uuid4().hex}
        )

        z = self.extract_zone_from_configdict()

        if "addresses" not in z:
            z["addresses"] = {self.name: self.value}
        else:
            if isinstance(z["addresses"], dict):
                z["addresses"] = [z["addresses"]]
            z["addresses"].append({self.name: self.value})

        return self.update_configdict_with_zone(z)

    def create_addrset(self):
        self.workingdict["addrsets"].append(
            {
                "name": self.name,
                "val": self.valuelist,
                "zone": self.zone,
                "id": uuid4().hex,
            }
        )

        z = self.extract_zone_from_configdict()

        if "addrsets" not in z:
            z["addrsets"] = {self.name: self.valuelist}
        else:
            if isinstance(z["addrsets"], dict):
                z["addrsets"] = [z["addrsets"]]
            z["addrsets"].append({self.name: self.valuelist})

        return self.update_configdict_with_zone(z)

    def create_application(self):
        val = str(self.protocol) + " " + str(self.port)

        self.workingdict["applications"].append(
            {"name": self.name, "val": val, "id": uuid4().hex}
        )

        configdict = dict(self.configdict)
        a = configdict.setdefault("applications", {})
        a[self.name] = {"protocol": self.protocol, "port": self.port}
        configdict["applications"].update(a)

        helpers.log_config(configdict)
        return configdict

    def create_appset(self):
        self.workingdict["appsets"].append(
            {"name": self.name, "val": self.valuelist, "id": uuid4().hex}
        )

        configdict = dict(self.configdict)
        a = configdict.setdefault("applicationsets", {})
        a[self.name] = self.valuelist
        configdict["applicationsets"].update(a)

        helpers.log_config(configdict)
        return configdict
