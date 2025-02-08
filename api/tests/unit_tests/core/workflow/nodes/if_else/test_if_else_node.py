from unittest.mock import MagicMock

from core.workflow.nodes.if_else.if_else_node import _should_not_use_old_function


def test_should_not_use_old_function():
    variable_pool = MagicMock()
    variable_pool.variables = {"test_var": "test"}
    conditions = [{"variable_selector": "test_var", "comparison_operator": "==", "value": "test"}]
    processor = MagicMock()
    processor.process_conditions.return_value = (conditions, [], True)

    result = _should_not_use_old_function(
        condition_processor=processor, variable_pool=variable_pool, conditions=conditions, operator="and"
    )

    assert isinstance(result, tuple)
    assert len(result) == 3
    assert isinstance(result[0], list)
    assert isinstance(result[1], list)
    assert isinstance(result[2], bool)
    assert result[2] is True
