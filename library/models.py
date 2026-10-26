from django.db import models
from django.utils import timezone

class Book(models.Model):
    title = models.CharField(max_length=180)
    author = models.CharField(max_length=140)
    isbn = models.CharField(max_length=20, blank=True)
    category = models.CharField(max_length=80, blank=True)
    total_copies = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    @property
    def active_loans(self):
        return self.loans.filter(returned_at__isnull=True).count()

    @property
    def available_copies(self):
        return max(0, self.total_copies - self.active_loans)

    def __str__(self):
        return f"{self.title} — {self.author}"

class Loan(models.Model):
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="loans")
    borrower_name = models.CharField(max_length=140)
    issued_on = models.DateField(default=timezone.localdate)
    due_on = models.DateField()
    returned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-issued_on", "-id"]

    @property
    def is_overdue(self):
        return self.returned_at is None and self.due_on < timezone.localdate()

    def __str__(self):
        return f"{self.book.title} — {self.borrower_name}"
