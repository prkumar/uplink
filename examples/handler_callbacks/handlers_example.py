from Server import Google, BASE_URL

def test_homepage():
    google = Google(base_url=BASE_URL)
    google.homepage()

def test_error():
    google = Google(base_url="NON_EXISTENT_URL")
    google.bad_page()

test_homepage()
test_error()