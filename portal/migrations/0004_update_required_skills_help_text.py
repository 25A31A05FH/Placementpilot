from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("portal", "0003_remove_hackerrank")]

    operations = [
        migrations.AlterField(
            model_name="placementdrive",
            name="required_skills",
            field=models.CharField(
                blank=True,
                help_text="Comma-separated skills; all listed skills are treated as required",
                max_length=500,
            ),
        ),
    ]
