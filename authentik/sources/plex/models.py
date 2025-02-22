"""Plex source"""
from typing import Optional

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.http.request import HttpRequest
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _
from rest_framework.fields import CharField
from rest_framework.serializers import BaseSerializer

from authentik.core.models import Source, UserSourceConnection
from authentik.core.types import UILoginButton, UserSettingSerializer
from authentik.flows.challenge import Challenge, ChallengeResponse, ChallengeTypes
from authentik.lib.generators import generate_id


class PlexAuthenticationChallenge(Challenge):
    """Challenge shown to the user in identification stage"""

    client_id = CharField()
    slug = CharField()
    component = CharField(default="ak-flow-sources-plex")


class PlexAuthenticationChallengeResponse(ChallengeResponse):
    """Pseudo class for plex response"""

    component = CharField(default="ak-flow-sources-plex")


class PlexSource(Source):
    """Authenticate against plex.tv"""

    client_id = models.TextField(
        default=generate_id,
        help_text=_("Client identifier used to talk to Plex."),
    )
    allowed_servers = ArrayField(
        models.TextField(),
        default=list,
        blank=True,
        help_text=_(
            (
                "Which servers a user has to be a member of to be granted access. "
                "Empty list allows every server."
            )
        ),
    )
    allow_friends = models.BooleanField(
        default=True,
        help_text=_("Allow friends to authenticate, even if you don't share a server."),
    )
    plex_token = models.TextField(help_text=_("Plex token used to check friends"))

    @property
    def component(self) -> str:
        return "ak-source-plex-form"

    @property
    def serializer(self) -> BaseSerializer:
        from authentik.sources.plex.api.source import PlexSourceSerializer

        return PlexSourceSerializer

    def ui_login_button(self, request: HttpRequest) -> UILoginButton:
        return UILoginButton(
            challenge=PlexAuthenticationChallenge(
                {
                    "type": ChallengeTypes.NATIVE.value,
                    "component": "ak-flow-sources-plex",
                    "client_id": self.client_id,
                    "slug": self.slug,
                }
            ),
            icon_url=static("authentik/sources/plex.svg"),
            name=self.name,
        )

    def ui_user_settings(self) -> Optional[UserSettingSerializer]:
        return UserSettingSerializer(
            data={
                "title": self.name,
                "component": "ak-user-settings-source-plex",
                "configure_url": self.client_id,
                "icon_url": static("authentik/sources/plex.svg"),
            }
        )

    class Meta:

        verbose_name = _("Plex Source")
        verbose_name_plural = _("Plex Sources")


class PlexSourceConnection(UserSourceConnection):
    """Connect user and plex source"""

    plex_token = models.TextField()
    identifier = models.TextField()

    class Meta:

        verbose_name = _("User Plex Source Connection")
        verbose_name_plural = _("User Plex Source Connections")
