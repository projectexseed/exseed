from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from score.models import Point


class AccountManager(BaseUserManager):
    def update_user(self, user, email, first_name, last_name, password=None, email_notifications=True):
        if password:
            user.set_password(password)

        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.email_notifications = email_notifications

        user.save()

    def create_user(self, email, first_name, last_name, password=None, house=None, email_notifications=True):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=AccountManager.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            email_notifications=email_notifications,
        )

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(email, first_name, last_name, password=password,)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

    def user_invitations(self, user):
        invites = Invitation.objects.filter(email=user.email, is_accepted=False, is_denied=False)
        if invites.exists():
            return invites
        else:
            return None

    def room_mates(self, user):
        qs = super(AccountManager, self).get_queryset()
        # qs = qs.filter(house=user.house)
        qs = qs.exclude(pk=user.pk)
        return qs


class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)

    email_notifications = models.BooleanField(default=True, help_text="Notifications are sent when one of your roommates does something, such as adding an item to split or marking things as paid between you.")
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', ]

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name

    def __unicode__(self):
        return self.get_full_name()

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def points(self):
        point, created = Point.objects.get_or_create(account=self)
        return point.points


class Invitation(models.Model):
    email = models.EmailField(max_length=254)
    from_user = models.ForeignKey(Account, related_name='sent_invitations')

    is_accepted = models.BooleanField(default=False)
    is_denied = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s %s %s" % (self.email, self.from_user.email, self.is_accepted)
