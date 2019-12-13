import sys
from io import StringIO
from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required

from baseapp import helpers


@login_required(redirect_field_name=None)
def main_view(request):
    try:
        context = helpers.get_baseapp_context(request)
    except Exception:
        helpers.view_exception(Exception)
        raise Http404("HTTP 404 Error")
    return render(request, "srxpolsrch/main.html", context)


def search(request):
    try:
        inp_src = request.GET.get("input_from", None)
        inp_dest = request.GET.get("input_to", None)

        wd = request.session["workingdict"]

        def find_objects(inp):
            objects = []

            for obj in wd["addresses"]:
                if inp in obj["name"].upper() or inp in obj["val"].upper():
                    objects.append(obj)

            for obj in wd["addrsets"]:
                if inp in obj["name"].upper():
                    objects.append(obj)
                else:
                    for val in obj["val"]:
                        if inp in val.upper():
                            objects.append(obj)
                            break
            return objects

        objects_src = find_objects(inp_src) if inp_src else None
        objects_dest = find_objects(inp_dest) if inp_dest else None

        def object_in_policy(pol, direction):
            objects = objects_src if direction == "source" else objects_dest
            for obj in objects:
                if isinstance(pol[direction], str):
                    if obj["name"] == pol[direction]:
                        return True
                else:
                    for obj_single in pol[direction]:
                        if obj["name"] == obj_single:
                            return True
            return False

        policies = []
        for pol in wd["policies"]:
            if objects_src and not objects_dest:
                if object_in_policy(pol, "source"):
                    policies.append(pol)
            elif objects_dest and not objects_src:
                if object_in_policy(pol, "destination"):
                    policies.append(pol)
            elif objects_src and objects_dest:
                if object_in_policy(pol, "source") and object_in_policy(pol, "destination"):
                    policies.append(pol)

        response = policies
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)


def get_policy_yaml(request):
    try:
        policyhash = request.GET.get("policyhash", None)
        wd = request.session["workingdict"]

        response = None
        for policy in wd["policies"]:
            if policyhash == policy["policyhash"]:
                pol = deepcopy(policy)
                pol.pop("name")
                pol.pop("policyhash")

                temp_in_memory_out = StringIO()
                sys.stdout = temp_in_memory_out
                yaml = YAML()
                yaml.indent(mapping=2, sequence=4, offset=2)
                yaml.dump(pol, sys.stdout)
                response = temp_in_memory_out.getvalue()
                break
    except Exception:
        response = helpers.view_exception(Exception)
    return JsonResponse(response, safe=False)
