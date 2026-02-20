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
    Decorator enforcing portal access to Admin group members only.

    Raises PermissionDenied for:
    - unauthenticated users
    - authenticated users who are not in the Admin group
    """

    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not request.user.groups.filter(name="Admin").exists():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped
