# OPSYS_algo

## Windows setup

From the repository root, enter the simulator directory:

```powershell
cd OS-Simulator
```

Create and activate the virtual environment:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the simulator:

```powershell
python .\main.py
```

Open the Qt Designer form:

```powershell
.\.venv\Scripts\pyside6-designer.exe .\main_window.ui
```

If the environment is not activated, use the venv executables directly:

```powershell
.\.venv\Scripts\python.exe .\main.py
.\.venv\Scripts\pyside6-designer.exe .\main_window.ui
```