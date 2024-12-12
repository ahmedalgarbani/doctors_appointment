from django.db import models

class Services(models.Model):
    hospital = models.ForeignKey('hospitals.Hospitals', on_delete=models.CASCADE)
    service_name = models.CharField(max_length=100)

class Payments(models.Model):
    booking = models.ForeignKey('bookings.Bookings', on_delete=models.CASCADE)
    user = models.ForeignKey('users.Users', on_delete=models.CASCADE)
    service = models.ForeignKey(Services, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
