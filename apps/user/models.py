from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

class User(AbstractUser):
    username = models.CharField(
        _('username'),
        max_length=24,
        unique=True,
    )
    nick_name=models.CharField(_('nick name'), max_length=32, blank=True,default='')
    first_name=None
    last_name=None

   # role=models.CharField(_('role'), max_length=32, blank=True,default='-')
    def __str__(self):
        return "{}|{}".format(self.nick_name,self.username)

    def get_full_name(self):

        return self.nick_name

    def get_short_name(self):
        """Return the short name for the user."""
        return self.nick_name

    def get_groups(self):
        return [group.name for group in self.groups.all()]
