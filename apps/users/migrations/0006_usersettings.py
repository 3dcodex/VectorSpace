from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_userprofile_artstation_userprofile_github_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_visible', models.BooleanField(default=True)),
                ('two_factor_enabled', models.BooleanField(default=False)),
                ('email_job_updates', models.BooleanField(default=True)),
                ('email_marketplace_sales', models.BooleanField(default=True)),
                ('email_competition_announcements', models.BooleanField(default=True)),
                ('email_community_replies', models.BooleanField(default=True)),
                ('notif_direct_messages', models.BooleanField(default=True)),
                ('notif_comments', models.BooleanField(default=True)),
                ('notif_follower_activity', models.BooleanField(default=True)),
                ('public_profile', models.BooleanField(default=True)),
                ('hide_email', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
