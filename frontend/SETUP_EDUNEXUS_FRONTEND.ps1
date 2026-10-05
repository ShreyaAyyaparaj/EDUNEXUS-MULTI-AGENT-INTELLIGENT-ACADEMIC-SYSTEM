# Run this from PowerShell.
# This replaces only the frontend folder and keeps the backend untouched.

$project = 'C:\Users\shreya\Desktop\EDUNEXUS'
$target = Join-Path $project 'frontend'
$backup = Join-Path $project ('frontend_backup_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))

if (Test-Path $target) { Rename-Item $target $backup }

# Extract this package so that its contents become the frontend folder.
# If this script is executed from the extracted package directory, use:
# Copy-Item -Recurse -Force . $target

New-Item -ItemType Directory -Force -Path $target | Out-Null
Copy-Item -Recurse -Force (Join-Path $PSScriptRoot '*') $target

Set-Location $target
npm install
npm run build
npm run dev
