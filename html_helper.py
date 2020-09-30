
async def fetch_html(url: str, session: ClientSession, cookies, **kwargs) -> str:
    """GET request wrapper to fetch page HTML.

    kwargs are passed to `session.request()`.
    """
    # session.cookie_jar = cookies
    # resp = await session.request(method="GET", url=url, cookies=cookies **kwargs)
    resp = await session.get(url=url, cookies=cookies, **kwargs)
    resp.raise_for_status()
    html = await resp.text()
    return html