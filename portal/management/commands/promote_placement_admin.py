"""Provision the dedicated PlacementPilot administrator.

The initial password is injected as a sensitive Vercel Production environment
variable. Existing accounts are never password-reset by subsequent deploys.
"""
import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from portal.models import Profile


class Command(BaseCommand):
    help = "Create or promote the configured PlacementPilot administrator."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            default=os.environ.get("PLACEMENT_ADMIN_USERNAME", ""),
            help="Administrator username (defaults to PLACEMENT_ADMIN_USERNAME).",
        )

    def handle(self, *args, **options):
        username = (options.get("username") or "").strip()
        initial_password = os.environ.get("PLACEMENT_ADMIN_PASSWORD", "")
        if not username:
            self.stdout.write("Skipping administrator provisioning: no username configured.")
            return

        user = User.objects.filter(username__iexact=username).first()
        if user is None:
            if not initial_password:
                raise CommandError(
                    "PLACEMENT_ADMIN_PASSWORD is required to create the initial administrator."
                )
            email = "placement.admin@placementpilot.local"
            if User.objects.filter(email__iexact=email).exists():
                email = ""
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name="PlacementPilot",
                last_name="Administrator",
                password=initial_password,
            )
            self.stdout.write("Created the configured administrator account.")
        else:
            self.stdout.write("Administrator account exists; its password will not be changed.")

        profile, _ = Profile.objects.get_or_create(user=user)
        if profile.role != "admin":
            profile.role = "admin"
            profile.save(update_fields=["role"])
        if not user.is_staff:
            user.is_staff = True
            user.save(update_fields=["is_staff"])

        self.stdout.write(self.style.SUCCESS(
            f"Administrator access is enabled for '{user.username}'."
        ))
