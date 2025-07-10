# HAL9001 Docker Management Script for PowerShell
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "logs", "status", "connect")]
    [string]$Action
)

switch ($Action) {
    "start" {
        Write-Host "Starting HAL9001 PostgreSQL container..." -ForegroundColor Green
        docker-compose up -d postgres
        Write-Host "Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        docker-compose logs postgres
    }
    "stop" {
        Write-Host "Stopping HAL9001 PostgreSQL container..." -ForegroundColor Red
        docker-compose down
    }
    "restart" {
        Write-Host "Restarting HAL9001 PostgreSQL container..." -ForegroundColor Yellow
        docker-compose restart postgres
    }
    "logs" {
        Write-Host "Showing PostgreSQL logs..." -ForegroundColor Cyan
        docker-compose logs -f postgres
    }
    "status" {
        Write-Host "Checking PostgreSQL status..." -ForegroundColor Blue
        docker-compose ps postgres
    }
    "connect" {
        Write-Host "Connecting to PostgreSQL..." -ForegroundColor Magenta
        docker-compose exec postgres psql -U hal_user -d hal9001_db
    }
}

# Usage information
if ($Action -eq $null) {
    Write-Host @"
Usage: .\docker-db.ps1 -Action <command>

Commands:
  start   - Start the PostgreSQL container
  stop    - Stop the PostgreSQL container  
  restart - Restart the PostgreSQL container
  logs    - Show PostgreSQL logs
  status  - Check container status
  connect - Connect to PostgreSQL CLI

Examples:
  .\docker-db.ps1 -Action start
  .\docker-db.ps1 -Action logs
"@ -ForegroundColor White
}
