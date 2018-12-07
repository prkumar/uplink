# Response and Error Handling Example

---

This example shows how to handle errors and responses via callbacks. These callbacks allow you
to define error handlers and response handlers that can perform processing of the response
from the remote server.

Included are two examples:

1. (response_handler) Get the google home page and print the response status code
```
google = Google(base_url=BASE_URL)
google.homepage()
Prints: Google response status: 200
```

2. (error_handler) Get an invalid url and prints the exception type
```
google = Google(base_url="NON_EXISTENT_URL")
google.bad_page()
Prints: Error Encountered. Exception will be raised...
```