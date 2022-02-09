"""LITReview URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from authentification.forms import UserLoginForm
import authentification.views
import reviews.views


urlpatterns = [
    # ADMIN
    path('admin/', admin.site.urls),

    # AUTHENTIFICATION
    path('', LoginView.as_view(
        template_name='authentification/login.html',
        authentication_form=UserLoginForm,
        redirect_authenticated_user=True),
        name='login'),
    path('logout/', LogoutView.as_view(
        next_page="login"),
        name='logout'),
    path('signup/', authentification.views.SignupView.as_view(), name='signup'),

    # TICKETS
    path('tickets/', reviews.views.FluxView.as_view(), name='flux'),
    path('create-ticket', reviews.views.CreateTicketView.as_view(),
         name='create-ticket'),
    path('ticket/<int:pk>', reviews.views.EditOrDeleteTicketView.as_view(), name='edit-ticket'),

    # FOLLOWS
    path('follows/', reviews.views.UserFollowsView.as_view(), name='follows'),
    
    #REVIEWS
    path('create-review', reviews.views.CreateReviewView.as_view(), name='create-review'),
    path('review/<int:pk>', reviews.views.EditOrDeleteReviewView.as_view(), name='edit-review'),
    
    #PROFILE 
    path('profile/', reviews.views.ProfileView.as_view(), name='profile'),

]

urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
