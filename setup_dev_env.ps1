Write-Host "Setting up Student Attendance System Environment..." -ForegroundColor Cyan

# Check if python is installed
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not installed or not in PATH." -ForegroundColor Red
    exit
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
$env:VIRTUAL_ENV = "$PWD\venv"
$env:Path = "$PWD\venv\Scripts;" + $env:Path

Write-Host "Installing dependencies..." -ForegroundColor Yellow
# Using pip from venv
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host "Setup Complete. You can now run 'python app.py' inside the virtual environment." -ForegroundColor Green
Write-Host "Starting the application..." -ForegroundColor Magenta
python app.py
