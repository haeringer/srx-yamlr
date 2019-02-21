import json
import oyaml as yaml
import logging
import traceback

logger = logging.getLogger(__name__)


def queryset_to_var(queryset):
    '''
    Convert django queryset to string or list, depending on queryset content
    '''
    if queryset:
        if len(queryset) > 1:
            rval = []
            for q in queryset:
                rval.append(q.name)
        else:
            rval = queryset[0].name
    else:
        rval = ''
    return rval


def view_exception(Exception):
    logger.error(traceback.format_exc())
    return dict(error=json.dumps(traceback.format_exc()))


def convert_dict_to_yaml(dictionary):
    return dict(yamlconfig=yaml.dump(dictionary, default_flow_style=False))
