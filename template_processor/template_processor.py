import re
import os

class TemplateProcessor:
    """
    A simple template processor that supports variables, conditions, and loops.
    """
    
    def __init__(self):
        self.variable_pattern = re.compile(r'\{\{\s*(.+?)\s*\}\}')
        self.block_start_pattern = re.compile(r'\{%\s*(.+?)\s*\%\}')
        self.block_end_pattern = re.compile(r'\{%\s*end(\w+)\s*\%\}')
    
    def render(self, template_content, context=None):
        """
        Render a template string with the given context.
        
        Args:
            template_content (str): The template content to render.
            context (dict, optional): The context data for the template.
            
        Returns:
            str: The rendered template.
        """
        if context is None:
            context = {}
        
        # Create a local namespace for evaluation
        local_namespace = context.copy()
        
        # Process template blocks (if/for) - this includes variable replacement
        result = self._process_blocks(template_content, local_namespace)
        
        return result
    
    def render_file(self, template_path, context=None):
        """
        Render a template file with the given context.
        
        Args:
            template_path (str): The path to the template file.
            context (dict, optional): The context data for the template.
            
        Returns:
            str: The rendered template.
        """
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        return self.render(template_content, context)
    
    def _process_blocks(self, content, context):
        """
        Process template blocks (if/for) recursively, including variable replacement.
        """
        # Find the first block start
        block_start_match = self.block_start_pattern.search(content)
        if not block_start_match:
            # No more blocks, just replace variables in the remaining content
            return self._replace_variables(content, context)
        
        # Extract block information
        block_start = block_start_match.group(0)
        block_content = block_start_match.group(1)
        block_type = block_content.split()[0].lower()
        
        # Find the corresponding block end
        block_end_pattern = re.compile(r'\{%\s*end' + block_type + r'\s*\%\}')
        block_end_match = block_end_pattern.search(content, block_start_match.end())
        
        if not block_end_match:
            raise SyntaxError(f"Unclosed block: {block_start}")
        
        # Extract the block body and the rest of the content
        block_body = content[block_start_match.end():block_end_match.start()]
        rest_content = content[block_end_match.end():]
        
        # Process the block based on its type
        if block_type == 'if':
            rendered_block = self._process_if_block(block_content, block_body, context)
        elif block_type == 'for':
            rendered_block = self._process_for_block(block_content, block_body, context)
        else:
            raise SyntaxError(f"Unknown block type: {block_type}")
        
        # Process variables in the content before the block
        before_block = self._replace_variables(content[:block_start_match.start()], context)
        
        # Recursively process the remaining content
        processed_rest = self._process_blocks(rest_content, context)
        
        # Combine the processed parts
        return before_block + rendered_block + processed_rest
    
    def _resolve_variable(self, expr, context):
        """
        Resolve a variable expression, supporting dot notation for dictionaries.
        
        Args:
            expr (str): The variable expression to resolve.
            context (dict): The context dictionary.
            
        Returns:
            The resolved value.
        """
        try:
            # First try direct evaluation
            return eval(expr, {}, context)
        except (AttributeError, KeyError):
            # If that fails, try to resolve dot notation manually
            parts = expr.split('.')
            value = context
            
            for part in parts:
                if isinstance(value, dict):
                    if part not in value:
                        raise KeyError(f"Key '{part}' not found in {value}")
                    value = value[part]
                else:
                    # Try attribute access as a fallback
                    if not hasattr(value, part):
                        raise AttributeError(f"'{type(value).__name__}' object has no attribute '{part}'")
                    value = getattr(value, part)
            
            return value
    
    def _process_if_block(self, block_content, block_body, context):
        """
        Process an if block.
        """
        # Extract the condition
        condition = block_content[2:].strip()
        
        # Evaluate the condition
        try:
            # Replace dot notation with dictionary access in the condition
            modified_condition = re.sub(r'(\w+)\.(\w+)', r"\1['\2']", condition)
            if eval(modified_condition, {}, context):
                # Process the block body recursively - this includes variable replacement
                return self._process_blocks(block_body, context)
            else:
                return ''
        except Exception as e:
            raise SyntaxError(f"Error evaluating if condition '{condition}': {e}")
    
    def _process_for_block(self, block_content, block_body, context):
        """
        Process a for block.
        """
        # Parse the for loop expression
        # Expected format: "for item in items"
        match = re.match(r'for\s+(\w+)\s+in\s+(.+)', block_content)
        if not match:
            raise SyntaxError(f"Invalid for loop syntax: {block_content}")
        
        item_var, iterable_expr = match.groups()
        
        # Evaluate the iterable
        try:
            # Replace dot notation with dictionary access in the iterable expression
            modified_iterable_expr = re.sub(r'(\w+)\.(\w+)', r"\1['\2']", iterable_expr)
            iterable = eval(modified_iterable_expr, {}, context)
        except Exception as e:
            raise SyntaxError(f"Error evaluating for loop iterable '{iterable_expr}': {e}")
        
        result = []
        
        # Process each item in the iterable
        for index, item in enumerate(iterable):
            # Create a new context for this iteration by copying the parent context
            loop_context = context.copy()
            loop_context[item_var] = item
            
            # Add loop information
            loop_context['loop'] = {
                'index': index + 1,
                'index0': index,
                'first': index == 0,
                'last': index == len(iterable) - 1,
                'length': len(iterable)
            }
            
            # Process the block body with the new context - this includes variable replacement
            processed_body = self._process_blocks(block_body, loop_context)
            result.append(processed_body)
        
        return ''.join(result)
    
    def _replace_variables(self, content, context):
        """
        Replace variables in the content with their values from the context.
        """
        def replace_variable(match):
            variable_expr = match.group(1).strip()
            try:
                # Replace dot notation with dictionary access in the variable expression
                modified_expr = re.sub(r'(\w+)\.(\w+)', r"\1['\2']", variable_expr)
                return str(eval(modified_expr, {}, context))
            except Exception as e:
                raise ValueError(f"Error evaluating variable '{variable_expr}': {e}")
        
        return self.variable_pattern.sub(replace_variable, content)
