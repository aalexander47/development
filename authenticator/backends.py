from django.contrib.auth.models import User

class EmailOrUsernameModelBackend(object):
    def authenticate(self, request, username=None, password=None):
        try:
            # Check if the input is an email
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # If not, try with username
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None