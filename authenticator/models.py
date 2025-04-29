from django.db import models
from django.contrib.auth.models import AbstractUser
from allauth.account.views import SignupView


class CustomUser(AbstractUser):
    # Custom fields can be added here

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Custom related_name to avoid conflict
        blank=True,
        help_text=('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_query_name='customuser',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # Custom related_name to avoid conflict
        blank=True,
        help_text=('Specific permissions for this user.'),
        related_query_name='customuser',
    )

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)


class CustomSignupView(SignupView):
    def form_valid(self, form):
        # Save user and add first_name and last_name from the form data
        response = super().form_valid(form)
        user = self.user
        user.first_name = form.cleaned_data.get('first_name', '')
        user.last_name = form.cleaned_data.get('last_name', '')
        user.save()
        return response