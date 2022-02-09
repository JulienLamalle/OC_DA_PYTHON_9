from tkinter.tix import Form
from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from reviews.models import Review, Ticket, UserFollows
from authentification.models import User


RATING_OPTIONS = [
    ("0", "0"),
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4"),
    ("5", "5")
  ]


class UserFollowsForm(forms.ModelForm):
  user = forms.CharField(widget=forms.TextInput(
    attrs={
      'class': 'form-control',
      'placeholder': "Nom d'utilisateur",
    }
  ), label="Nom d'utilisateur")

  class Meta:
    model = UserFollows
    fields = ['user']


class DeleteUserFollowsForm(forms.Form):
  delete_user_follow = forms.BooleanField(
    widget=forms.HiddenInput, initial=True)


class TicketForm(forms.ModelForm):
  class Meta:
    model = Ticket
    fields = ['title', 'description', 'image']

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    for field in self.fields:
      self.fields[field].widget.attrs.update({"class": "form-control my-3"})


class ReviewForm(forms.ModelForm):

  rating = forms.ChoiceField(
    widget=forms.RadioSelect, choices=RATING_OPTIONS, label="Note")

  class Meta:
    model = Review
    fields = ['rating', 'headline', 'body']

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    for field in self.fields:
      if field == "rating":
        self.fields[field].widget.attrs.update({"type": "radio"})
      else:
        self.fields[field].widget.attrs.update({"class": "form-control my-3"})


class DeleteTicketForm(forms.Form):
  delete_ticket_form = forms.BooleanField(
    widget=forms.HiddenInput, initial=True)


class DeleteReviewForm(forms.Form):
  delete_review_form = forms.BooleanField(
    widget=forms.HiddenInput, initial=True)
