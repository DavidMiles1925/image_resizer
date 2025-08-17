Thank you for your interest in contributing to Batch Image Resizer!

Guidelines

- Please open an issue to discuss major changes or new features before starting work.
- Keep pull requests (PRs) focused and small — one logical change per PR.
- Use descriptive commit messages and reference related issues (e.g., "Fixes #123").

Development setup

1. Create a virtual environment and activate it:

   - python -m venv .venv
   - On Windows: .venv\Scripts\activate
   - On macOS/Linux: source .venv/bin/activate

2. Install dependencies:

   - pip install -r requirements.txt

3. Note about Tkinter:
   - On Debian/Ubuntu you may need to install the system package:
     sudo apt-get install python3-tk
   - The tkinterdnd2 package is optional and provides drag & drop support; if not installed, the app still runs without DnD.

Running the app

- Run the main script:
  - python <script_name>.py
    Replace <script_name>.py with your script filename (e.g. resizer.py).

Code style

- Follow PEP 8 where practical.
- Keep code readable and add docstrings for new functions.
- Add comments for non-obvious logic.

Testing

- There are no automated tests in the repository yet. Add tests in a tests/ folder if you introduce logic that should be validated automatically.

Submitting changes

1. Fork the repository and create a feature branch: git checkout -b feature/my-change
2. Commit your changes with clear messages.
3. Push your branch and open a pull request against the main branch.
4. Describe what your change does and why, and link any related issue numbers.

Reporting bugs & requesting features

- Open an issue with:
  - A clear title and description
  - Steps to reproduce
  - Your OS, Python version, and Pillow version
  - Any traceback or screenshots

License

- This project is licensed under the MIT License. See LICENSE for details.
