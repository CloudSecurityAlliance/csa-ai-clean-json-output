#!/usr/bin/env python3

# csa_ai_clean_json_output.py

import json
import argparse
import re

class clean_ai_json_output:
  def __init__(self, input_source=None, output_file=None, input_type='file'):
    self.input_source = input_source
    self.output_file = output_file
    self.input_type = input_type
    self.start_character = None

  def is_valid_json(self, data):
    try:
      json.loads(data)
      return True
    except ValueError:
      return False

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

  def replace_smart_quotes_at_end_of_line(self, data):
    def replace_quotes(obj):
      if isinstance(obj, str):
        obj = re.sub('”$', '"', obj, flags=re.MULTILINE)
      elif isinstance(obj, list):
        obj = [replace_quotes(item) for item in obj]
      elif isinstance(obj, dict):
        obj = {k: replace_quotes(v) for k, v in obj.items()}
      return obj
    
    return replace_quotes(data)
  
  def replace_smart_quotes_at_start_of_line(self, data):
    def replace_quotes(obj):
      if isinstance(obj, str):
        obj = re.sub(r'^\s*“', '"', obj, flags=re.MULTILINE)
      elif isinstance(obj, list):
        obj = [replace_quotes(item) for item in obj]
      elif isinstance(obj, dict):
        obj = {k: replace_quotes(v) for k, v in obj.items()}
      return obj
    
    return replace_quotes(data)
  
  def remove_extra_at_start_of_file(self, raw_data):
    match = re.search(r'[{[\"]', raw_data)
    if match:
      self.start_character = raw_data[match.start()]
      return raw_data[match.start():]
    return raw_data

  def remove_extra_at_end_of_file(self, raw_data):
    if self.start_character:
      if self.start_character == '{':
        end_character = '}'
      elif self.start_character == '[':
        end_character = ']'
      elif self.start_character == '"':
        end_character = '"'
      else:
        return raw_data
      
      end_pos = raw_data.rfind(end_character)
      if end_pos != -1:
        return raw_data[:end_pos + 1]
    return raw_data

  def clean(self, data):
    data = self.replace_unicode_characters(data)
    data = self.replace_smart_quotes_at_end_of_line(data)
    data = self.replace_smart_quotes_at_start_of_line(data)
    # Add additional cleaning steps here if needed
    return data

  def process(self):
    if self.input_type == 'file':
      with open(self.input_source, 'r') as infile:
        raw_data = infile.read()
    elif self.input_type == 'string':
      raw_data = self.input_source
    else:
      raise ValueError("Invalid input type. Must be 'file' or 'string'.")
    
    if not self.is_valid_json(raw_data):
      raw_data = self.remove_extra_at_start_of_file(raw_data)
      raw_data = self.remove_extra_at_end_of_file(raw_data)
      raw_data = self.replace_smart_quotes_at_start_of_line(raw_data)
      raw_data = self.replace_smart_quotes_at_end_of_line(raw_data)
      
      if not self.is_valid_json(raw_data):
        raise ValueError("Invalid JSON in input data.")
    
    data = json.loads(raw_data)
    cleaned_data = self.clean(data)
    cleaned_json = json.dumps(cleaned_data, indent=2)
    
    if not self.is_valid_json(cleaned_json):
      raise ValueError("The cleaned JSON is invalid.")

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
  
  cleaner = clean_ai_json_output(input_source=args.input, output_file=args.output, input_type=args.type)
  if args.type == 'file' and not args.output:
    parser.error("--output is required when --type is 'file'")
  
  result = cleaner.process()
  
  if args.type == 'string':
    print(result)

if __name__ == '__main__':
  main()
