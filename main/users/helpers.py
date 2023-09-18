from django.contrib.auth.models import Permission


def get_perms(*models, scope=None):
    perms_list = []
    for model in models:
        if scope:
            perms = Permission.objects.filter(
                content_type__model=model, codename__startswith=scope
            )
        else:
            perms = Permission.objects.filter(content_type__model=model)
        perms_list.extend(perms)
    return perms_list
