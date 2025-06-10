from django.db import models

# Create your models here.

class Program(models.Model):
    program_id = models.AutoField(primary_key=True)
    program_name = models.CharField(max_length=100, unique=True)
    workspace_id = models.CharField(max_length=100)
    report_name = models.CharField(max_length=100)
    dataset_id = models.CharField(max_length=100)
    method = models.CharField(max_length=100)
    output_name = models.CharField(max_length=100)
    output_type = models.CharField(max_length=100)
    sharepoint_site = models.CharField(max_length=100)
    sharepoint_path = models.CharField(max_length=255)
    filelocation = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
