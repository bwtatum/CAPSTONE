from django import template

register = template.Library()

@register.filter
def in_group(user, group_name: str) -> bool:
    # If the user is a superuser, bypass the group check and grant access
    if user and getattr(user, 'is_superuser', False):
        return True
        
    if not user or not hasattr(user, "groups"):
        return False
        
    return user.groups.filter(name=group_name).exists()