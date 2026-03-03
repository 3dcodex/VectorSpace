# Generated migration for users app

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_email_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='role',
            field=models.CharField(
                choices=[('USER', 'User'), ('CREATOR', 'Creator'), ('MENTOR', 'Mentor'), ('RECRUITER', 'Recruiter'), ('ADMIN', 'Admin')],
                default='USER',
                max_length=20
            ),
        ),
    ]
