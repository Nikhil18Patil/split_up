import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator  # Import validators


class Expense(models.Model):
    SPLIT_METHOD_CHOICES = [
        ('equal', 'Equal'),
        ('exact', 'Exact'),
        ('percentage', 'Percentage'),
    ]
    
    expense_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)  # Set as primary key
    description = models.CharField(max_length=255, blank=False, null=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    split_method = models.CharField(max_length=20, choices=SPLIT_METHOD_CHOICES, blank=False, null=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_expenses")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.description} - {self.amount} ({self.split_method})"

class Participant(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('settled', 'Settled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="participant_expenses")
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name="participants")
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])  # Validators for percentage
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"Participant: {self.user.username}, Status: {self.status}"  # Changed to username since we are not using email
