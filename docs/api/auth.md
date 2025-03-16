# Authentication

The `auth` parameter of the `Consumer` constructor offers a way to
define an auth method to use for all requests.

``` python
auth_method = SomeAuthMethod(...)
github = GitHub(BASE_URL, auth=auth_method)
```

::: uplink.auth.BasicAuth
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.auth.ProxyAuth
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.auth.BearerToken
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.auth.MultiAuth
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.auth.ApiTokenParam
    options:
        show_bases: false
        members: false
        inherited_members: false
