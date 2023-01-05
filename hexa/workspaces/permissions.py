from hexa.user_management.models import User


def create_workspace(principal: User):
    """Only superusers can create a workspace"""
    return principal.is_superuser


def update_workspace(principal: User):
    """Only superusers can update a workspace"""
    return principal.is_superuser


def delete_workspace(principal: User):
    """Only superusers can delte a workspace"""
    return principal.is_superuser
