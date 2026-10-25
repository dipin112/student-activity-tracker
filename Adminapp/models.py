from django.db import models


class Activity(models.Model):
    """A single activity logged by a student."""

    name = models.CharField(max_length=100)
    activity = models.CharField(max_length=150)
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'activities'

    def __str__(self):
        return f'{self.name} - {self.activity}'
