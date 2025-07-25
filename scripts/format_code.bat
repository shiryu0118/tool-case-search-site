@echo off
echo Formatting Python code...

REM Check if Black and isort are installed
where black >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Black not found. Installing...
    pip install black
)

where isort >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo isort not found. Installing...
    pip install isort
)

REM Format with Black
echo Running Black...
black .

REM Sort imports with isort
echo Running isort...
isort .

echo Code formatting complete!