# Splitting the Szeliski Textbook into Sections

This script takes the full Szeliski PDF (*Computer Vision: Algorithms and Applications*, 2nd Ed.) and splits it into one file per section (e.g., 5.1 Supervised Learning, 5.2 Unsupervised Learning). You end up with about 113 small PDFs instead of one 1,200-page book.

## What you need

- The Szeliski PDF file (`Szeliski_CVAABook_2ndEd.pdf`)
- Python installed on your computer
- A terminal (Terminal on Mac, PowerShell on Windows)

---

## Mac

### 1. Open Terminal

Press **Cmd + Space**, type `Terminal`, and hit Enter.

### 2. Navigate to the project folder

```
cd path/to/rose
```

Replace `path/to/rose` with wherever you downloaded or cloned the project. If you're not sure, drag the folder from Finder into the Terminal window and it will paste the path for you.

### 3. Create a virtual environment

A virtual environment is an isolated copy of Python where you can install packages without affecting anything else on your machine.

```
python3 -m venv .venv
```

This creates a `.venv` folder inside the project. You only need to do this once.

### 4. Activate the virtual environment

```
source .venv/bin/activate
```

Your terminal prompt will change to show `(.venv)` at the beginning. That means you're inside the virtual environment. Every `pip install` and `python3` command you run now uses this isolated copy.

### 5. Install the PDF library

```
pip install pymupdf
```

You only need to do this once (per virtual environment).

### 6. Run the script

Place the `Szeliski_CVAABook_2ndEd.pdf` file in the project root (the `rose/` folder), then run:

```
python3 scripts/split_szeliski.py
```

The split PDFs will appear in `readings/szeliski/`.

### 7. When you're done

Deactivate the virtual environment:

```
deactivate
```

Next time you want to run the script again, you only need steps 4 and 6 (activate and run). The virtual environment and the installed library are still there.

---

## Windows

### 1. Install Python (if you don't have it)

Open a PowerShell window (press **Win + X**, then click **Terminal** or **PowerShell**) and type:

```
python --version
```

If you see a version number (3.10 or higher), skip to step 2. If you get an error or it opens the Microsoft Store, install Python:

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download the latest Python 3 installer for Windows
3. Run the installer. **Check the box that says "Add Python to PATH"** before clicking Install. This is the most common mistake. If you skip this, nothing below will work without extra configuration.
4. Close and reopen PowerShell, then run `python --version` again to confirm.

### 2. Open PowerShell and navigate to the project folder

```
cd C:\path\to\rose
```

Replace with the actual path. If you're not sure, open the folder in File Explorer, click the address bar, and copy the path.

### 3. Create a virtual environment

```
python -m venv .venv
```

Note: on Windows, the command is `python`, not `python3`.

### 4. Activate the virtual environment

```
.venv\Scripts\Activate
```

Your prompt will change to show `(.venv)`. If you get an error about execution policies, run this first and then try again:

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 5. Install the PDF library

```
pip install pymupdf
```

### 6. Run the script

Place the `Szeliski_CVAABook_2ndEd.pdf` file in the project root (the `rose\` folder), then run:

```
python scripts/split_szeliski.py
```

The split PDFs will appear in `readings\szeliski\`.

### 7. When you're done

```
deactivate
```

Next time, you only need steps 4 and 6.

---

## Output

The script creates files named like:

```
szeliski-5.1-supervised-learning.pdf
szeliski-5.2-unsupervised-learning.pdf
szeliski-5.3-deep-neural-networks.pdf
```

Each file contains one section of the book. The chapter and section numbers match the table of contents.
