from django import template
from quiz import models as QMODEL

register = template.Library()


@register.simple_tag
def all_courses():
    return QMODEL.Course.objects.all()