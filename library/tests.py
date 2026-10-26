from datetime import timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Book, Loan

class LibraryFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="librarian", password="TestPass123!", first_name="Riya")
        self.book = Book.objects.create(title="Test Book", author="A. Writer", total_copies=1)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_staff_can_add_catalogue_book(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("book_create"), {"title": "New Book", "author": "Writer", "isbn": "", "category": "Fiction", "total_copies": 2})
        self.assertRedirects(response, reverse("book_list"))
        self.assertTrue(Book.objects.filter(title="New Book").exists())

    def test_issue_decreases_available_copies_and_return_restores_it(self):
        self.client.force_login(self.user)
        due = timezone.localdate() + timedelta(days=7)
        response = self.client.post(reverse("issue_create"), {"book": self.book.pk, "borrower_name": "A Reader", "issued_on": timezone.localdate().isoformat(), "due_on": due.isoformat()})
        self.assertRedirects(response, reverse("issue_list"))
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 0)
        loan = Loan.objects.get(book=self.book)
        self.client.post(reverse("issue_return", args=[loan.pk]))
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 1)

    def test_cannot_issue_when_no_copy_available(self):
        self.client.force_login(self.user)
        Loan.objects.create(book=self.book, borrower_name="Already borrowing", due_on=timezone.localdate() + timedelta(days=3))
        response = self.client.post(reverse("issue_create"), {"book": self.book.pk, "borrower_name": "Second reader", "issued_on": timezone.localdate().isoformat(), "due_on": (timezone.localdate() + timedelta(days=7)).isoformat()})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Loan.objects.filter(book=self.book).count(), 1)
