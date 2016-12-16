from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from django.contrib.auth import get_user_model
from utils.mixins.form_mixins import CrispyFormMixin
from crispy_forms.layout import Layout

Account = get_user_model()


class InviteUserForm(forms.Form):
    email = forms.EmailField(max_length=100)


class LoginForm(AuthenticationForm, CrispyFormMixin):
    submit_value = "Sign In"


class ResetPassword(PasswordResetForm, CrispyFormMixin):
    submit_value = "Reset Password"


class SetPassword(SetPasswordForm, CrispyFormMixin):
    submit_value = "Save Password"


class AccountCreationForm(forms.ModelForm, CrispyFormMixin):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password (again)', widget=forms.PasswordInput)

    house_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    submit_value = "Create Account"

    def __init__(self, *args, **kwargs):
        super(AccountCreationForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2'
        )

    class Meta:
        model = Account
        fields = ('email', 'first_name', 'last_name',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(AccountCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class AccountChangeForm(forms.ModelForm, CrispyFormMixin):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput, required=False)

    submit_value = "Save"

    class Meta:
        model = Account
        fields = ['email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial')
        if initial:
            self.current_user = initial.pop('current_user')
        super(AccountChangeForm, self).__init__(*args, **kwargs)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        try:
            user = Account.objects.get(email__iexact=self.cleaned_data['email'])
            if user != self.current_user:
                raise forms.ValidationError("This email address is already in use.")
        except Account.DoesNotExist:
            pass
        return self.cleaned_data['email']

    def clean(self):
        return self.cleaned_data


class AccountAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Account
        fields = ['email', 'first_name', 'last_name', 'password', 'is_active', 'is_admin']

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]
