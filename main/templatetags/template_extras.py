from django import template
from django.contrib.auth.models import Group
import os

register = template.Library()


@register.filter
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


@register.filter
def basename(value):
    return os.path.basename(value)
