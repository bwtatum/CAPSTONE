"""
Permissions Helpers

Contains reusable authorization checks for admin portal access.

The portal views intentionally use group based access control so that:
- normal employees can use the timeclock UI
- portal admins can manage schedules and policy
"""

from django.core.exceptions import PermissionDenied

def portal_admin_required(view_func):
    """
    Decorator enforcing portal access to Admin group members or Superusers.
    """
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
            
        # BUG FIX: Allow access if the user is a superuser OR in the "Admin" group
        is_admin_group = request.user.groups.filter(name="Admin").exists()
        
        if not (request.user.is_superuser or is_admin_group):
            raise PermissionDenied
            
        return view_func(request, *args, **kwargs)

    return _wrapped