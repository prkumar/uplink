from uplink import helpers


def test_get_api_definitions(request_definition_builder):
    class Service(object):
        builder = request_definition_builder

    assert dict(helpers.get_api_definitions(Service)) == {
        "builder": request_definition_builder
    }


def test_get_api_definitions_from_parent(request_definition_builder):
    class Parent(object):
        builder = request_definition_builder

    class Child(Parent):
        other_builder = request_definition_builder

    assert dict(helpers.get_api_definitions(Child)) == {
        "other_builder": request_definition_builder
    }


class TestRequestBuilder(object):
    def test_return_type(self):
        # Setup
        builder = helpers.RequestBuilder({})

        # Run
        builder.return_type = str

        # Verify
        assert builder.return_type is str

    def test_add_transaction_hook(self, transaction_hook_mock):
        # Setup
        builder = helpers.RequestBuilder({})

        # Run
        builder.add_transaction_hook(transaction_hook_mock)

        # Verify
        assert list(builder.transaction_hooks) == [transaction_hook_mock]
