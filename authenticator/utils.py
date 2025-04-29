from django.contrib.auth.models import User, Group

def add_group_to_user(user, group_name):
    try:
        # Retrieve the group object
        group = Group.objects.get(name=group_name)
        
        # Add the group to the user
        user.groups.add(group)
        
        # Save the user object
        user.save()
        
        return True, "Group added successfully."
    except Group.DoesNotExist:
        return False, f"Group '{group_name}' does not exist."
    except User.DoesNotExist:
        return False, f"User '{user.username}' does not exist."
    


def remove_group_from_user(user, group_name):
    try:
        # Retrieve the group object
        group = Group.objects.get(name=group_name)
        
        # Remove the group from the user
        user.groups.remove(group)
        
        # Save the user object
        user.save()
        
        return True, "Group removed successfully."
    except Group.DoesNotExist:
        return False, f"Group '{group_name}' does not exist."
    except User.DoesNotExist:
        return False, f"User '{user.username}' does not exist."