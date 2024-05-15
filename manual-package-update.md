# Manual process to update project

1. Update software, test
2. update version in pyproject.toml
3. install python build "python3 -m pip install --upgrade build"
4. build software: "python3 -m build"
5. install twine "python3 -m pip install --upgrade twine"
6. upload new version: "python3 -m twine upload --repository pypi dist/*"
7. remove dist directory
