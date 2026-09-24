from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .forms import LoginForm, UserRegistrationForm, StudentRegistrationForm
from .models import User

def get_role_redirect_url(user):
    """
    FR-AUTH-03 Role-Based Routing:
    Admin -> /admin-portal/dashboard/
    Instructor -> /faculty/dashboard/
    Student -> /student/dashboard/
    """
    if user.role == User.Role.ADMIN or user.is_superuser:
        return '/admin-portal/dashboard/'
    elif user.role == User.Role.INSTRUCTOR:
        return '/faculty/dashboard/'
    else:
        return '/student/dashboard/'

def login_view(request):
    if request.user.is_authenticated:
        return redirect(get_role_redirect_url(request.user))

    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Reset last activity timestamp
            request.session['last_activity'] = None
            messages.success(request, f"Welcome back, {user.get_full_name_or_username()}!")
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(get_role_redirect_url(user))
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = LoginForm(request)

    return render(request, 'auth/login.html', {
        'form': form,
        'next': next_url,
    })

def register_view(request):
    if request.user.is_authenticated:
        return redirect(get_role_redirect_url(request.user))

    initial_role = request.GET.get('role', '').upper()
    if initial_role not in [User.Role.STUDENT, User.Role.INSTRUCTOR]:
        initial_role = User.Role.STUDENT

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            role_label = "Instructor" if user.role == User.Role.INSTRUCTOR else "Student"
            messages.success(request, f"Registration successful! Welcome to UnivLMS as {role_label}, {user.first_name}!")
            return redirect(get_role_redirect_url(user))
        else:
            messages.error(request, "Please correct the errors in the registration form.")
    else:
        form = UserRegistrationForm(initial={'role': initial_role})

    return render(request, 'auth/register.html', {
        'form': form,
        'selected_role': initial_role,
    })

@login_required
def role_redirect_view(request):
    return redirect(get_role_redirect_url(request.user))

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('accounts:login')

def demo_login_view(request, role):
    """
    Convenience endpoint for quickly logging in as demo users
    (Admin, Faculty, or Student) during local testing and presentation.
    """
    role_key = role.upper()
    if role_key == 'STUDENT':
        user = User.objects.filter(role='STUDENT', enrollments__isnull=False).distinct().first() or User.objects.filter(role='STUDENT').first()
    elif role_key == 'INSTRUCTOR':
        user = User.objects.filter(role='INSTRUCTOR', instructed_courses__isnull=False).distinct().first() or User.objects.filter(role='INSTRUCTOR').first()
    else:
        user = User.objects.filter(role='ADMIN').first() or User.objects.filter(is_superuser=True).first()

    if user:
        login(request, user)
        messages.success(request, f"Switched session to demo {user.role}: {user.get_full_name_or_username()}")
        return redirect(get_role_redirect_url(user))
    messages.error(request, f"No demo user found for role '{role}'. Please seed the database.")
    return redirect('accounts:login')
