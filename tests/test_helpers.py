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
