You are working at the repository root of the `skillhost` project.

Goal:
Prepare and publish the Python package `skillhost` version `0.1.0` to the real PyPI registry using Twine and the PyPI API token I provide below.

PyPI package name:
skillhost

Version:
0.1.0

PyPI API token:
<PYPI_API_TOKEN_HERE>

Important security rules:
- Never write the PyPI token into any repository file.
- Never write the PyPI token into pyproject.toml, README, RELEASE.md, GitHub Actions, .env, .pypirc, or shell scripts.
- Never commit the token.
- Never print the token.
- Use the token only as an environment variable for the upload command.
- After upload, do not persist the token anywhere.

Tasks:

1. Inspect the repository.
Confirm this is a Python package with a valid `pyproject.toml`.
If needed, update `pyproject.toml` so that:
- project name is exactly `skillhost`
- version is exactly `0.1.0`
- package uses a normal modern Python build backend
- CLI entry point exists:
  skillhost = "skillhost.cli:main"
- README is included as the long description
- Python version requirement is appropriate, preferably >=3.10
- project URLs include:
  Homepage = "https://skillhost.dev"
  Repository = "https://github.com/wang-chonghuan/skillhost"
  Issues = "https://github.com/wang-chonghuan/skillhost/issues"

2. Check the package locally.
Run:
python -m pip install --upgrade build twine

Then clean old builds:
rm -rf dist build *.egg-info src/*.egg-info

Run tests if tests exist:
python -m pytest

If pytest is not installed but tests exist, install pytest and run tests:
python -m pip install pytest
python -m pytest

3. Build the package.
Run:
python -m build

4. Validate the build.
Run:
python -m twine check dist/*

5. Inspect the generated distributions.
List:
ls -la dist

Confirm the generated files are for version 0.1.0 and package name skillhost.

6. Upload to real PyPI.
Use this exact pattern, with the provided token only as an environment variable:

TWINE_USERNAME="__token__" TWINE_PASSWORD="<PYPI_API_TOKEN_HERE>" python -m twine upload dist/*

Do not upload to TestPyPI. Upload to real PyPI.

7. After upload:
- Report whether the upload succeeded.
- If PyPI says the version already exists, explain that PyPI versions are immutable and the next release must bump to 0.1.1 or another new version.
- Do not retry with the same version if PyPI reports that the file or version already exists.
- Do not modify the token or store it anywhere.

8. Final verification:
Run:
python -m pip index versions skillhost

Then report the PyPI package URL:
https://pypi.org/project/skillhost/0.1.0/

Do not make unrelated changes.
Do not add GitHub Actions publishing in this task.
Do not configure Trusted Publishing in this task.
This is a one-time manual Twine upload using the provided token.