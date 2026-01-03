import unittest
import os
from template_processor import TemplateProcessor

class TestTemplateProcessor(unittest.TestCase):
    
    def setUp(self):
        """
        Set up a TemplateProcessor instance for each test.
        """
        self.processor = TemplateProcessor()
        
        # Create a test template file
        self.test_template_dir = "templates"
        self.test_template_file = os.path.join(self.test_template_dir, "test.txt")
        
        if not os.path.exists(self.test_template_dir):
            os.makedirs(self.test_template_dir)
        
        with open(self.test_template_file, 'w', encoding='utf-8') as f:
            f.write("Hello, {{ name }}! Welcome to {{ project }}.")
    
    def tearDown(self):
        """
        Clean up after each test.
        """
        if os.path.exists(self.test_template_file):
            os.remove(self.test_template_file)
        
        if os.path.exists(self.test_template_dir) and not os.listdir(self.test_template_dir):
            os.rmdir(self.test_template_dir)
    
    def test_variable_replacement(self):
        """
        Test basic variable replacement.
        """
        template = "Hello, {{ name }}! You are {{ age }} years old."
        context = {"name": "John", "age": 30}
        
        result = self.processor.render(template, context)
        self.assertEqual(result, "Hello, John! You are 30 years old.")
    
    def test_complex_variable_expression(self):
        """
        Test more complex variable expressions.
        """
        template = "The total is {{ price * quantity }} dollars."
        context = {"price": 10, "quantity": 5}
        
        result = self.processor.render(template, context)
        self.assertEqual(result, "The total is 50 dollars.")
    
    def test_if_block_true(self):
        """
        Test if block with true condition.
        """
        template = "{% if show_message %}Hello!{% endif %}"
        context = {"show_message": True}
        
        result = self.processor.render(template, context)
        self.assertEqual(result, "Hello!")
    
    def test_if_block_false(self):
        """
        Test if block with false condition.
        """
        template = "{% if show_message %}Hello!{% endif %}"
        context = {"show_message": False}
        
        result = self.processor.render(template, context)
        self.assertEqual(result, "")
    
    def test_for_loop(self):
        """
        Test for loop block.
        """
        template = """
        Items:
        {% for item in items %}
        - {{ item }}
        {% endfor %}
        """
        context = {"items": ["apple", "banana", "cherry"]}
        
        result = self.processor.render(template, context)
        expected = """
        Items:
        
        - apple
        
        - banana
        
        - cherry
        
        """
        self.assertEqual(result, expected)
    
    def test_for_loop_with_loop_info(self):
        """
        Test for loop with loop information.
        """
        template = """
        {% for item in items %}
        {{ loop.index }}. {{ item }}{% if not loop.last %},{% endif %}
        {% endfor %}
        """
        context = {"items": ["first", "second", "third"]}
        
        result = self.processor.render(template, context)
        expected = """
        
        1. first,
        
        2. second,
        
        3. third
        
        """
        self.assertEqual(result, expected)
    
    def test_nested_blocks(self):
        """
        Test nested blocks (if inside for).
        """
        template = """
        {% for item in items %}
            {% if item.active %}
            - {{ item.name }}
            {% endif %}
        {% endfor %}
        """
        context = {
            "items": [
                {"name": "Item 1", "active": True},
                {"name": "Item 2", "active": False},
                {"name": "Item 3", "active": True}
            ]
        }
        
        result = self.processor.render(template, context)
        expected = """
        
            
            - Item 1
            
        
            
        
            
            - Item 3
            
        
        """
        self.assertEqual(result, expected)
    
    def test_render_file(self):
        """
        Test rendering from a file.
        """
        context = {"name": "Alice", "project": "Template Processor"}
        
        result = self.processor.render_file(self.test_template_file, context)
        self.assertEqual(result, "Hello, Alice! Welcome to Template Processor.")
    
    def test_file_not_found(self):
        """
        Test that FileNotFoundError is raised when template file doesn't exist.
        """
        with self.assertRaises(FileNotFoundError):
            self.processor.render_file("non_existent_template.txt", {})

if __name__ == '__main__':
    unittest.main()
