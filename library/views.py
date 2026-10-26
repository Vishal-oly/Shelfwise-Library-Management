from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_exempt
from .forms import BookForm, LoanForm, SignUpForm
from .models import Book, Loan

def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "library/home.html")

def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome! Your account is ready.")
        return redirect("dashboard")
    return render(request, "registration/signup.html", {"form": form})

@csrf_exempt
def preview_login(request):
    """Login endpoint for the embedded preview; middleware validates Origin."""
    if request.user.is_authenticated:
        return redirect("dashboard")
    next_url = request.POST.get("next") or request.GET.get("next", "")
    form = AuthenticationForm(request, data=request.POST or None)
    for field in form.fields.values():
        field.widget.attrs["class"] = "field-input"
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}, require_https=True):
            return redirect(next_url)
        return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, "registration/login.html", {"form": form, "next": next_url})

@csrf_exempt
def preview_logout(request):
    """Logout endpoint for embedded preview; middleware validates Origin."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    logout(request)
    return redirect("home")

@login_required
def dashboard(request):
    books = Book.objects.all()
    loans = Loan.objects.select_related("book")
    context = {
        "book_titles": books.count(),
        "copies": sum(book.total_copies for book in books),
        "active_loans": loans.filter(returned_at__isnull=True).count(),
        "overdue_count": loans.filter(returned_at__isnull=True, due_on__lt=timezone.localdate()).count(),
        "recent_loans": loans[:5],
        "low_stock": [book for book in books if book.available_copies <= 1][:4],
    }
    return render(request, "library/dashboard.html", context)

@login_required
def book_list(request):
    query = request.GET.get("q", "").strip()
    books = Book.objects.all()
    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query) | Q(category__icontains=query) | Q(isbn__icontains=query))
    return render(request, "library/book_list.html", {"books": books, "query": query})

@login_required
def book_create(request):
    form = BookForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        book = form.save()
        messages.success(request, f'“{book.title}” added to the catalogue.')
        return redirect("book_list")
    return render(request, "library/book_form.html", {"form": form, "title": "Add a book", "button": "Add book"})

@login_required
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    form = BookForm(request.POST or None, instance=book)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Book details updated.")
        return redirect("book_list")
    return render(request, "library/book_form.html", {"form": form, "title": "Edit book", "button": "Save changes"})

@login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        if book.loans.filter(returned_at__isnull=True).exists():
            messages.error(request, "Return active loans before removing this book.")
        else:
            book.delete()
            messages.success(request, "Book removed from catalogue.")
        return redirect("book_list")
    return render(request, "library/book_confirm_delete.html", {"book": book})

@login_required
def issue_list(request):
    loans = Loan.objects.select_related("book")
    status = request.GET.get("status", "active")
    if status == "returned":
        loans = loans.filter(returned_at__isnull=False)
    elif status == "all":
        pass
    else:
        status = "active"
        loans = loans.filter(returned_at__isnull=True)
    return render(request, "library/issue_list.html", {"loans": loans, "status": status})

@login_required
def issue_create(request):
    form = LoanForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Book issued successfully.")
        return redirect("issue_list")
    return render(request, "library/issue_form.html", {"form": form})

@login_required
def issue_return(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    if request.method == "POST" and loan.returned_at is None:
        loan.returned_at = timezone.now()
        loan.save(update_fields=["returned_at"])
        messages.success(request, f'“{loan.book.title}” marked as returned.')
    return redirect("issue_list")
