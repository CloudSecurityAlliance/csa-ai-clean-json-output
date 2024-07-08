# Cloud Security Alliance AI Clean JSON Output

This library is not yet packaged, this is planned but there appears to be an issue with my PyPi account.

You can get this library at https://pypi.org/project/csa-ai-clean-json-output/ or via:

```
pip install csa_ai_clean_json_output
```

This Python library (csa-ai-clean-json-output) provides a simple class to clean AI JSON output with common problems:

* JSON escaped with json and back ticks
* JSON with a ranndom smart quote at the end of a string
* JSON with unicode characters

## Examples:

Using this as a library:

```

from csa_ai_clean_json_output import clean_ai_json_output

cleaner = clean_ai_json_output(input_source=input_string, input_type='string')
cleaned_json = cleaner.process()
```

Using this as a command line tool by calling it one a file:

```
python csa_ai_clean_json_output.py --input input.json --output output.json --type file
```

Or on a string:

```
python csa_ai_clean_json_output.py --input '{"some":"json"}' --type string
```

## Future notes:

This library shouldn't be needed long term:

chatgpt:

To prevent these errors and improve model performance, when using gpt-4o, gpt-4-turbo, or gpt-3.5-turbo, you can set response_format to { "type": "json_object" } to enable JSON mode. When JSON mode is enabled, the model is constrained to only generate strings that parse into valid JSON object.

https://platform.openai.com/docs/guides/text-generation/json-mode

claude:

Not possible? Closest piece of documentation:

https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/increase-consistency#example-standardizing-customer-feedback

gemini:

Use response_schema 

https://ai.google.dev/gemini-api/docs/json-mode
