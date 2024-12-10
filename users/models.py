# from django.db import models
# from django.contrib.auth.models import AbstractUser
# #----ahmed----develop
# class User(AbstractUser):
#     phone_number = models.CharField(max_length=15, blank=True, null=True)
#     address = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return self.username


# class Role(models.Model):
#     name = models.CharField(max_length=50, unique=True)
#     description = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return self.name


# class Permission(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     description = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return self.name


# class RolePermission(models.Model):
#     role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permissions")
#     permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ('role', 'permission')

#     def __str__(self):
#         return f"{self.role.name} - {self.permission.name}"
