# Generated migration for marketplace app

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.AddField(
            model_name='asset',
            name='file_format',
            field=models.CharField(blank=True, choices=[('OBJ', 'OBJ'), ('FBX', 'FBX'), ('BLEND', 'Blender'), ('GLTF', 'GLTF'), ('GLB', 'GLB'), ('MAX', '3DS Max'), ('MA', 'Maya'), ('C4D', 'Cinema 4D')], max_length=10),
        ),
        migrations.AddField(
            model_name='asset',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='asset',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='marketplace.category'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='file',
            field=models.FileField(upload_to='asset_files/'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='preview_image',
            field=models.ImageField(blank=True, null=True, upload_to='asset_thumbnails/'),
        ),
    ]
