# CleanInbox AI - Windows Setup Script (PowerShell)
# Chay script nay de cai dat moi truong phat trien

Write-Host ""
Write-Host "CleanInbox AI - Environment Setup" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
Write-Host ""

# Buoc 1: Kiem tra Python
Write-Host "[1/6] Kiem tra Python..." -ForegroundColor Cyan
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $output = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            Write-Host "  OK: $output (lenh: $cmd)" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $pythonCmd) {
    Write-Host "  FAIL: Python chua duoc cai dat!" -ForegroundColor Red
    Write-Host "  -> Tai Python 3.11+ tai: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  -> Nho tich 'Add Python to PATH' khi cai dat!" -ForegroundColor Yellow
    exit 1
}

# Buoc 2: Tao Virtual Environment
Write-Host ""
Write-Host "[2/6] Tao Virtual Environment (.venv)..." -ForegroundColor Cyan
if (Test-Path ".venv") {
    Write-Host "  .venv da ton tai - bo qua tao moi" -ForegroundColor Yellow
} else {
    & $pythonCmd -m venv .venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK: Da tao .venv" -ForegroundColor Green
    } else {
        Write-Host "  FAIL: Khong tao duoc .venv" -ForegroundColor Red
        exit 1
    }
}

# Buoc 3: Kich hoat venv va cai packages
Write-Host ""
Write-Host "[3/6] Cai dat Python packages..." -ForegroundColor Cyan
$pipPath = ".venv\Scripts\pip.exe"
if (-not (Test-Path $pipPath)) {
    Write-Host "  FAIL: Khong tim thay pip trong .venv" -ForegroundColor Red
    exit 1
}

& $pipPath install --upgrade pip --quiet
& $pipPath install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK: Da cai xong tat ca packages" -ForegroundColor Green
} else {
    Write-Host "  FAIL: Loi khi cai packages" -ForegroundColor Red
    exit 1
}

# Buoc 4: Copy .env
Write-Host ""
Write-Host "[4/6] Cau hinh moi truong..." -ForegroundColor Cyan
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  OK: Da tao .env tu .env.example" -ForegroundColor Green
    Write-Host "  -> Mo .env va dien API keys cua ban!" -ForegroundColor Yellow
} else {
    Write-Host "  .env da ton tai - giu nguyen" -ForegroundColor Yellow
}

# Buoc 5: Kiem tra Docker
Write-Host ""
Write-Host "[5/6] Kiem tra Docker..." -ForegroundColor Cyan
try {
    $dockerVer = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK: $dockerVer" -ForegroundColor Green
    }
} catch {
    Write-Host "  WARN: Docker chua cai - can cho production deploy" -ForegroundColor Yellow
    Write-Host "  -> Tai tai: https://www.docker.com/products/docker-desktop/" -ForegroundColor Gray
}

# Buoc 6: Kiem tra frontend server
Write-Host ""
Write-Host "[6/6] Kiem tra Node.js (cho frontend serve)..." -ForegroundColor Cyan
try {
    $nodeVer = node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK: Node.js $nodeVer" -ForegroundColor Green
    }
} catch {
    Write-Host "  WARN: Node.js chua cai" -ForegroundColor Yellow
}

# Tom tat
Write-Host ""
Write-Host "===================================" -ForegroundColor Green
Write-Host "Setup hoan tat!" -ForegroundColor Green
Write-Host ""
Write-Host "Lenh tiep theo:" -ForegroundColor White
Write-Host "  Kich hoat venv    : .venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "  Chay backend      : uvicorn backend.main:app --reload" -ForegroundColor Cyan
Write-Host "  API docs          : http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Full Docker stack : docker compose up --build" -ForegroundColor Cyan
Write-Host "  Frontend          : npx serve . -p 3999" -ForegroundColor Cyan
Write-Host ""
Write-Host "Xem them: README.md" -ForegroundColor Gray
Write-Host ""
