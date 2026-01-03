# Template Processor

A simple yet powerful template processing engine written in Python.

## Features

- Easy-to-use template syntax
- Support for variables and expressions
- Loop and condition control structures
- Template inheritance and includes
- Custom filters and functions
- Error handling and debugging

## Installation

```bash
pip install -e .
```

## Usage

### Basic Example

```python
from template_processor import TemplateProcessor

# Create a template processor instance
processor = TemplateProcessor()

# Define template content
template_content = "Hello, {{ name }}! You are {{ age }} years old."

# Define context data
context = {
    "name": "John Doe",
    "age": 30
}

# Render the template
result = processor.render(template_content, context)
print(result)
# Output: Hello, John Doe! You are 30 years old.
```

### Using Template Files

```python
# Render from a template file
result = processor.render_file("templates/greeting.txt", context)
print(result)
```

### Advanced Features

```python
# Template with loops and conditions
template_content = """
<ul>
{% for item in items %}
    {% if item.active %}
        <li>{{ loop.index }}. {{ item.name }}</li>
    {% endif %}
{% endfor %}
</ul>
"""

context = {
    "items": [
        {"name": "Item 1", "active": True},
        {"name": "Item 2", "active": False},
        {"name": "Item 3", "active": True}
    ]
}

result = processor.render(template_content, context)
print(result)
```

## Project Structure

```
template_processor/
├── template_processor/          # Main package directory
│   ├── __init__.py             # Package initialization
│   ├── template_processor.py   # Main template processor implementation
│   ├── lexer.py                # Template lexer
│   ├── parser.py               # Template parser
│   └── renderer.py             # Template renderer
├── templates/                  # Example templates
│   └── greeting.txt
├── tests/                      # Test files
│   ├── test_lexer.py
│   ├── test_parser.py
│   └── test_renderer.py
├── README.md                   # This file
├── requirements.txt            # Dependencies
└── setup.py                    # Package setup
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE for details.
