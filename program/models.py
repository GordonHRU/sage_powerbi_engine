from django.db import models

# Create your models here.

class Program(models.Model):
    program_id = models.AutoField(primary_key=True)
    program_name = models.CharField(max_length=100, unique=True, db_index=True)
    workspace_id = models.CharField(max_length=100, db_index=True)
    report_name = models.CharField(max_length=100, db_index=True)
    dataset_id = models.CharField(max_length=100)
    method = models.CharField(max_length=100)
    output_name = models.CharField(max_length=100)
    output_type = models.CharField(max_length=100)
    sharepoint_site = models.CharField(max_length=100)
    sharepoint_path = models.CharField(max_length=255)
    filelocation = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.program_name} (ID: {self.program_id})"

    class Meta:
        verbose_name = 'Power BI Program'
        verbose_name_plural = 'Power BI Programs'
        ordering = ['-created_at']
        db_table = 'program'
        # indexes = [
        #     models.Index(fields=['workspace_id', 'report_name']),
        #     models.Index(fields=['created_at', 'updated_at']),
        #     models.Index(fields=['is_active', 'program_name']),
        # ]
        
