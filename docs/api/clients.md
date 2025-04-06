# HTTP Clients

The `client` parameter of the `Consumer` constructor offers a way
to swap out Requests with another HTTP client, including those listed here:

```python
github = GitHub(BASE_URL, client=...)
```

## Requests

::: uplink.RequestsClient
    options:
        members: false
        inherited_members: false

## Aiohttp

::: uplink.AiohttpClient
    options:
        members: false
        inherited_members: false

## Twisted

::: uplink.TwistedClient
    options:
        members: false
        inherited_members: false
