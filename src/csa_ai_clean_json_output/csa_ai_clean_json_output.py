#!/usr/bin/env python3

import json
import argparse
import re
import os
import sys

class CleanAIJsonOutput:
    def __init__(self, input_source=None, output_file=None, input_type='file'):
        self.input_source = input_source
        self.output_file = output_file
        self.input_type = input_type
        self.start_character = None

    def is_valid_json(self, data):
        try:
            json.loads(data)
            return True, None
        except json.JSONDecodeError as e:
            return False, str(e)

    def unescape_json_quotes(self, data):
        # This regex looks for escaped quotes that are not already within a string
        return re.sub(r'(?<!\\)\\(?=["\\\w])"', '"', data)

    def replace_unicode_characters(self, data):
        unicode_replacements = {
            '\u200b': '',  # Zero Width Space
            '\u200c': '',  # Zero Width Non-Joiner
            '\u200d': '',  # Zero Width Joiner
            '\u2060': '',  # Word Joiner
            '\ufeff': ''   # Zero Width No-Break Space
        }

        def replace_chars(obj):
            if isinstance(obj, str):
                for key, value in unicode_replacements.items():
                    obj = obj.replace(key, value)
            elif isinstance(obj, list):
                obj = [replace_chars(item) for item in obj]
            elif isinstance(obj, dict):
                obj = {k: replace_chars(v) for k, v in obj.items()}
            return obj

        return replace_chars(data)

    def replace_smart_quotes(self, data):
        def replace_quotes(obj):
            if isinstance(obj, str):
                obj = obj.replace('"', '"').replace('"', '"')
                obj = obj.replace(''', "'").replace(''', "'")
            elif isinstance(obj, list):
                obj = [replace_quotes(item) for item in obj]
            elif isinstance(obj, dict):
                obj = {k: replace_quotes(v) for k, v in obj.items()}
            return obj

        return replace_quotes(data)

    def remove_comments(self, data):
        pattern = re.compile(r'//.*?$|/\*.*?\*/|#.*?$', re.MULTILINE | re.DOTALL)
        return re.sub(pattern, '', data)

    def remove_extra_at_start_of_file(self, raw_data):
        match = re.search(r'[{[]', raw_data)
        if match:
            self.start_character = raw_data[match.start()]
            return raw_data[match.start():]
        return raw_data

    def remove_extra_at_end_of_file(self, raw_data):
        if self.start_character == '{':
            end_character = '}'
        elif self.start_character == '[':
            end_character = ']'
        else:
            return raw_data

        last_occurrence = raw_data.rfind(end_character)
        if last_occurrence != -1:
            return raw_data[:last_occurrence + 1]
        return raw_data

    def fix_trailing_commas(self, data):
        fixed_content = re.sub(r',(\s*[\]}])', r'\1', data)
        return fixed_content

    def fix_unescaped_quotes_in_string(self, string):
        def replace(match):
            return match.group(1) + '\\"' + match.group(2)
        
        pattern = re.compile(r'([^\\])"([^:,}\]]*[^\\])"')
        return re.sub(pattern, replace, string)

    def fix_unescaped_quotes_in_json(self, data):
        if isinstance(data, dict):
            return {key: self.fix_unescaped_quotes_in_json(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.fix_unescaped_quotes_in_json(item) for item in data]
        elif isinstance(data, str):
            return self.fix_unescaped_quotes_in_string(data)
        else:
            return data

    def replace_escaped_newlines(self, data):
        return re.sub(r'(?<!\\)\\n', '\n', data)

    def clean(self, data):
        data = self.replace_unicode_characters(data)
        data = self.replace_smart_quotes(data)
        data = self.fix_unescaped_quotes_in_json(data)
        return data

    def process(self):
        if self.input_type == 'file':
            with open(self.input_source, 'r') as infile:
                raw_data = infile.read()
        elif self.input_type == 'string':
            raw_data = self.input_source
        else:
            raise ValueError("Invalid input type. Must be 'file' or 'string'.")

        # Remove extra characters at the start and end of the file
        raw_data = self.remove_extra_at_start_of_file(raw_data)
        raw_data = self.remove_extra_at_end_of_file(raw_data)

        # Unescape JSON quotes
        raw_data = self.unescape_json_quotes(raw_data)
    
        # Normalize line breaks to Unix style
        raw_data = raw_data.replace('\r\n', '\n').replace('\r', '\n')

        # Replace escaped newlines with actual newlines
        raw_data = self.replace_escaped_newlines(raw_data)

        # Remove comments
        raw_data = self.remove_comments(raw_data)

        # Fix smart quotes before other processing
        raw_data = self.replace_smart_quotes(raw_data)

        # Fix trailing commas
        raw_data = self.fix_trailing_commas(raw_data)

        is_valid, error_message = self.is_valid_json(raw_data)
        if not is_valid:
            raise ValueError(f"Invalid JSON in input data. Error details: {error_message}\n\nProblematic JSON:\n{raw_data}")

        data = json.loads(raw_data)
        cleaned_data = self.clean(data)
        cleaned_json = json.dumps(cleaned_data, indent=2)

        is_valid, error_message = self.is_valid_json(cleaned_json)
        if not is_valid:
            raise ValueError(f"The cleaned JSON is invalid. Error details: {error_message}\n\nProblematic JSON:\n{cleaned_json}")

        if self.input_type == 'file':
            with open(self.output_file, 'w') as outfile:
                outfile.write(cleaned_json)
        elif self.input_type == 'string':
            return cleaned_json

def main():
    parser = argparse.ArgumentParser(description="Clean JSON output from AI systems")
    parser.add_argument('--input', type=str, required=True, help='Input JSON file or string')
    parser.add_argument('--output', type=str, required=False, help='Output JSON file (required if input type is file)')
    parser.add_argument('--type', type=str, choices=['file', 'string'], required=True, help='Type of input: file or string')

    args = parser.parse_args()

    cleaner = CleanAIJsonOutput(input_source=args.input, output_file=args.output, input_type=args.type)
    if args.type == 'file' and not args.output:
        parser.error("--output is required when --type is 'file'")

    try:
        result = cleaner.process()
        if args.type == 'string':
            print(result)
    except ValueError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
    
