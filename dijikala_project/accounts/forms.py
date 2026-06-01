import re
from django import forms
from django.core.exceptions import ValidationError
from .models import User
from stores.models import Store
from django.utils.text import slugify

def validate_phone(value):
    if not re.match(r'^09\d{9}$', value):
        raise ValidationError("شماره تماس باید با 09 شروع شود و دقیقاً 11 رقم باشد.")

def validate_password_strength(value):
    if len(value) < 8:
        raise ValidationError("رمز عبور باید حداقل ۸ کاراکتر باشد.")
    if not re.match(r'^[A-Za-z0-9]+$', value):
        raise ValidationError("رمز عبور فقط شامل حروف انگلیسی و اعداد باشد.")

def validate_store_name(value):
    if not re.match(r'^[A-Za-z0-9 ]+$', value):
        raise ValidationError("نام فروشگاه فقط شامل حروف انگلیسی و اعداد باشد (بدون _ یا کاراکتر خاص).")

class BaseSignupForm(forms.ModelForm):
    phone_number = forms.CharField(validators=[validate_phone])
    password = forms.CharField(widget=forms.PasswordInput, validators=[validate_password_strength])

    class Meta:
        model = User
        fields = ['phone_number', 'name', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['phone_number']
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class CustomerSignupForm(BaseSignupForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'user'
        if commit:
            user.save()
        return user

class SellerSignupForm(BaseSignupForm):
    store_name = forms.CharField(max_length=200, validators=[validate_store_name])

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'seller'
        if commit:
            user.save()
            Store.objects.create(
                name=self.cleaned_data['store_name'],
                owner=user,
                slug=slugify(self.cleaned_data['store_name'])
            )
        return user

class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'custom-input'})

class ProfileUpdateForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'avatar']

class AddBalanceForm(StyledFormMixin, forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=0, min_value=1)
