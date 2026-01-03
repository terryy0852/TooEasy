"""
Legal Document Generator

A powerful template processing engine specifically designed for creating legal documents.
"""

import re
import os
from typing import Any, Dict, List, Tuple, Optional


class LegalDocumentGenerator:
    """
    A template processor designed for creating legal documents.
    
    This class provides functionality for processing templates with variables,
    conditionals, loops, and other features commonly needed in legal documents.
    """

    def __init__(self):
        """
        Initialize the LegalDocumentGenerator.
        """
        self.variable_pattern = re.compile(r'\{\{\s*(\w+(?:\.\w+)*)\s*\}\}')
        # Pattern to match any block tag
        self.block_pattern = re.compile(r'\{%\s*(\w+)\s*(.*?)\s*%\}', re.DOTALL)

    def _get_value(self, context: Dict[str, Any], key: str) -> Any:
        """
        Get a value from the context using dot notation.
        
        Args:
            context: The context dictionary
            key: The key to look up (can use dot notation)
            
        Returns:
            The value from the context
        """
        keys = key.split('.')
        value = context
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return ""
        return value

    def _replace_variables(self, content: str, context: Dict[str, Any]) -> str:
        """
        Replace variables in the content with values from the context.
        
        Args:
            content: The content to process
            context: The context dictionary
            
        Returns:
            The content with variables replaced
        """
        def replace_var(match: re.Match) -> str:
            key = match.group(1)
            return str(self._get_value(context, key))
        
        return self.variable_pattern.sub(replace_var, content)

    def _find_block_end(self, content: str, start_index: int, block_type: str) -> Optional[int]:
        """
        Find the matching end block for a given start block using a stack.
        
        Args:
            content: The content to search in
            start_index: The index after the start block
            block_type: The type of block ("if" or "for")
            
        Returns:
            The index of the matching end block, or None if not found
        """
        stack = [block_type]
        end_pattern = re.compile(r'\{%\s*(end\w+|\w+)\s*%\}', re.DOTALL)
        current_index = start_index
        
        while stack and current_index < len(content):
            match = end_pattern.search(content, current_index)
            if not match:
                break
            
            tag = match.group(1)
            if tag.startswith('end'):
                # End block found
                end_block_type = tag[3:]
                if stack[-1] == end_block_type:
                    stack.pop()
                    if not stack:
                        return match.start()
            elif tag in ['if', 'for']:
                # Start of a nested block
                stack.append(tag)
            
            current_index = match.end()
        
        return None

    def _process_blocks(self, content: str, context: Dict[str, Any]) -> str:
        """
        Process all blocks in the content using a stack-based approach for nested blocks.
        
        Args:
            content: The content to process
            context: The context dictionary
            
        Returns:
            The content with all blocks processed
        """
        result = []
        current_index = 0
        
        while True:
            # Find the next block tag
            match = self.block_pattern.search(content, current_index)
            if not match:
                # No more blocks, add the remaining content
                result.append(content[current_index:])
                break
            
            # Add content before the block
            result.append(content[current_index:match.start()])
            
            # Process the block
            block_type = match.group(1)
            block_args = match.group(2).strip()
            
            if block_type in ['if', 'for']:
                # Find the matching end block
                end_index = self._find_block_end(content, match.end(), block_type)
                if end_index is None:
                    # No matching end block, skip this block
                    result.append(content[match.start():match.end()])
                    current_index = match.end()
                    continue
                
                # Extract the block content
                block_content = content[match.end():end_index]
                
                if block_type == 'if':
                    # Process if block
                    try:
                        # Evaluate the condition using _get_value
                        condition_result = self._get_value(context, block_args)
                        if condition_result:
                            # Recursively process the content inside the if block
                            result.append(self._process_blocks(block_content, context))
                    except Exception:
                        pass  # Silently skip if there's an error in the condition
                
                elif block_type == 'for':
                    # Process for block
                    try:
                        # Parse the for loop arguments: "item in items"
                        item_var, _, list_var = block_args.partition(' in ')
                        item_var = item_var.strip()
                        list_var = list_var.strip()
                        
                        items = self._get_value(context, list_var)
                        if isinstance(items, list):
                            for_index = 0
                            for item in items:
                                local_context = context.copy()
                                local_context[item_var] = item
                                local_context['loop'] = {
                                    'index': for_index + 1,
                                    'index0': for_index,
                                    'first': for_index == 0,
                                    'last': for_index == len(items) - 1,
                                    'length': len(items)
                                }
                                
                                # Recursively process the content inside the for block
                                result.append(self._process_blocks(block_content, local_context))
                                for_index += 1
                    except Exception:
                        pass  # Silently skip if there's an error in the for loop
                
                # Move past the end block
                current_index = content.find('%}', end_index) + 2
            
            else:
                # Not a recognized block type, add it as-is
                result.append(content[match.start():match.end()])
                current_index = match.end()
        
        # Process variables in the final result
        final_content = ''.join(result)
        return self._replace_variables(final_content, context)

    def render(self, content: str, context: Dict[str, Any]) -> str:
        """
        Render the template content with the given context.
        
        Args:
            content: The template content
            context: The context dictionary
            
        Returns:
            The rendered content
        """
        if not content:
            return ""
        
        return self._process_blocks(content, context)

    def render_file(self, file_path: str, context: Dict[str, Any]) -> str:
        """
        Render a template file with the given context.
        
        Args:
            file_path: The path to the template file
            context: The context dictionary
            
        Returns:
            The rendered content
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Template file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.render(content, context)
