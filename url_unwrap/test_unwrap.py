from pytest import fixture, mark, param

from url_unwrap import Providers, default_providers, unwrap


@fixture
def extra_providers() -> Providers:
    """Only the providers added on top of ClearURLs."""
    return Providers(providers={})


@fixture
def providers() -> Providers:
    """ClearURLs rules (fetched) and extra providers."""
    return default_providers()


@mark.parametrize(
    ("url", "expected"),
    [
        param(
            "https://www.google.com/imgres?imgurl=https://example.org/i.png&imgrefurl=https://example.org/page&h=1",
            "https://example.org/page",
            id="google-imgres",
        ),
        param(
            # ``u`` is ``a1`` + base64url("https://example.org/p?x=1").
            "https://www.bing.com/ck/a?!&&p=abc&ptn=3&u=a1aHR0cHM6Ly9leGFtcGxlLm9yZy9wP3g9MQ&ntb=1",
            "https://example.org/p?x=1",
            id="bing",
        ),
        param(
            "https://r.search.yahoo.com/_ylt=Awr;_ylu=Y29s/RV=2/RE=1700000000/RO=10/"
            "RU=https%3a%2f%2fexample.org%2fpage/RK=2/RS=abc-",
            "https://example.org/page",
            id="yahoo",
        ),
    ],
)
def test_extra_providers(extra_providers: Providers, url: str, expected: str) -> None:
    assert unwrap(url, extra_providers) == expected


@mark.parametrize(
    ("url", "expected"),
    [
        param(
            "https://www.google.com/url?q=https://example.org/a%3Fb%3D1&sa=U&ved=x&usg=y",
            "https://example.org/a?b=1",
            id="google-q",
        ),
        param(
            "https://www.google.de/url?sa=t&q=search+terms&url=https%3A%2F%2Fexample.org%2Fa%3Fb%3D1",
            "https://example.org/a?b=1",
            id="google-url",
        ),
        param(
            "https://duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.org%2F&rut=abc",
            "https://example.org/",
            id="duckduckgo",
        ),
        param(
            "https://duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.google.com%2Furl%3Fq%3Dhttps%3A%2F%2Fexample.org%2F",
            "https://example.org/",
            id="chain",
        ),
        param(
            "https://www.youtube.com/redirect?event=x&q=https%3A%2F%2Fexample.org%2F%3Futm_source%3Dyt",
            "https://example.org/",
            id="youtube",
        ),
        param(
            "https://l.facebook.com/l.php?u=https%3A%2F%2Fexample.org%2F&h=AT0",
            "https://example.org/",
            id="facebook",
        ),
        *(
            param(
                f"https://example.org/a?id=7&{name}=x",
                "https://example.org/a?id=7",
                id=name,
            )
            for name in [
                "utm_source",
                "utm_medium",
                "utm_campaign",
                "utm_term",
                "utm_content",
                "utm_id",
                "UTM_Source",
            ]
        ),
        param(
            "https://example.org/a?id=7&utm_source=x&UTM_Medium=y&fbclid=z#top",
            "https://example.org/a?id=7#top",
            id="tracking",
        ),
        param(
            "https://example.org/a?utm_source=x",
            "https://example.org/a",
            id="all-params-removed",
        ),
        param(
            "https://example.org/s?q=a%20b+c&utm_source=x",
            "https://example.org/s?q=a%20b+c",
            id="encoding-preserved",
        ),
        param(
            "https://www.google.com/search?q=wayback&sca_esv=1&ei=abc&ved=0&oq=way&gs_lp=x",
            "https://www.google.com/search?q=wayback",
            id="google-search",
        ),
        param(
            "https://example.org/?ref=abc&x=1",
            "https://example.org/?x=1",
            id="referral",
        ),
        param(
            "https://github.com/x/y?ref=abc",
            "https://github.com/x/y?ref=abc",
            id="exception",
        ),
    ],
)
def test_unwrap(providers: Providers, url: str, expected: str) -> None:
    assert unwrap(url, providers) == expected
