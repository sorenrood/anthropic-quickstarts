# Windows startup script for Computer Use Demo
param(
    [string]$AnthropicApiKey
)

# Check if running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Please run this script as Administrator"
    exit 1
}

# Create and activate virtual environment
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r computer_use_demo/requirements.txt

# Set environment variables
$env:ANTHROPIC_API_KEY = $AnthropicApiKey
$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false"

# Start Streamlit
Start-Process -NoNewWindow python -ArgumentList "-m streamlit run computer_use_demo/streamlit.py"

Write-Host "✨ Computer Use Demo is ready!"
Write-Host "➡️  Open http://localhost:8501 in your browser to begin"
