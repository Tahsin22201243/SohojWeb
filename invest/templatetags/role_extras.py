from django import template
from django.core.exceptions import ObjectDoesNotExist
from ..models import Profile
import os

register = template.Library()

@register.filter
def user_is_business(user):
    if not user or not getattr(user, "is_authenticated", False):
        return False
    try:
        return user.profile.is_business
    except (Profile.DoesNotExist, ObjectDoesNotExist, AttributeError):
        return False

@register.filter
def user_is_investor(user):
    if not user or not getattr(user, "is_authenticated", False):
        return False
    try:
        return user.profile.is_investor
    except (Profile.DoesNotExist, ObjectDoesNotExist, AttributeError):
        return False


@register.filter
def basename(path):
    try:
        return os.path.basename(path)
    except Exception:
        return path
