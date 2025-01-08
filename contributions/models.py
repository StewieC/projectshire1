from django.db import models
from django.contrib.auth.models import User
from datetime import date
import uuid
from django.utils import timezone

# models.py
class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User)
    weekly_contribution = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=25)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_groups')
    join_code = models.CharField(max_length=8, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.join_code:
            self.join_code = str(uuid.uuid4())[:8]  # Generate unique join code
        super().save(*args, **kwargs)

    def add_member(self, user):
        self.members.add(user)

    def remove_member(self, user):
        self.members.remove(user)


    def __str__(self):
        return self.name

class PayoutCycle(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    payout_date = models.DateField(default=date.today)
    status = models.BooleanField(default=False)  # True if paid

    def __str__(self):
        return f"{self.recipient} - {self.payout_date}"

class Contribution(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    contribution_date = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.member} - {self.amount} on {self.contribution_date}"