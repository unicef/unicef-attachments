# Generated by Django 3.2.6 on 2022-05-12 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('unicef_attachments', '0006_auto_20211123_2120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='hyperlink',
            field=models.CharField(blank=True, default='', max_length=1000, verbose_name='Hyperlink'),
        ),
    ]
