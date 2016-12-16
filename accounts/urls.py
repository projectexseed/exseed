from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from . import views
from accounts.forms import LoginForm, ResetPassword, SetPassword


#Accounts
urlpatterns = [
    url(r'^login/$', auth_views.login, {'authentication_form': LoginForm, }, name='login'),
    url(r'^forgot_password/$', auth_views.password_reset, {'password_reset_form': ResetPassword}, name='password_reset'),
    url(r'^forgot_password/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^forgot_password/complete/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^forgot_password/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm, {'set_password_form': SetPassword}, name='password_reset_confirm'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^signup/$', views.RegistrationFormView.as_view(), name='signup'),
    url(r'^update/$', login_required(views.AccountEditFormView.as_view()), name='account_update'),
    url(r'^signup/(?P<invitation_id>\d+)/$', views.RegistrationFormView.as_view(), name='signup_from_invite'),
    url(r'^invite/$', login_required(views.InviteUserView.as_view()), name='invite'),
    url(r'^invite/accept/(?P<invitation_id>\d+)/$', views.AcceptInvitationView.as_view(), name='invite_accept'),
    url(r'^invite/deny/(?P<invitation_id>\d+)/$', login_required(views.DenyInvitationView.as_view()), name='invite_deny'),
    url(r'^invite/cancel/(?P<invitation_id>\d+)/$', login_required(views.CancelInvitationView.as_view()), name='invite_cancel')
]
