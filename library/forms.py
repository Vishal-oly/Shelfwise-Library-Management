from datetime import timedelta
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Book, Loan

INPUT = "field-input"

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={"class": INPUT, "placeholder": "Your name"}))
    class Meta:
        model = User
        fields = ("first_name", "username", "password1", "password2")
        widgets = {"username": forms.TextInput(attrs={"class": INPUT, "placeholder": "Choose a username"})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "isbn", "category", "total_copies"]
        widgets = {"title": forms.TextInput(attrs={"class": INPUT, "placeholder": "e.g. The Alchemist"}),
                  "author": forms.TextInput(attrs={"class": INPUT, "placeholder": "Author name"}),
                  "isbn": forms.TextInput(attrs={"class": INPUT, "placeholder": "Optional"}),
                  "category": forms.TextInput(attrs={"class": INPUT, "placeholder": "e.g. Fiction"}),
                  "total_copies": forms.NumberInput(attrs={"class": INPUT, "min": 1})}

    def clean_total_copies(self):
        count = self.cleaned_data["total_copies"]
        if self.instance.pk and count < self.instance.active_loans:
            raise forms.ValidationError("Copies cannot be fewer than the books currently on loan.")
        return count

class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ["book", "borrower_name", "issued_on", "due_on"]
        widgets = {"book": forms.Select(attrs={"class": INPUT}),
                  "borrower_name": forms.TextInput(attrs={"class": INPUT, "placeholder": "Student / member name"}),
                  "issued_on": forms.DateInput(attrs={"class": INPUT, "type": "date"}),
                  "due_on": forms.DateInput(attrs={"class": INPUT, "type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["issued_on"].initial = timezone.localdate()
        self.fields["due_on"].initial = timezone.localdate() + timedelta(days=14)
        self.fields["book"].queryset = Book.objects.order_by("title")
        self.fields["book"].label_from_instance = lambda book: f"{book.title} ({book.available_copies} available)"

    def clean(self):
        cleaned = super().clean()
        book = cleaned.get("book")
        issued = cleaned.get("issued_on")
        due = cleaned.get("due_on")
        if book and book.available_copies < 1:
            self.add_error("book", "No copies of this book are currently available.")
        if issued and due and due < issued:
            self.add_error("due_on", "Due date cannot be before the issue date.")
        return cleaned
