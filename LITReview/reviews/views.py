from csv import excel_tab
from multiprocessing import get_context
from operator import ge
from re import search, template
from urllib import request
from itertools import chain
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib.auth import get_user_model
from django.db.models import Q, Value, CharField

from reviews.forms import DeleteReviewForm, DeleteTicketForm, ReviewForm, TicketForm, DeleteUserFollowsForm, UserFollowsForm
from reviews.models import Ticket, Review, UserFollows

User = get_user_model()


class FluxView(LoginRequiredMixin, View):
  model = Ticket
  template_name = 'reviews/flux.html'

  def get(self, request):
    users_followed = UserFollows.objects.filter(
      user=self.request.user)
    all_reviews = Review.objects.all()

    reviews_of_followed_users_tickets_id = [
        review.id for review in all_reviews
        if review.ticket.user in [user.followed_user for user in users_followed]
    ]

    reviews_of_followed_users_tickets = Review.objects.filter(
      pk__in=reviews_of_followed_users_tickets_id)

    tickets = self.model.objects.filter(
        user__in=list(
            chain([user.followed_user for user in users_followed], [self.request.user]))
    )

    reviews = Review.objects.filter(
        user__in=list(
            chain([user.followed_user for user in users_followed], [self.request.user])))

    id_of_reviews_on_request_user_tickets = [
      review.id for review in all_reviews
      if review.ticket.user == self.request.user
    ]

    reviews_on_request_user_tickets = Review.objects.filter(
      pk__in=id_of_reviews_on_request_user_tickets)
    
    reviews_on_request_user_tickets_annotated = reviews_on_request_user_tickets.annotate(
      content_type=Value('REVIEW', CharField()))
    reviews_of_followed_users_tickets_annotated = reviews_of_followed_users_tickets.annotate(
      content_type=Value('REVIEW', CharField()))
    tickets_annotated = tickets.annotate(
        content_type=Value('TICKET', CharField()))
    reviews_annotated = reviews.annotate(
        content_type=Value('REVIEW', CharField()))

    set_reviews = set(
        list(chain(reviews_annotated, reviews_of_followed_users_tickets_annotated, reviews_on_request_user_tickets_annotated)))

    posts = list(sorted(chain(tickets_annotated, set_reviews),
                        key=lambda post: post.time_created,
                        reverse=True))
    return render(request, self.template_name, {'posts': posts})


class UserFollowsView(LoginRequiredMixin, View):
  model = UserFollows
  template_name = 'reviews/user_follows.html'
  form_class = UserFollowsForm
  delete_form = DeleteUserFollowsForm

  def get(self, request):
    user_following = self.model.objects.filter(user=request.user)
    user_followed_by = self.model.objects.filter(followed_user=request.user)
    query = request.GET.get('user')
    search_result = []
    if query is not None:
      try:
        search_result = User.objects.all().filter(
          username__icontains=query).exclude(Q(username=request.user.username) | Q(username__in=[str(user.followed_user) for user in user_following]))
      except User.DoesNotExist:
        search_result = []
    return render(request, self.template_name, context={'form': self.form_class(), 'delete_form': self.delete_form(), 'user_following': user_following, 'user_followed_by': user_followed_by, 'search_result': search_result})

  def post(self, request):
    user_following = self.model.objects.filter(user=request.user)
    user_followed_by = self.model.objects.filter(followed_user=request.user)
    search_result = []

    query = request.GET.get('user')
    if query is not None:
      try:
        search_result = User.objects.all().filter(
          username__icontains=query).exclude(Q(username=request.user.username) | Q(username__in=[str(user.followed_user) for user in user_following]))
      except User.DoesNotExist:
        search_result = []
    if 'delete_user_follow' in request.POST:
      to_unfollower_user = User.objects.get(id=request.POST.get('user_id'))
      if to_unfollower_user is not None:
        UserFollows.objects.filter(
          user=request.user, followed_user=to_unfollower_user).delete()
        user_following = self.model.objects.filter(user=request.user)
      return render(request, self.template_name, context={'form': self.form_class(), 'delete_form': self.delete_form, 'user_following': user_following, 'user_followed_by': user_followed_by, 'search_result': search_result, 'to_unfollower_user': to_unfollower_user})
    else:
      to_follow_user = request.POST.get("user_id")

      if to_follow_user not in [str(user.followed_user.id) for user in user_following]:
        new_followed_user = UserFollows.objects.create(
          user=request.user, followed_user=User.objects.get(id=to_follow_user))
        new_followed_user.save()

      user_following = self.model.objects.all().filter(user=request.user)
      user_followed_by = self.model.objects.all().filter(followed_user=request.user)
      if query is not None:
        try:
          search_result = User.objects.all().filter(
            username__icontains=query).exclude(Q(username=request.user.username) | Q(username__in=[str(user.followed_user) for user in user_following]))
        except User.DoesNotExist:
          search_result = []
      return render(request, self.template_name, context={'form': self.form_class(), 'delete_form': self.delete_form, 'user_following': user_following, 'user_followed_by': user_followed_by, 'search_result': search_result})


class CreateTicketView(LoginRequiredMixin, View):
  model = Ticket
  template_name = 'reviews/create_ticket.html'
  form_class = TicketForm

  def get(self, request):
    return render(request, self.template_name, context={'form': self.form_class()})

  def post(self, request):
    form = self.form_class(request.POST, request.FILES)
    if not form.is_valid():
      return render(request, self.template_name, context={'form': form})
    new_ticket = Ticket.objects.create(
      title=form.cleaned_data['title'],
      description=form.cleaned_data['description'],
      image=form.cleaned_data['image'],
      user=request.user
    )
    new_ticket.save()
    return redirect('flux')


class CreateReviewView(LoginRequiredMixin, View):
  model = Review
  template_name = 'reviews/create_review.html'
  form_class = ReviewForm
  ticket_form = TicketForm

  def get(self, request):
    if request.GET.get('ticket_id') is None:
      return render(request, self.template_name, context={'form': self.form_class(), 'ticket_form': self.ticket_form()})
    ticket = Ticket.objects.get(id=request.GET.get('ticket_id'))
    return render(request, self.template_name, context={'form': self.form_class(), 'ticket': ticket})

  def post(self, request):
    if request.POST.get('ticket_id') is None:
      form = self.ticket_form(request.POST, request.FILES)
      if not form.is_valid():
        return render(request, self.template_name, context={'form': form})
      new_ticket = Ticket.objects.create(
        title=form.cleaned_data['title'],
        description=form.cleaned_data['description'],
        image=form.cleaned_data['image'],
        user=request.user
      )
      new_ticket.save()
      ticket = Ticket.objects.get(
        user=request.user, title=form.cleaned_data['title'])
      return render(request, self.template_name, context={'form': self.form_class(), 'ticket': ticket})
    else:
      form = self.form_class(request.POST)
      if not form.is_valid():
        return render(request, self.template_name, context={'form': form})
      new_review = Review.objects.create(
        rating=form.cleaned_data['rating'],
        body=form.cleaned_data['body'],
        headline=form.cleaned_data['headline'],
        user=request.user,
        ticket=Ticket.objects.get(id=request.POST.get('ticket_id')))
      new_review.save()
      return redirect('flux')


class ProfileView(LoginRequiredMixin, View):
  model = User
  template_name = 'reviews/profile.html'

  def get(self, request):
    current_user_tickets = Ticket.objects.filter(user=request.user)
    current_user_reviews = Review.objects.filter(user=request.user)
    return render(request, self.template_name, context={'current_user_tickets': current_user_tickets, 'current_user_reviews': current_user_reviews})


class EditOrDeleteTicketView(LoginRequiredMixin, View):
  model = Ticket
  template_name = 'reviews/edit_or_delete_ticket.html'
  edit_form_class = TicketForm
  delete_form_class = DeleteTicketForm

  def get(self, request, pk):
    ticket = get_object_or_404(self.model, pk=pk)
    return render(request, self.template_name, context={'ticket': ticket, 'edit_form': self.edit_form_class(instance=ticket), 'delete_form': self.delete_form_class()})

  def post(self, request, pk):
    if 'delete_ticket_form' in request.POST:
      ticket = get_object_or_404(self.model, pk=pk)
      ticket.delete()
      return redirect('profile')
    else:
      ticket = get_object_or_404(self.model, pk=pk)
      edit_form = self.edit_form_class(
        request.POST, request.FILES, instance=ticket)
      if edit_form.is_valid():
        edit_form.save()
        return redirect('profile')


class EditOrDeleteReviewView(LoginRequiredMixin, View):
  model = Review
  template_name = 'reviews/edit_or_delete_review.html'
  edit_form_class = ReviewForm
  delete_form_class = DeleteReviewForm

  def get(self, request, pk):
    review = get_object_or_404(self.model, pk=pk)
    return render(request, self.template_name, context={'review': review, 'edit_form': self.edit_form_class(instance=review), 'delete_form': self.delete_form_class()})

  def post(self, request, pk):
    if 'delete_review_form' in request.POST:
      review = get_object_or_404(self.model, pk=pk)
      review.delete()
      return redirect('profile')
    else:
      review = get_object_or_404(self.model, pk=pk)
      edit_form = self.edit_form_class(
        request.POST, instance=review)
      if edit_form.is_valid():
        edit_form.save()
        return redirect('profile')
