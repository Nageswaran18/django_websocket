from django.contrib import admin
from django.apps import apps

# Get all models in the current app
app_models = apps.get_app_config("chat_app").get_models()

# Dynamically register all models
for model in app_models:
    class GenericAdmin(admin.ModelAdmin):
        list_display = [field.name for field in model._meta.fields]  # Display all fields
        search_fields = [field.name for field in model._meta.fields if field.get_internal_type() in ["CharField", "TextField"]]  # Searchable fields
        list_filter = [field.name for field in model._meta.fields if field.get_internal_type() in ["BooleanField", "DateField", "DateTimeField", "ForeignKey"]]  # Add filters for specific field types

    admin.site.register(model, GenericAdmin)
