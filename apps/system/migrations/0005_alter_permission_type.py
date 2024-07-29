# Generated by Django 3.2.12 on 2024-07-29 02:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0004_auto_20240605_1011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(10, '模块'), (20, '页面'), (30, '接口')], default=30, verbose_name='类型'),
        ),
    ]
