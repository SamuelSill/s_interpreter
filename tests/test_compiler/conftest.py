from pytest import Function as _Function

VARIABLE_NAMES = ["X", "Y", "Z"]
LABEL_NAMES = ["A", "B", "C", "D", "E"]
OPTIONAL_WHITESPACE = ["", "\t", " "]


def pytest_collection_modifyitems(items: list[_Function]):
    module_order: list[str] = [
        "test_variable",
        "test_label",
        "test_sentence",
        "test_instruction",
        "test_program",
        "test_encode"
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
