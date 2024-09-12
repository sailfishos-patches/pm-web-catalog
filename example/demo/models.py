from __future__ import unicode_literals

from django.db import models
from django.core.files.base import ContentFile
from multiselectfield import MultiSelectField
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
import re

from example.demo.filehandler import *


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length):
        if self.exists(name):
            self.delete(name)
        return name


class ProjectsModel(models.Model):
    def validate_name(text):
        if not re.search(r'^[a-zA-Z][a-zA-Z0-9_.+-]*[a-zA-Z0-9]$', text):
            raise ValidationError('Name string "%s" does not match RegEx "^[a-zA-Z][a-zA-Z0-9_.+-]*[a-zA-Z0-9]$"!' % text)

    category_default = "other"
    category_choices = (
        ("browser", "Browser"),
        ("camera", "Camera"),
        ("calendar", "Calendar"),
        ("clock", "Clock"),
        ("contacts", "Contacts"),
        ("email", "Email"),
        ("gallery", "Gallery"),
        ("homescreen", "Homescreen"),
        ("keyboard", "Keyboard"),
        ("media", "Media"),
        ("messages", "Messages"),
        ("phone", "Phone"),
        ("settings", "Settings"),
        ("silica", "Silica"),
        ("other", "Other")
    )

    description = models.CharField(max_length=4096, blank=False)
    last_updated = models.DateTimeField(auto_now_add=True)
    name = models.CharField(blank=False, unique=True, max_length=255, validators=[validate_name])
    display_name = models.CharField(blank=False, max_length=255)
    category = models.CharField(blank=False, max_length=255, choices=category_choices, default=category_default)
    author = models.CharField(blank=True, max_length=255)
    rating = models.IntegerField(blank=True, default=0)
    total_activations = models.PositiveIntegerField(blank=True, default=0)
    discussion = models.CharField(blank=True, max_length=255)
    donations = models.CharField(blank=True, max_length=255)
    sources = models.CharField(blank=True, max_length=255)


extensions = ('.tar.gz', '.tar.xz', '.tar.bz2', '.zip')

maximum_file_size = 1024 * 1024 * 16


class FilesModel(models.Model):
    def upload_path_handler(instance, filename):
        for i in extensions:
            if filename.endswith(i):
                ext = i
        return 'documents/{author}-{project}-{version}{ext}'.format(author=instance.author, project=instance.project, version=instance.version, ext=ext)

    fs = OverwriteStorage()

    compatible_choices_default = "4.4.0.72"
    compatible_choices = (
        ("4.5.0.19", "4.5.0.19"),
        ("4.5.0.18", "4.5.0.18"),
        ("4.5.0.16", "4.5.0.16"),
        ("4.4.0.72", "4.4.0.72"),
        ("4.4.0.68", "4.4.0.68"),
        ("4.4.0.64", "4.4.0.64"),
        ("4.4.0.58", "4.4.0.58"),
        ("4.3.0.15", "4.3.0.15"),
        ("4.3.0.12", "4.3.0.12"),
        ("4.2.0.21", "4.2.0.21"),
        ("4.2.0.19", "4.2.0.19"),
        ("4.1.0.24", "4.1.0.24"),
        ("4.1.0.23", "4.1.0.23"),
        ("4.0.1.48", "4.0.1.48"),
        ("4.0.1.45", "4.0.1.45"),
        ("3.4.0.24", "3.4.0.24"),
        ("3.4.0.22", "3.4.0.22"),
        ("3.3.0.16", "3.3.0.16"),
        ("3.3.0.14", "3.3.0.14"),
        ("3.2.1.20", "3.2.1.20"),
        ("3.2.1.19", "3.2.1.19"),
        ("3.2.0.14", "3.2.0.14"),
        ("3.2.0.12", "3.2.0.12"),
        ("3.1.0.12", "3.1.0.12"),
        ("3.1.0.11", "3.1.0.11"),
        ("3.0.3.10", "3.0.3.10"),
        ("3.0.3.9",  "3.0.3.9"),
        ("3.0.3.8",  "3.0.3.8"),
        ("3.0.2.8",  "3.0.2.8"),
        ("3.0.1.14", "3.0.1.14"),
        ("3.0.1.13", "3.0.1.13"),
        ("3.0.1.11", "3.0.1.11"),
        ("3.0.0.11", "3.0.0.11"),
        ("3.0.0.8",  "3.0.0.8"),
        ("3.0.0.5",  "3.0.0.5"),
        ("3.0.0.11", "3.0.0.11"),
        ("2.2.1.23", "2.2.1.23"),
        ("2.2.1.20", "2.2.1.20"),
        ("2.2.1.19", "2.2.1.19"),
        ("2.2.1.18", "2.2.1.18"),
        ("2.2.0.29", "2.2.0.29"),
        ("2.1.4.15", "2.1.4.15"),
        ("2.1.4.14", "2.1.4.14"),
        ("2.1.4.13", "2.1.4.13"),
        ("2.1.4.12", "2.1.4.12"),
        ("2.1.3.7",  "2.1.3.7"),
        ("2.1.3.5",  "2.1.3.5"),
        ("2.1.3.3",  "2.1.3.3"),
        ("2.1.2.3",  "2.1.2.3"),
        ("2.1.1.26", "2.1.1.26"),
        ("2.1.1.24", "2.1.1.24"),
        ("2.1.1.25", "2.1.1.25"),
        ("2.1.1.23", "2.1.1.23"),
        ("2.1.1.12", "2.1.1.12"),
        ("2.1.0.11", "2.1.0.11"),
        ("2.1.0.10", "2.1.0.10"),
        ("2.1.0.9",  "2.1.0.9"),
        ("2.0.5.6",  "2.0.5.6"),
        ("2.0.4.14", "2.0.4.14"),
        ("2.0.4.13", "2.0.4.13"),
        ("2.0.3.14", "2.0.3.14"),
        ("2.0.3.11", "2.0.3.11"),
        ("2.0.2.51", "2.0.2.51"),
        ("2.0.2.48", "2.0.2.48"),
        ("2.0.2.47", "2.0.2.47"),
        ("2.0.2.45", "2.0.2.45"),
        ("2.0.2.43", "2.0.2.43"),
        ("2.0.1.11", "2.0.1.11"),
        ("2.0.1.9",  "2.0.1.9"),
        ("2.0.1.7",  "2.0.1.7"),
        ("2.0.0.10", "2.0.0.10"),
        ("1.1.9.30", "1.1.9.30"),
        ("1.1.9.28", "1.1.9.28"),
        ("1.1.9.27", "1.1.9.27"),
        ("1.1.9.24", "1.1.9.24"),
        ("1.1.9.23", "1.1.9.23")
      )

    def validate_file_type(upload):
        if not upload.name.lower().endswith(extensions):
            raise ValidationError('Unsupported file extension in: %s' % upload.name.lower())
        if upload.file.size > maximum_file_size:
            raise ValidationError('File is too large. Maximum allowed size is 16MB')
        storage = FileSystemStorage()
        f = storage.save('tmp/%s' % upload.name, ContentFile(upload.file.read()))
        verified, message, content = ArchiveVerifier(f).is_valid()
        if storage.exists(f):
            storage.delete(f)
        if not verified:
            raise ValidationError(message)

    def validate_version(ver):
        if not re.search(r'^[0-9]+\.[0-9]+\.[0-9]+$', ver):
            raise ValidationError('Version string "%s" does not match EnhancedRegEx (ERE) "^[0-9]+\.[0-9]+\.[0-9]+$" (e.g, 1.2.3)!' % ver)

    uploaded = models.DateTimeField(auto_now_add=True)
    author = models.CharField(blank=True, max_length=255)
    project = models.CharField(blank=True, max_length=255)
    document = models.FileField(storage=fs, upload_to=upload_path_handler, validators=[validate_file_type])
    version = models.CharField(blank=False, max_length=15, validators=[validate_version])
    compatible = MultiSelectField(blank=False, max_length=255, choices=compatible_choices, default=compatible_choices_default)
    activations = models.PositiveIntegerField(blank=True, default=0)
    changelog = models.CharField(max_length=512, blank=True)


class ScreenshotsModel(models.Model):
    def upload_screenshot_handler(instance, filename):
        return 'screenshots/{project}-{filename}'.format(project=instance.project, filename=filename)

    def validate_content_type(upload):
        if not upload.file.content_type == 'image/png':
            raise ValidationError('File content-type "%s" doesnt match image/png' % upload.file.content_type)
        if upload.file.size > maximum_file_size:
            raise ValidationError('File is too large. Maximum allowed size is 16MB')

    fs = OverwriteStorage()
    screenshot = models.FileField(blank=True, storage=fs, upload_to=upload_screenshot_handler, validators=[validate_content_type])
    filename = models.CharField(blank=True, max_length=255)
    project = models.CharField(blank=True, max_length=255)
