from django import template

register = template.Library()


@register.filter
def in_group(user, group_name: str) -> bool:
    if not user or not hasattr(user, "groups"):
        return False
    return user.groups.filter(name=group_name).exists()
