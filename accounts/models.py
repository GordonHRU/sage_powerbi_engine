from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(
        max_length=100, 
        unique=True,
        help_text='Required. 100 characters or fewer.'
    )
    email = models.EmailField(
        unique=True,
        help_text='Required. A valid email address.'
    )
    password = models.CharField(max_length=128, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user can log in.'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        db_table = 'accounts_user'

    def __str__(self):
        return self.username

class Group(models.Model):
    group_id = models.AutoField(primary_key=True)
    group_name = models.CharField(
        max_length=100, 
        unique=True,
        help_text='Required. 100 characters or fewer.'
    )
    user_id = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='group',
        help_text='The user who created this group.'
    )
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.group_name

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'
        ordering = ['-created_at']
        db_table = 'accounts_group'