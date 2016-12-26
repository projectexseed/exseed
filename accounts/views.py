from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views import generic
from django.views.generic import FormView
from django.contrib.auth import authenticate, login
from accounts.forms import AccountCreationForm, InviteUserForm, AccountChangeForm
from accounts.models import Invitation
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from exseed import config

Account = get_user_model()


class AccountRequiredMixin(object):
    """
    This will make sure, for generic views, that the object being acted upon
    is in fact owned by the logged in user.
    """
    def dispatch(self, request, *args, **kwargs):
        result = super(AccountRequiredMixin, self).dispatch(request, *args, **kwargs)
        if self.object.owner != self.request.user:
            return HttpResponseForbidden()
        return result


class InviteUserView(FormView):
    template_name = 'accounts/invite.html'

    def get_form_class(self):
        return InviteUserForm

    def get_context_data(self, **kwargs):
        context = super(InviteUserView, self).get_context_data(**kwargs)
        invitations = Invitation.objects.filter(from_user=self.request.user, is_accepted=False, is_denied=False)
        context['invitations'] = invitations
        return context

    def form_valid(self, form):
        email = form.cleaned_data['email']
        invitation, created = Invitation.objects.get_or_create(email=email, from_user=self.request.user)

        url = self.request.build_absolute_uri(reverse('invite_accept', args=[invitation.pk]))
        deny = self.request.build_absolute_uri(reverse('invite_deny', args=[invitation.pk]))

        context = {
            'user': self.request.user,
            'accept_url': url,
            'deny_url': deny
        }

        subject = render_to_string('registration/invitation_subject.txt', context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        body = render_to_string('registration/invitation_message.txt', context)

        msg = EmailMultiAlternatives(subject, body, self.request.user.email, [email])
        msg.content_subtype = "html"
        msg.send()

        return render(self.request, 'accounts/invite_sent.html')


class IndexView(generic.TemplateView):
    template_name = 'common/index.html'


class TenantInfoView(generic.TemplateView):
    template_name = 'common/info_tenants.html'


class LandlordInfoView(generic.TemplateView):
    template_name = 'common/info_landlords.html'


class AccountEditFormView(FormView):
    template_name = 'registration/registration_form_update.html'

    def get_form_class(self):
        return AccountChangeForm

    def get_context_data(self, **kwargs):
        context = super(AccountEditFormView, self).get_context_data(**kwargs)
        context["form_title"] = "Edit Account"
        return context

    def get_initial(self):
        initial = {}
        if self.request.user.is_authenticated():
            user = self.request.user
            initial = {
                'current_user': user,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }

        return initial

    def form_valid(self, form):
        email = form.cleaned_data['email']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        password = form.cleaned_data['password1']

        Account.objects.update_user(
            user=self.request.user,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )

        messages.success(self.request, 'Account information updated')
        return self.render_to_response(self.get_context_data(form=form))


class RegistrationFormView(FormView):
    """ User sign up form """
    template_name = 'registration/registration_form.html'

    def get_form_class(self):
        return AccountCreationForm

    def get_contextdata(self, **kwargs):
        context = super(RegistrationFormView, self).get_context_data(**kwargs)
        context["form_title"] = "Create Account"
        return context

    def get_initial(self):
        initial = {}
        if self.kwargs.get('invitation_id'):
            try:
                invitation = Invitation.objects.get(pk=self.kwargs.get('invitation_id'))
                invitation.is_accepted = True
                invitation.save()
                initial['email'] = invitation.email
            except:
                pass

        return initial

    def form_valid(self, form):
        email = form.cleaned_data['email']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        password = form.cleaned_data['password1']

        # house = None
        # if form.cleaned_data.get('house_id'):
        #     house = form.cleaned_data['house_id']

        Account.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )

        send_mail("Account Created", "Welcome aboard %s! Feel free to reply with questions, suggstions or jokes, if you know one.\n\nRaphael" % first_name, config.EMAIL_FROM_ADDRESS, [email])

        user = authenticate(email=email, password=password)
        login(self.request, user)
        return redirect('/')


class AcceptInvitationView(generic.View):
    def get(self, request, *args, **kwargs):
        user = request.user
        invitation_id = kwargs.get('invitation_id')
        if user.is_authenticated():
            try:
                invite = Invitation.objects.get(pk=invitation_id)
                invite.is_accepted = True
                invite.save()
                user.save()
            except:
                raise Http404
            else:
                return render(request, 'accounts/invite_accepted.html')
        else:
            return redirect(request.build_absolute_uri(reverse('signup_from_invite', args=[invitation_id])))


class DenyInvitationView(generic.View):
    def get(self, request, *args, **kwargs):
        try:
            invitation_id = kwargs.get('invitation_id')
            invite = Invitation.objects.get(pk=invitation_id)
            invite.is_denied = True
            invite.save()
        except:
            return render(request, 'accounts/invite_failed.html')
        else:
            return render(request, 'accounts/invite_denied.html')


class CancelInvitationView(generic.View):
    def get(self, request, *args, **kwargs):
        user = request.user
        invitation_id = kwargs.get('invitation_id')
        try:
            invite = Invitation.objects.get(pk=invitation_id, from_user=user)
            invite.delete()
        except:
            raise Http404
        else:
            messages.success(self.request, 'Invitation deleted.')

        return redirect('invite')
