from pytest import Function as _Function


def pytest_collection_modifyitems(items: list[_Function]):
    module_order: list[str] = [
        "test_compiler",
        "test_interpreter"
    ]

    module_mapping = {
        item: item.module.__name__
        for item in items
    }

    for module in module_order:
        items[:] = [
            item for item in items if module_mapping[item] != module
        ] + [
            item for item in items if module_mapping[item] == module
        ]
