# Generated by Django 3.2.6 on 2023-01-19 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('unicef_attachments', '0007_alter_attachment_hyperlink'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
