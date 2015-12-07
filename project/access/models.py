from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_markdown.models import MarkdownField
from asylum.models import AsylumModel
# importing after asylum.mixins to get the monkeypatching done there
from reversion import revisions
from django.db import transaction

class TokenType(AsylumModel):
    label = models.CharField(_("Label"), max_length=200, blank=False)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = _('Token Type')
        verbose_name_plural = _('Token Types')

revisions.default_revision_manager.register(TokenType)


class Token(AsylumModel):
    label = models.CharField(_("Label"), max_length=200, blank=True)
    owner = models.ForeignKey('members.Member', blank=False, verbose_name=_("Member"), related_name='access_tokens')
    ttype = models.ForeignKey(TokenType, blank=False, verbose_name=_("Token type"), related_name='+')
    value = models.CharField(_("Token value"), max_length=200, blank=False)
    revoked = models.BooleanField(_("Revoked"), default=False)

    def __str__(self):
        if self.label:
            return self.label
        return _("%s '%s' for %s") % (self.ttype, self.value, self.owner)

    class Meta:
        verbose_name = _('Token')
        verbose_name_plural = _('Tokens')

revisions.default_revision_manager.register(Token)


class AccessType(AsylumModel):
    label = models.CharField(_("Label"), max_length=200, blank=False)
    bit = models.PositiveSmallIntegerField(_("Bit number"), blank=True, null=True, unique=True) # For systems that utilize bitwise checks
    external_id = models.CharField(_("External identifier"), max_length=200, blank=True, null=True, unique=True) # For other systems

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = _('Access Type')
        verbose_name_plural = _('Access Types')

revisions.default_revision_manager.register(AccessType)


class Grant(AsylumModel):
    owner = models.ForeignKey('members.Member', blank=False, verbose_name=_("Member"), related_name='access_granted')
    atype = models.ForeignKey(AccessType, related_name='+', verbose_name=_("Access"))
    notes = MarkdownField(verbose_name=_("Notes"), blank=True)

    def __str__(self):
        return _("%s for %s") % (self.atype, self.owner)

    class Meta:
        verbose_name = _('Grant')
        verbose_name_plural = _('Grants')
        unique_together = ('owner', 'atype')

revisions.default_revision_manager.register(Grant)

class NonMemberToken(AsylumModel):
    label = models.CharField(_("Label"), max_length=200, blank=True)
    ttype = models.ForeignKey(TokenType, blank=False, verbose_name=_("Token type"), related_name='+')
    value = models.CharField(_("Token value"), max_length=200, blank=False)
    revoked = models.BooleanField(_("Revoked"), default=False)
    grants = models.ManyToManyField(Grant, blank=True)
    contact = models.CharField(_("Contact"), max_length=200, blank=False)
    notes = MarkdownField(verbose_name=_("Notes"), blank=True)

    def __str__(self):
        if self.label:
            return self.label
        return _("%s '%s' for %s") % (self.ttype, self.value, self.contact)

    class Meta:
        verbose_name = _('Non-member token')
        verbose_name_plural = _('Non-member tokens')

revisions.default_revision_manager.register(NonMemberToken)
