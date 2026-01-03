import pytest
from legal_doc_gen import LegalDocumentGenerator


def test_variable_replacement():
    """Test basic variable replacement."""
    generator = LegalDocumentGenerator()
    template = "Hello, {{ name }}!"
    context = {"name": "John Doe"}
    result = generator.render(template, context)
    assert result == "Hello, John Doe!"


def test_variable_replacement_with_dot_notation():
    """Test variable replacement with dot notation."""
    generator = LegalDocumentGenerator()
    template = "Hello, {{ person.name }}! You are {{ person.age }} years old."
    context = {"person": {"name": "John Doe", "age": 30}}
    result = generator.render(template, context)
    assert result == "Hello, John Doe! You are 30 years old."


def test_if_block_true():
    """Test if block with true condition."""
    generator = LegalDocumentGenerator()
    template = "{% if show_message %}Hello!{% endif %}"
    context = {"show_message": True}
    result = generator.render(template, context)
    assert result == "Hello!"


def test_if_block_false():
    """Test if block with false condition."""
    generator = LegalDocumentGenerator()
    template = "{% if show_message %}Hello!{% endif %}"
    context = {"show_message": False}
    result = generator.render(template, context)
    assert result == ""


def test_for_loop():
    """Test for loop without loop information."""
    generator = LegalDocumentGenerator()
    template = "{% for item in items %}{{ item }}, {% endfor %}"
    context = {"items": ["apple", "banana", "cherry"]}
    result = generator.render(template, context)
    assert result == "apple, banana, cherry, "


def test_for_loop_with_loop_info():
    """Test for loop with loop information."""
    generator = LegalDocumentGenerator()
    template = "{% for item in items %}{{ loop.index }}. {{ item }}\n{% endfor %}"
    context = {"items": ["apple", "banana", "cherry"]}
    result = generator.render(template, context)
    expected = "1. apple\n2. banana\n3. cherry\n"
    assert result == expected


def test_nested_blocks():
    """Test nested if and for blocks."""
    generator = LegalDocumentGenerator()
    template = "{% for item in items %}{% if item.active %}{{ item.name }}{% endif %}{% endfor %}"
    context = {"items": [{"name": "apple", "active": True}, {"name": "banana", "active": False}, {"name": "cherry", "active": True}]}
    result = generator.render(template, context)
    assert result == "applecherry"


def test_legal_document_example():
    """Test a complete legal document example."""
    generator = LegalDocumentGenerator()
    template = """
# LEGAL AGREEMENT

This Agreement is made and entered into on {{ today }} by and between:

- {{ client.full_name }}, residing at {{ client.address }}
- {{ attorney.full_name }}, licensed to practice law in {{ attorney.state }}

### TERMS AND CONDITIONS

1. {{ attorney.full_name }} agrees to represent {{ client.full_name }} in the matter of {{ case.subject }}.
2. The representation shall commence on {{ case.start_date }} and continue until {{ case.end_date }}.
3. {{ client.full_name }} agrees to pay {{ attorney.rate }} per hour for legal services.

{% if client.retainer_paid %}
4. A retainer fee of {{ client.retainer_amount }} has been paid.
{% endif %}

SIGNED:
- _________________________ ({{ client.full_name }})
- _________________________ ({{ attorney.full_name }})
"""
    
    context = {
        "today": "January 1, 2024",
        "client": {
            "full_name": "John Doe",
            "address": "123 Main Street, Anytown, USA",
            "retainer_paid": True,
            "retainer_amount": "$5,000"
        },
        "attorney": {
            "full_name": "Jane Smith",
            "state": "California",
            "rate": "$300"
        },
        "case": {
            "subject": "Divorce Proceedings",
            "start_date": "January 10, 2024",
            "end_date": "December 31, 2024"
        }
    }
    
    result = generator.render(template, context)
    
    # Check that all variables are replaced correctly
    assert "January 1, 2024" in result
    assert "John Doe" in result
    assert "123 Main Street, Anytown, USA" in result
    assert "Jane Smith" in result
    assert "California" in result
    assert "$300" in result
    assert "Divorce Proceedings" in result
    assert "January 10, 2024" in result
    assert "December 31, 2024" in result
    assert "$5,000" in result


def test_empty_template():
    """Test rendering an empty template."""
    generator = LegalDocumentGenerator()
    template = ""
    context = {"name": "John"}
    result = generator.render(template, context)
    assert result == ""


def test_missing_variable():
    """Test handling of missing variables."""
    generator = LegalDocumentGenerator()
    template = "Hello, {{ name }}! Your age is {{ age }}."
    context = {"name": "John"}
    result = generator.render(template, context)
    assert result == "Hello, John! Your age is ."
