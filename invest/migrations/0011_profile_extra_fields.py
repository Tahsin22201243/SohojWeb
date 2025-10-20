from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invest', '0010_campaign_cover_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='birthdate',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='country',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='city',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='postal_code',
            field=models.CharField(max_length=20, blank=True),
        ),
    ]
