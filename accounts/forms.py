from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from accounts.models import CustomUser

INPUT_CLASSES = (
    "w-full rounded-xl border border-cyan-400/20 bg-slate-900/80 px-4 py-3 "
    "text-sm text-slate-100 placeholder:text-slate-500 outline-none transition "
    "focus:border-cyan-400 focus:ring-4 focus:ring-cyan-400/20 "
    "disabled:cursor-not-allowed disabled:opacity-60"
)

PASSWORD_INPUT_CLASSES = f"{INPUT_CLASSES} pr-12"


class BaseRegistrationForm(UserCreationForm):
    role = None

    email = forms.EmailField(
        required=True,
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "class": INPUT_CLASSES,
                "placeholder": "your@mail.com",
                "autocomplete": "email",
                "maxlength": "254",
            },
        ),
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].max_length = 30
        self.fields["username"].help_text = ""
        self.fields["username"].widget = forms.TextInput(
            attrs={
                "class": INPUT_CLASSES,
                "placeholder": "User_123",
                "maxlength": "30",
                "autocomplete": "username",
            },
        )

        self.fields["password1"].widget = forms.PasswordInput(
            attrs={
                "class": PASSWORD_INPUT_CLASSES,
                "placeholder": "••••••••",
                "autocomplete": "new-password",
                "minlength": "8",
            },
        )
        self.fields["password2"].widget = forms.PasswordInput(
            attrs={
                "class": PASSWORD_INPUT_CLASSES,
                "placeholder": "••••••••",
                "autocomplete": "new-password",
                "minlength": "8",
            },
        )

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if len(username) > 30:
            raise forms.ValidationError(
                "Имя пользователя должно быть не длиннее 30 символов.",
            )
        return username

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if len(email) > 254:
            raise forms.ValidationError("Email должен быть не длиннее 254 символов.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = self.role
        if commit:
            user.save()
        return user


class OrganizerRegistrationForm(BaseRegistrationForm):
    role = "organizer"


class ParticipantRegistrationForm(BaseRegistrationForm):
    role = "participant"


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update(
            {
                "class": INPUT_CLASSES,
                "placeholder": "Имя пользователя",
                "autocomplete": "username",
                "maxlength": "30",
            },
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": PASSWORD_INPUT_CLASSES,
                "placeholder": "Пароль",
                "autocomplete": "current-password",
            },
        )
