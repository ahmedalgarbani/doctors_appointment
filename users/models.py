from django.db import models

class Roles(models.Model):
    role_name = models.CharField(max_length=100)
    role_desc = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.role_name

class Permissions(models.Model):
    permission_name = models.CharField(max_length=100)
    permission_code = models.CharField(max_length=50)

    def __str__(self):
        return self.permission_name

class RolePermissions(models.Model):
    role = models.ForeignKey(Roles, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permissions, on_delete=models.CASCADE)

class Users(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.ForeignKey(Roles, on_delete=models.CASCADE)

    def __str__(self):
        return self.username
