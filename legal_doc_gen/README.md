# Legal Document Generator

A powerful template processing engine specifically designed for creating legal documents.

## Features

- **Variable Replacement**: Replace placeholders with values from a context dictionary
- **Conditional Blocks**: Use `{% if %}` blocks to conditionally include content
- **Loop Blocks**: Use `{% for %}` blocks to iterate over lists
- **Nested Blocks**: Support for nested conditionals and loops
- **Dot Notation**: Access nested dictionary values using dot notation (e.g., `{{ client.name }}`)
- **Loop Information**: Access loop metadata like index, first, last, and length

## Usage

### Basic Example

```python
from legal_doc_gen.legal_doc_generator import LegalDocumentGenerator

# Create a template
template = """
Dear {{ client.name }},

This letter is regarding your case: {{ case.title }}.

{% if case.open %}
Your case is currently open and active.
{% else %}
Your case has been closed.
{% endif %}

{% for item in items %}
- Item {{ loop.index }}: {{ item }}
{% endfor %}

Sincerely,
{{ attorney.name }}
"""

# Create a context
context = {
    "client": {"name": "John Doe"},
    "case": {"title": "Divorce Proceedings", "open": True},
    "items": ["Consultation", "Filing", "Hearing"],
    "attorney": {"name": "Jane Smith"}
}

# Generate the document
generator = LegalDocumentGenerator()
result = generator.render(template, context)
print(result)
```

### Rendering from a File

```python
# Render a document from a template file
generator = LegalDocumentGenerator()
result = generator.render_file("template.txt", context)
print(result)
```

## Template Syntax

### Variables

Use double curly braces to include variables:

```
{{ variable_name }}
{{ nested.variable }}
```

### Conditionals

```
{% if condition %}
Content to include if condition is true
{% endif %}
```

### Loops

```
{% for item in items %}
- {{ item }}
- Index: {{ loop.index }}
- Is First: {{ loop.first }}
- Is Last: {{ loop.last }}
{% endfor %}
```

## Installation

```bash
# Install from source
pip install -e .
```

## Testing

```bash
# Run tests
python -m pytest tests/ -v
```

## Project Structure

```
legal_doc_gen/
├── legal_doc_gen/
│   ├── __init__.py
│   └── legal_doc_generator.py
├── tests/
│   └── test_legal_doc_generator.py
├── README.md
└── setup.py
```

## License

MIT

- Easy-to-use template syntax tailored for legal documents
- Support for variables and complex expressions using dot notation
- Loop and condition control structures for dynamic content
- Template inheritance and includes for consistent document formatting
- Custom filters for legal-specific formatting (dates, numbers, etc.)
- Error handling and debugging tools
- Designed for creating legally compliant documents
- Support for document templates in various formats

## Installation

### From Source

```bash
# Navigate to the legal_doc_gen directory
cd legal_doc_gen

# Install the package
pip install -e .
```

### Requirements

The Legal Document Generator requires Python 3.6 or higher.

## Usage

### Basic Legal Document Example

```python
from legal_doc_gen import LegalDocumentGenerator

# Create a document generator instance
generator = LegalDocumentGenerator()

# Define a legal document template
template_content = """
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

# Define context data for the legal document
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

# Render the legal document
result = generator.render(template_content, context)
print(result)
```

### Using Legal Document Templates

```python
# Render from a legal document template file
result = generator.render_file("templates/agreement.md", context)
print(result)
```

### Advanced Features for Legal Documents

```python
# Legal document with complex loops and conditions
template_content = """
# LIST OF PROPERTIES

{% for property in properties %}
{% if property.owned %}
**Property {{ loop.index }}:**
- Address: {{ property.address }}
- Value: {{ property.value }}
- {% if property.mortgaged %}Mortgaged{% else %}Owned Outright{% endif %}

{% endif %}
{% endfor %}
"""

context = {
    "properties": [
        {"address": "123 Main St", "value": "$350,000", "owned": True, "mortgaged": True},
        {"address": "456 Oak Ave", "value": "$280,000", "owned": False, "mortgaged": False},
        {"address": "789 Pine Rd", "value": "$450,000", "owned": True, "mortgaged": False}
    ]
}

result = generator.render(template_content, context)
print(result)
```

## Project Structure

```
legal_doc_gen/
├── legal_doc_gen/              # Main package directory
│   ├── __init__.py            # Package initialization
│   └── legal_doc_generator.py # Main legal document generator implementation
├── templates/                 # Legal document templates
│   ├── agreement.md
│   ├── contract.txt
│   └── will_template.md
├── tests/                     # Test files
│   └── test_legal_doc_generator.py
├── README.md                  # This file
├── requirements.txt           # Dependencies
└── setup.py                   # Package setup
```

## Templates

The Legal Document Generator uses a simple yet powerful template syntax:

- **Variables**: `{{ variable.name }}` - Access variables using dot notation
- **If Statements**: `{% if condition %}...{% endif %}` - Conditional logic
- **For Loops**: `{% for item in items %}...{% endfor %}` - Loop through collections
- **Loop Information**: `{{ loop.index }}`, `{{ loop.first }}`, `{{ loop.last }}` - Loop metadata

## Examples

### Creating a Contract

```python
from legal_doc_gen import LegalDocumentGenerator

# Create generator instance
generator = LegalDocumentGenerator()

# Define contract template
template = """
# SERVICE CONTRACT

This Service Contract ("Contract") is entered into between:

- Service Provider: {{ provider.name }}, located at {{ provider.address }}
- Client: {{ client.name }}, located at {{ client.address }}

## SERVICES
Service Provider shall perform the following services:
{% for service in services %}
{{ loop.index }}. {{ service.description }}
{% endfor %}

## TERM
The term of this Contract shall commence on {{ start_date }} and continue until {{ end_date }}.

## COMPENSATION
Client agrees to pay Service Provider {{ payment.amount }} {{ payment.frequency }} for the services rendered.

## SIGNATURES
IN WITNESS WHEREOF, the parties hereto have executed this Contract as of the date first above written.

_________________________
{{ provider.name }}
Service Provider

_________________________
{{ client.name }}
Client
"""

# Define context
context = {
    "provider": {
        "name": "ABC Services Inc.",
        "address": "456 Business Ave, Cityville"
    },
    "client": {
        "name": "XYZ Corporation",
        "address": "789 Tech Street, Techville"
    },
    "services": [
        {"description": "Website development"},
        {"description": "SEO optimization"},
        {"description": "Monthly maintenance"}
    ],
    "start_date": "February 1, 2024",
    "end_date": "January 31, 2025",
    "payment": {
        "amount": "$5,000",
        "frequency": "monthly"
    }
}

# Render contract
contract = generator.render(template, context)
print(contract)
```

## Testing

To run the tests for the Legal Document Generator:

```bash
cd legal_doc_gen
python -m pytest tests/ -v
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
