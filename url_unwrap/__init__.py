"""Recover clean target URLs from redirect links with the ClearURLs rules.

Follows the browser extension (https://github.com/ClearURLs/Addon) on its
published rule set (https://github.com/ClearURLs/Rules, LGPL-3.0):

* a provider applies if ``urlPattern`` matches and no ``exceptions`` match;
* ``redirections``: the first capture group is the target, percent-decoded once;
* ``rawRules``: regex substitutions on the whole URL;
* ``rules`` and ``referralMarketing``: query and fragment parameters whose
  name fully matches are removed;
* all patterns are case-insensitive.
"""

from base64 import urlsafe_b64decode
from functools import cache
from os import PathLike
from re import IGNORECASE, Pattern, compile
from typing import Annotated
from urllib.parse import unquote, urlsplit, urlunsplit
from urllib.request import urlopen

from pydantic import BaseModel, BeforeValidator, ConfigDict
from pydantic.alias_generators import to_camel

__all__ = ["Provider", "Providers", "default_providers", "unwrap"]


PatternIgnoreCase = Annotated[
    Pattern,
    BeforeValidator(lambda pattern: compile(pattern, IGNORECASE)),
]


class Provider(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    url_pattern: PatternIgnoreCase
    exceptions: list[PatternIgnoreCase] = []
    redirections: list[PatternIgnoreCase] = []
    # Not a ClearURLs key: like ``redirections``, but the target is base64url-encoded.
    base64_redirections: list[PatternIgnoreCase] = []
    raw_rules: list[PatternIgnoreCase] = []
    rules: list[PatternIgnoreCase] = []
    referral_marketing: list[PatternIgnoreCase] = []

    def applies_to(self, url: str) -> bool:
        return self.url_pattern.search(url) is not None and not any(
            exception.search(url) for exception in self.exceptions
        )

    def apply(self, url: str) -> str:
        """Redirection target if one matches, else ``url`` without tracking params."""
        if not self.applies_to(url):
            return url
        for redirection in self.redirections:
            match = redirection.search(url)
            if match:
                return unquote(match.group(1))
        for redirection in self.base64_redirections:
            match = redirection.search(url)
            if match:
                encoded = match.group(1)
                return urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)).decode()
        for raw_rule in self.raw_rules:
            url = raw_rule.sub("", url)
        param_names = self.rules + self.referral_marketing
        if param_names:
            parts = urlsplit(url)
            url = urlunsplit(
                parts._replace(
                    query=_remove_params(parts.query, param_names),
                    fragment=_remove_params(parts.fragment, param_names),
                )
            )
        return url


# Search-engine redirect links not covered by the ClearURLs rules.
EXTRA_PROVIDERS = [
    Provider.model_validate(  # Google image search
        {
            "urlPattern": r"^https?://(?:[a-z0-9-]+\.)*?google(?:\.[a-z]{2,}){1,}/imgres\?",
            "redirections": [r"[?&]imgrefurl=([^&]+)"],
        }
    ),
    Provider.model_validate(
        {
            "urlPattern": r"^https?://(?:[a-z0-9-]+\.)*?bing\.com/ck/a\?",
            "base64Redirections": [r"[?&]u=a1([^&]+)"],
        }
    ),
    Provider.model_validate(
        {
            "urlPattern": r"^https?://r\.search\.yahoo\.com/",
            "redirections": [r"/RU=([^/]+)/"],
        }
    ),
]


class Providers(BaseModel):
    providers: dict[str, Provider]

    @classmethod
    def from_file(cls, path: str | PathLike) -> "Providers":
        with open(path, "rb") as file:
            return cls.model_validate_json(file.read())

    @classmethod
    def fetch(
        cls, url: str = "https://rules2.clearurls.xyz/data.minify.json"
    ) -> "Providers":
        with urlopen(url) as response:
            return cls.model_validate_json(response.read())

    def apply(self, url: str) -> str:
        for provider in [*self.providers.values(), *EXTRA_PROVIDERS]:
            url = provider.apply(url)
        return url


@cache
def default_providers() -> Providers:
    """ClearURLs rules, fetched once and shared."""
    return Providers.fetch()


def unwrap(url: str, providers: Providers | None = None) -> str:
    """Follow redirections and remove tracking parameters until nothing changes.

    >>> unwrap(
    ...     "https://www.bing.com/ck/a?u=a1aHR0cHM6Ly9leGFtcGxlLm9yZy8",
    ...     Providers(providers={}),
    ... )
    'https://example.org/'
    """
    providers = providers or default_providers()
    # Redirection targets and cleaned URLs are shorter than their input, so this ends.
    while (result := providers.apply(url)) != url:
        url = result
    return url


def _remove_params(params: str, name_patterns: list[Pattern]) -> str:
    """Drop ``name=value`` items whose name matches; kept items stay as they are."""
    # Not parse_qsl/urlencode: the round trip would re-encode kept values
    # (e.g. ``a%20b`` -> ``a+b``).
    return "&".join(
        param
        for param in params.split("&")
        if not any(
            pattern.fullmatch(param.split("=", 1)[0]) for pattern in name_patterns
        )
    )
