from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm
from django.contrib.auth import get_user_model
from django import forms


class UserLoginForm(AuthenticationForm):
  def __init__(self, *args, **kwargs):
    super(UserLoginForm, self).__init__(*args, **kwargs)

  username = UsernameField(widget=forms.TextInput(
    attrs={'class': 'form-control', 'placeholder': "Nom d'utilisateur"}), label='Nom d\'utilisateur')
  password = forms.CharField(widget=forms.PasswordInput(
    attrs={
      'class': 'form-control',
      'placeholder': 'Mot de passe',
    }
  ), label='Mot de passe')


class SignupForm(UserCreationForm):
  username = forms.Field(widget=forms.TextInput(
      attrs={'class': 'form-control'}), label="Nom d'utilisateur")
  password1 = forms.Field(widget=forms.PasswordInput(
      attrs={'class': 'form-control'}), label="Mot de passe")
  password2 = forms.Field(widget=forms.PasswordInput(
      attrs={'class': 'form-control'}), label="Confirmation du mot de passe")

  class Meta:
    model = get_user_model()
    fields = ('username', 'password1', 'password2')
