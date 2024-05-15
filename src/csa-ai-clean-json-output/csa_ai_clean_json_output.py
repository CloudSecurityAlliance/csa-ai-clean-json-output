#!/usr/bin/env python3

import json
import argparse
import re

class clean_ai_json_output:
  def __init__(self, input_file=None, output_file=None):
    self.input_file = input_file
    self.output_file = output_file
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

  def process_files(self):
    with open(self.input_file, 'r') as infile:
      raw_data = infile.read()
      
      if not self.is_valid_json(raw_data):
        raw_data = self.remove_extra_at_start_of_file(raw_data)
        raw_data = self.remove_extra_at_end_of_file(raw_data)
        raw_data = self.replace_smart_quotes_at_start_of_line(raw_data)
        raw_data = self.replace_smart_quotes_at_end_of_line(raw_data)
        
        if not self.is_valid_json(raw_data):
          raise ValueError(f"Invalid JSON in input file: {self.input_file}")

      data = json.loads(raw_data)
      cleaned_data = self.replace_unicode_characters(data)
    
    with open(self.output_file, 'w') as outfile:
      json.dump(cleaned_data, outfile, indent=2)

def main():
  parser = argparse.ArgumentParser(description="Clean JSON output from AI systems")
  parser.add_argument('--input', type=str, required=True, help='Input JSON file')
  parser.add_argument('--output', type=str, required=True, help='Output JSON file')
  
  args = parser.parse_args()
  
  cleaner = clean_ai_json_output(input_file=args.input, output_file=args.output)
  cleaner.process_files()

if __name__ == '__main__':
  main()
