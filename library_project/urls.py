from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from library import views

if settings.SHELFWISE_PREVIEW:
    # The preview proxy may suppress CSRF cookies; the preview-only middleware
    # enforces exact HTTPS Origin/Host matching for these POST endpoints.
    login_view = views.preview_login
    logout_view = views.preview_logout
else:
    login_view = auth_views.LoginView.as_view(template_name="registration/login.html")
    logout_view = auth_views.LogoutView.as_view()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("books/", views.book_list, name="book_list"),
    path("books/add/", views.book_create, name="book_create"),
    path("books/<int:pk>/edit/", views.book_update, name="book_update"),
    path("books/<int:pk>/delete/", views.book_delete, name="book_delete"),
    path("issues/", views.issue_list, name="issue_list"),
    path("issues/new/", views.issue_create, name="issue_create"),
    path("issues/<int:pk>/return/", views.issue_return, name="issue_return"),
]
