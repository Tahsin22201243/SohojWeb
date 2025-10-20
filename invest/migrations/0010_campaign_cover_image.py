from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invest', '0009_campaign_risk_grade'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='campaign_covers/'),
        ),
    ]
