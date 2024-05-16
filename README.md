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
