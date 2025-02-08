from core.prompt.utils.prompt_template_parser import PromptTemplateParser


def test_extract_basic_variables():
    template = "Hello {{name}}, your age is {{age}}"
    parser = PromptTemplateParser(template)
    assert parser.extract() == ["name", "age"]


def test_extract_special_variables():
    template = "{{#query#}} {{#context#}} {{#histories#}}"
    parser = PromptTemplateParser(template)
    assert parser.extract() == ["#query#", "#context#", "#histories#"]


def test_extract_with_variable_tmpl():
    template = "{{#user.name#}} {{#system.context#}}"
    parser = PromptTemplateParser(template, with_variable_tmpl=True)
    assert parser.extract() == ["#user.name#", "#system.context#"]


def test_extract_mixed_variables():
    template = "{{name}} {{#query#}} {{age}} {{#context#}}"
    parser = PromptTemplateParser(template)
    assert parser.extract() == ["name", "#query#", "age", "#context#"]


def test_format_basic_variables():
    template = "Hello {{name}}, your age is {{age}}"
    parser = PromptTemplateParser(template)
    result = parser.format({"name": "John", "age": "30"})
    assert result == "Hello John, your age is 30"


def test_format_missing_variables():
    template = "Hello {{name}}, your age is {{age}}"
    parser = PromptTemplateParser(template)
    result = parser.format({"name": "John"})
    assert result == "Hello John, your age is {age}"


def test_format_with_variable_tmpl():
    template = "User {{#user.name#}} says {{#message.content#}}"
    parser = PromptTemplateParser(template, with_variable_tmpl=True)
    result = parser.format({"#user.name#": "John", "#message.content#": "hello"})
    assert result == "User John says hello"


def test_format_with_special_tokens():
    template = "Query: {{#query#}} <|im_end|> Context: {{#context#}}"
    parser = PromptTemplateParser(template)
    result = parser.format({"#query#": "test", "#context#": "info"})
    assert result == "Query: test  Context: info"


def test_format_keep_template_variables():
    template = "Hello {{name}} with {{nested_var}}"
    parser = PromptTemplateParser(template)
    result = parser.format({"name": "John {{title}}"}, remove_template_variables=False)
    assert result == "Hello John {{title}} with {{nested_var}}"


def test_format_remove_template_variables():
    template = "Hello {{name}} with {{nested_var}}"
    parser = PromptTemplateParser(template)
    result = parser.format({"name": "John {{title}}"}, remove_template_variables=True)
    assert result == "Hello John {title} with {nested_var}"


def test_extract_empty_template():
    template = ""
    parser = PromptTemplateParser(template)
    assert parser.extract() == []


def test_format_empty_template():
    template = ""
    parser = PromptTemplateParser(template)
    result = parser.format({})
    assert result == ""


def test_extract_invalid_variable_names():
    template = "{{123}} {{!invalid}} {{valid_name}}"
    parser = PromptTemplateParser(template)
    assert parser.extract() == ["valid_name"]


def test_format_special_characters():
    template = "Hello {{name}}"
    parser = PromptTemplateParser(template)
    result = parser.format({"name": "John & Jane"})
    assert result == "Hello John & Jane"


def test_format_multiline_template():
    template = """Line 1: {{var1}}
    Line 2: {{var2}}"""
    parser = PromptTemplateParser(template)
    result = parser.format({"var1": "test1", "var2": "test2"})
    assert (
        result
        == """Line 1: test1
    Line 2: test2"""
    )
