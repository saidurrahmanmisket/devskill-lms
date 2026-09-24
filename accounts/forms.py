import re
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()

def validate_strong_password(password):
    """
    FR-AUTH-02: Strong password criteria (min 8 characters, alphanumeric/special).
    """
    if len(password) < 8:
        raise ValidationError(_("Password must be at least 8 characters long."))
    if not re.search(r'[A-Za-z]', password):
        raise ValidationError(_("Password must contain at least one letter."))
    if not re.search(r'\d', password):
        raise ValidationError(_("Password must contain at least one digit."))
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=~/\\\[\]]', password):
        raise ValidationError(_("Password must contain at least one special character."))

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username, Email or Academic ID',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        })
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            if '@' in username:
                try:
                    user_obj = User.objects.filter(email__iexact=username).first()
                    if user_obj:
                        username = user_obj.username
                except Exception:
                    pass

            from django.contrib.auth import authenticate
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

class UserRegistrationForm(forms.ModelForm):
    ROLE_CHOICES = [
        (User.Role.STUDENT, _('Student (Access courses, submit assignments & view grades)')),
        (User.Role.INSTRUCTOR, _('Instructor / Faculty (Publish courses, author curricula & grade submissions)')),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'role-radio-input'}),
        initial=User.Role.STUDENT,
        label=_("Register As"),
        help_text=_("Choose whether you are enrolling as an active Student or teaching Faculty.")
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
        validators=[validate_strong_password],
        help_text=_("Min 8 characters with letters, numbers, and special characters.")
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
        label=_("Confirm Password")
    )

    class Meta:
        model = User
        fields = ['role', 'username', 'email', 'first_name', 'last_name', 'academic_id']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. j_doe or prof_smith'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@univ.edu'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Doe'}),
            'academic_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. STU-101 or FAC-202'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', _("Passwords do not match."))
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        selected_role = self.cleaned_data.get('role', User.Role.STUDENT)
        # Only allow STUDENT or INSTRUCTOR self-registration
        if selected_role in [User.Role.STUDENT, User.Role.INSTRUCTOR]:
            user.role = selected_role
            if selected_role == User.Role.INSTRUCTOR:
                user.is_staff = True
        else:
            user.role = User.Role.STUDENT
        if commit:
            user.save()
        return user


# Backwards compatibility alias
StudentRegistrationForm = UserRegistrationForm

class CSVImportForm(forms.Form):
    csv_file = forms.FileField(
        label=_("Roster CSV File"),
        help_text=_("CSV format: First Name, Last Name, Email, Role (ADMIN/INSTRUCTOR/STUDENT), Academic ID"),
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'})
    )
