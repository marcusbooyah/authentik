# Generated by Django 3.2.4 on 2021-07-03 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentik_flows", "0021_flowstagebinding_invalid_response_action"),
    ]

    operations = [
        migrations.AlterField(
            model_name="flowstagebinding",
            name="invalid_response_action",
            field=models.TextField(
                choices=[
                    ("retry", "Retry"),
                    ("restart", "Restart"),
                    ("restart_with_context", "Restart With Context"),
                ],
                default="retry",
                help_text="Configure how the flow executor should handle an invalid response to a challenge. RETRY returns the error message and a similar challenge to the executor. RESTART restarts the flow from the beginning, and RESTART_WITH_CONTEXT restarts the flow while keeping the current context.",
            ),
        ),
    ]