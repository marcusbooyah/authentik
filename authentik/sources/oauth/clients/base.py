"""OAuth Clients"""
from typing import Any, Optional
from urllib.parse import quote, urlencode

from django.http import HttpRequest
from requests import Session
from requests.exceptions import RequestException
from requests.models import Response
from structlog.stdlib import get_logger

from authentik.events.models import Event, EventAction
from authentik.lib.utils.http import get_http_session
from authentik.sources.oauth.models import OAuthSource

LOGGER = get_logger()


class BaseOAuthClient:
    """Base OAuth Client"""

    session: Session

    source: OAuthSource
    request: HttpRequest

    callback: Optional[str]

    def __init__(self, source: OAuthSource, request: HttpRequest, callback: Optional[str] = None):
        self.source = source
        self.session = get_http_session()
        self.request = request
        self.callback = callback

    def get_access_token(self, **request_kwargs) -> Optional[dict[str, Any]]:
        "Fetch access token from callback request."
        raise NotImplementedError("Defined in a sub-class")  # pragma: no cover

    def get_profile_info(self, token: dict[str, str]) -> Optional[dict[str, Any]]:
        "Fetch user profile information."
        profile_url = self.source.type.profile_url or ""
        if self.source.type.urls_customizable and self.source.profile_url:
            profile_url = self.source.profile_url
        try:
            response = self.do_request("get", profile_url, token=token)
            response.raise_for_status()
        except RequestException as exc:
            LOGGER.warning("Unable to fetch user profile", exc=exc, body=response.text)
            return None
        else:
            return response.json()

    def get_redirect_args(self) -> dict[str, str]:
        "Get request parameters for redirect url."
        raise NotImplementedError("Defined in a sub-class")  # pragma: no cover

    def get_redirect_url(self, parameters=None):
        "Build authentication redirect url."
        args = self.get_redirect_args()
        additional = parameters or {}
        args.update(additional)
        # Special handling for scope, since it's set as array
        # to make additional scopes easier
        args["scope"] = " ".join(sorted(set(args["scope"])))
        params = urlencode(args, quote_via=quote)
        LOGGER.info("redirect args", **args)
        authorization_url = self.source.type.authorization_url or ""
        if self.source.type.urls_customizable and self.source.authorization_url:
            authorization_url = self.source.authorization_url
        if authorization_url == "":
            Event.new(
                EventAction.CONFIGURATION_ERROR,
                source=self.source,
                message="Source has an empty authorization URL.",
            ).save()
        return f"{authorization_url}?{params}"

    def parse_raw_token(self, raw_token: str) -> dict[str, Any]:
        "Parse token and secret from raw token response."
        raise NotImplementedError("Defined in a sub-class")  # pragma: no cover

    def do_request(self, method: str, url: str, **kwargs) -> Response:
        """Wrapper around self.session.request, which can add special headers"""
        return self.session.request(method, url, **kwargs)

    @property
    def session_key(self) -> str:
        """Return Session Key"""
        raise NotImplementedError("Defined in a sub-class")  # pragma: no cover
