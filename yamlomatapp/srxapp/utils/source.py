import os
import logging
from ruamel.yaml import YAML
from uuid import uuid4
from django.core.cache import cache

from srxapp.utils import helpers

logger = logging.getLogger(__name__)
yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)


class sourceData:
    def __init__(self, request):
        workspace = "workspace/" + request.user.get_username()
        yamlfile = os.environ.get("YM_YAMLFILE", "")
        self.filepath = workspace + "/" + yamlfile
        self.workingdict = request.session["workingdict"]
        self.configdict = request.session["configdict"]

    def read_source_file(self):
        logger.info("Importing YAML source data...")
        with open(self.filepath, "r") as sourcefile:
            self.sourcedict = yaml.load(sourcefile)
            cache.set("sourcedict", self.sourcedict)

    def update_source_file(self):
        sourcedict = cache.get("sourcedict")
        if not sourcedict:
            self.read_source_file()
            sourcedict = cache.get("sourcedict")

        def update_simple_dict(vartype):
            if vartype in self.configdict:
                vals = self.configdict[vartype]
                sourcedict[vartype].update(vals)

        def update_zone_dict(vartype):
            if "zones" in self.configdict:
                for zone, items in self.configdict["zones"].items():
                    if vartype in items:
                        vals = self.configdict["zones"][zone][vartype]
                        source = sourcedict["zones"][zone][vartype]
                        if isinstance(vals, list):
                            for v in vals:
                                source.update(v)
                        else:
                            source.update(vals)

        update_simple_dict("policies")
        update_simple_dict("applications")
        update_simple_dict("applicationsets")
        update_zone_dict("addresses")
        update_zone_dict("addrsets")

        logger.info("Writing YAML config to source file...")

        with open(self.filepath, "w") as sourcefile:
            yaml.dump(sourcedict, sourcefile)

    def import_zones(self):
        zones = self.workingdict.setdefault("zones", [])

        for name in self.sourcedict["zones"]:
            zones.append({"name": name})

    def import_addresses(self):
        addresses = self.workingdict.setdefault("addresses", [])

        for zone, values in self.sourcedict["zones"].items():
            zone_addresses = values["addresses"]
            for name, ip in zone_addresses.items():
                addresses.append(
                    {"name": name, "val": ip, "zone": zone, "id": uuid4().hex}
                )
            # add one 'any' address per zone to configuration set
            addresses.append(
                {"name": "any", "val": zone, "zone": zone, "id": uuid4().hex}
            )

    def import_addrsets(self):
        addrsets = self.workingdict.setdefault("addrsets", [])

        for zone, values in self.sourcedict["zones"].items():
            if "addrsets" in values:
                if values["addrsets"]:
                    for name, addresses in values["addrsets"].items():
                        addrsets.append(
                            {
                                "name": name,
                                "val": addresses,
                                "zone": zone,
                                "id": uuid4().hex,
                            }
                        )

    def import_applications(self):
        applications = self.workingdict.setdefault("applications", [])

        def fill_application_list(applications_dict):
            for name, values in applications_dict.items():
                val = str(values["protocol"]) + " " + str(values.get("port", ""))
                applications.append({"name": name, "val": val, "id": uuid4().hex})

        fill_application_list(self.sourcedict["applications"])
        fill_application_list(self.sourcedict["default-applications"])

    def import_appsets(self):
        appsets = self.workingdict.setdefault("appsets", [])

        for name, values in self.sourcedict["applicationsets"].items():
            appsets.append({"name": name, "val": values, "id": uuid4().hex})

    def import_policies(self):
        policies = self.workingdict.setdefault("policies", [])

        for name, values in self.sourcedict["policies"].items():

            sorted_dict_for_hash = helpers.dict_with_sorted_list_values(
                source=values["source"], destination=values["destination"]
            )
            policyhash = hash(repr(sorted_dict_for_hash))

            policies.append(
                {
                    "name": name,
                    "policyhash": policyhash,
                    "fromzone": values["fromzone"],
                    "tozone": values["tozone"],
                    "source": values["source"],
                    "destination": values["destination"],
                    "application": values["application"],
                    "action": values["action"],
                }
            )
