# Non-Blocking Requests with Uplink

This example details how you can use the same Uplink consumer with different
HTTP clients, with an emphasis on performing non-blocking HTTP requests. 

The example includes three Python scripts:

- `github.py`: Defines a `GitHub` API with two methods:
    - `GitHub.get_repos`: Gets all public repositories
    - `GitHub.get_contributors`: Lists contributors for the specified repository.
    
The other two scripts are functionally identical. They each use the `GitHub` 
consumer to fetch contributors for 10 public repositories, concurrently. The
only difference between the scripts is the HTTP client used:

- `asyncio_example.py`: Uses `aiohttp` for awaitable responses to be run with
                        an `asyncio` event loop.
- `twisted_example.py`: Uses `requests` with `twisted` (inspired by
                        [`requests-threads`](https://github.com/requests/requests-threads))
                        to create `Deferred` responses.
    
  