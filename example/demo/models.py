from __future__ import unicode_literals

from django.db import models
from multiselectfield import MultiSelectField
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
import re



class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length):
        if self.exists(name):
            self.delete(name)
        return name


class ProjectsModel(models.Model):
    def validate_name(text):
        if not re.match(r'^([\w-]*)$', text):
            raise ValidationError('Name string "%s" doesnt match template "a-ZA-Z0-9-_"' % text)

    category_default = "others"
    category_choices = (
        ("homescreen", "homescreen"),
        ("browser", "browser"),
        ("camera", "camera"),
        ("calendar", "calendar"),
        ("clock", "clock"),
        ("contacts", "contacts"),
        ("email", "email"),
        ("gallery", "gallery"),
        ("homescreen", "homescreen"),
        ("media", "media"),
        ("messages", "messages"),
        ("phone", "phone"),
        ("settings", "settings"),
        ("others", "others")
    )

    description = models.CharField(max_length=4096, blank=False)
    last_updated = models.DateTimeField(auto_now=True)
    name = models.CharField(blank=False, unique=True, max_length=255, validators=[validate_name])
    display_name = models.CharField(blank=False, max_length=255)
    category = models.CharField(blank=False, max_length=255, choices=category_choices, default=category_default)
    author = models.CharField(blank=True, max_length=255)
    rating = models.IntegerField(blank=True, default=0)
    total_activations = models.PositiveIntegerField(blank=True, default=0)


class FilesModel(models.Model):
    def upload_path_handler(instance, filename):
        return 'documents/{author}-{project}-{version}'.format(author=instance.author, project=instance.project, version=instance.version)

    fs = OverwriteStorage()

    compatible_choices_default = "2.0.4.14"
    compatible_choices = (
        ("1.1.9.30", "1.1.9.30"),
        ("2.0.2.51", "2.0.2.51"),
        ("2.0.4.14", "2.0.4.14"),
        ("2.0.5.4", "2.0.5.4")
    )

    def validate_file_type(upload):
        if not upload.name.lower().endswith(('.tar.gz', '.tar.xz', '.tar.bz2', '.zip')):
            raise ValidationError('Unsupported file extension in: %s' % upload.name.lower())

    def validate_version(ver):
        if not re.match(r'^(\d+)\.(\d+)\.(\d+)$', ver):
            raise ValidationError('Version string "%s" doesnt match template "0-9.0-9.0-9", like 1.2.3' % ver)

    uploaded = models.DateTimeField(auto_now=True)
    author = models.CharField(blank=True, max_length=255)
    project = models.CharField(blank=True, max_length=255)
    document = models.FileField(storage=fs, upload_to=upload_path_handler, validators=[validate_file_type])
    version = models.CharField(blank=False, unique=True, max_length=15, validators=[validate_version])
    compatible = MultiSelectField(blank=False, max_length=255, choices=compatible_choices, default=compatible_choices_default)
    activations = models.PositiveIntegerField(blank=True, default=0)
