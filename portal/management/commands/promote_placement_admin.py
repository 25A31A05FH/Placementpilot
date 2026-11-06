"""Promote an existing account to PlacementPilot administrator access.

This command never sets or reads a password. In production, set
PLACEMENT_ADMIN_USERNAME for one deployment, then remove that variable.
"""
import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from portal.models import Profile


class Command(BaseCommand):
    help = "Promote an existing user account to the PlacementPilot administrator role."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            default=os.environ.get("PLACEMENT_ADMIN_USERNAME", ""),
            help="Existing account username (defaults to PLACEMENT_ADMIN_USERNAME).",
        )

    def handle(self, *args, **options):
        username = (options.get("username") or "").strip()
        if not username:
            self.stdout.write("Skipping administrator promotion: no username configured.")
            return

        user = User.objects.filter(username__iexact=username).first()
        if user is None:
            raise CommandError(
                f"No account found for username '{username}'. Create the student account first."
            )

        profile, _ = Profile.objects.get_or_create(user=user)
        if profile.role != "admin":
            profile.role = "admin"
            profile.save(update_fields=["role"])

        if not user.is_staff:
            user.is_staff = True
            user.save(update_fields=["is_staff"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Administrator access enabled for '{user.username}'. The existing password was not changed."
            )
        )
