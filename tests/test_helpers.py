from uplink import helpers


def test_get_api_definitions(request_definition_builder):
    class Service(object):
        builder = request_definition_builder

    assert dict(helpers.get_api_definitions(Service)) == {
        "builder": request_definition_builder
    }
