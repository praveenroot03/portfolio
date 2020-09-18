# Generated by Django 2.2.16 on 2020-09-13 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainPage', '0003_auto_20200913_0505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='about',
            name='image',
            field=models.ImageField(upload_to='mainPage/about_image'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='link',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='contact',
            name='types',
            field=models.CharField(choices=[('fa-linkedin', 'Linkedin'), ('fa-instagram', 'Instagram'), ('fa-github', 'Github'), ('fa-twitter', 'Twitter'), ('fa-envelope', 'Email')], max_length=20, primary_key=True, serialize=False),
        ),
    ]
