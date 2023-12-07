import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import migrations
from django.core.management.sql import emit_post_migrate_signal

logger = logging.getLogger(__name__)


def generate_admin_moder(apps, schema_editor):
    User = get_user_model()
    admin = User.objects.create_superuser(email="admin@admin.com", username="admin", password="admin")
    moderator = User.objects.create_superuser(email="moderator@moderator.com", username="moderator", password="moderator")
    moderator.is_superuser = False
    moderator.save()

    moder_group = Group.objects.create(name="moderators")
    moderator.groups.add(moder_group)
    # person_read = Permission.objects.get(codename='view_person')
    # person_delete = Permission.objects.get(codename='delete_person')
    # moder_group.permissions.add(person_read)
    # moder_group.permissions.add(person_delete)


class Migration(migrations.Migration):
    dependencies = [("profiles", "0001_initial")]

    # emit_post_migrate_signal(2, False, 'default')

    operations = [migrations.RunPython(generate_admin_moder)]

