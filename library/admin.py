from django.contrib import admin
from .models import Book, Loan

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "total_copies")
    search_fields = ("title", "author", "isbn")
    list_filter = ("category",)

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("book", "borrower_name", "issued_on", "due_on", "returned_at")
    search_fields = ("book__title", "borrower_name")
    list_filter = ("issued_on", "due_on", "returned_at")
