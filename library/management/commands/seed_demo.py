from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from library.models import Book, Loan

class Command(BaseCommand):
    help = "Add a few example books and lending records for a quick demo."
    def handle(self, *args, **options):
        samples = [
            ("The Alchemist", "Paulo Coelho", "Fiction", 3),
            ("Ikigai", "Héctor García & Francesc Miralles", "Wellbeing", 2),
            ("Atomic Habits", "James Clear", "Personal growth", 4),
            ("The Psychology of Money", "Morgan Housel", "Finance", 2),
            ("The Little Prince", "Antoine de Saint-Exupéry", "Classic", 2),
        ]
        for title, author, category, copies in samples:
            Book.objects.get_or_create(title=title, author=author, defaults={"category": category, "total_copies": copies})
        if not Loan.objects.exists():
            book = Book.objects.get(title="The Alchemist")
            Loan.objects.create(book=book, borrower_name="Aarav Sharma", issued_on=timezone.localdate()-timedelta(days=3), due_on=timezone.localdate()+timedelta(days=11))
            book = Book.objects.get(title="Ikigai")
            Loan.objects.create(book=book, borrower_name="Meera Joshi", issued_on=timezone.localdate()-timedelta(days=18), due_on=timezone.localdate()-timedelta(days=4))
        self.stdout.write(self.style.SUCCESS("Demo catalogue and lending records are ready."))
