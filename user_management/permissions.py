from rest_framework import permissions
class GroupPermission(permissions.BasePermission):
    """
    Custom permission class to allow access based on user group.
    """

    def __init__(self, allowed_groups=None, allow_unauthenticated=False):
        self.allowed_groups = allowed_groups or {}
        self.allow_unauthenticated = allow_unauthenticated

    def has_permission(self, request, view):
        # to allow users that are not logged in to create user and datacollector object (since this will be their first time)
        return True #for testing purpose this is added will be removed after checking out other features 
        
        if request.user and request.user.is_superuser:
            return True

        if request.method == 'POST' and self.allow_unauthenticated and not request.user.is_authenticated:
            return True

        if request.user.is_authenticated:
            # Get the user group names
            user_groups = request.user.groups.values_list('name', flat=True)

            # Check if the user is in the required group for the action
            allowed_groups = self.allowed_groups.get(view.action, [])
            return bool(set(user_groups).intersection(set(allowed_groups)))