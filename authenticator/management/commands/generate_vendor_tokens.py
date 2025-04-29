from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from rest_framework_simplejwt.tokens import RefreshToken
from user.models import UserProfile  # Import your custom model

class Command(BaseCommand):
    help = 'Generate JWT access tokens for all users in the vendor group.'

    def handle(self, *args, **kwargs):
        try:
            vendor_group = Group.objects.get(name='vendor')
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR('Vendor group does not exist'))
            return

        vendor_users = User.objects.filter(groups=vendor_group)

        if not vendor_users.exists():
            self.stdout.write(self.style.WARNING('No users in the vendor group'))
            return

        for user in vendor_users:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Save the token in the UserProfile model
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.access_token = access_token
            profile.save()

            self.stdout.write(self.style.SUCCESS(
                f'Saved token for User: {user.username}'
            ))

        self.stdout.write(self.style.SUCCESS('Token generation completed!'))
