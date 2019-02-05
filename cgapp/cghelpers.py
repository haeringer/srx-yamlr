
def queryset_to_var(queryset):
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
