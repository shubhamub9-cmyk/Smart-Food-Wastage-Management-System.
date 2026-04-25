# Generated manually — fix logged_by CharField→ForeignKey migration for SQLite
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_canteen_userprofile_canteen'),
        ('waste', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Step 1: Add canteen FK
        migrations.AddField(
            model_name='wastelog',
            name='canteen',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='waste_logs', to='users.canteen'),
        ),
        # Step 2: Remove old logged_by CharField
        migrations.RemoveField(
            model_name='wastelog',
            name='logged_by',
        ),
        # Step 3: Add new logged_by as ForeignKey
        migrations.AddField(
            model_name='wastelog',
            name='logged_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='waste_logs', to=settings.AUTH_USER_MODEL),
        ),
    ]
