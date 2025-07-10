#!/usr/bin/env pwsh
# PowerShell script to manage HAL9001 Docker environment

param(
    [Parameter(Position=0)]
    [ValidateSet("up", "down", "restart", "logs", "db-only", "api-only", "status")]
    [string]$Action = "up",
    
    [switch]$Build,
    [switch]$Detach
)

function Write-ColorText {
    param([string]$Text, [string]$Color = "White")
    Write-Host $Text -ForegroundColor $Color
}

Write-ColorText "🤖 HAL9001 Docker Management Script" "Cyan"
Write-ColorText "=====================================" "Cyan"

switch ($Action) {
    "up" {
        Write-ColorText "Starting HAL9001 services..." "Green"
        if ($Build) {
            docker-compose up --build -d
        } else {
            docker-compose up -d
        }
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ Services started successfully!" "Green"
            Write-ColorText "🌐 API available at: http://localhost:8000" "Yellow"
            Write-ColorText "🗄️  PostgreSQL available at: localhost:5432" "Yellow"
            Write-ColorText "📊 Open UI.html in your browser to use the application" "Yellow"
        }
    }
    
    "down" {
        Write-ColorText "Stopping HAL9001 services..." "Red"
        docker-compose down
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ Services stopped successfully!" "Green"
        }
    }
    
    "restart" {
        Write-ColorText "Restarting HAL9001 services..." "Yellow"
        docker-compose restart
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ Services restarted successfully!" "Green"
        }
    }
    
    "logs" {
        Write-ColorText "Showing logs for all services..." "Blue"
        docker-compose logs -f
    }
    
    "db-only" {
        Write-ColorText "Starting only PostgreSQL database..." "Green"
        docker-compose up postgres -d
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ Database started successfully!" "Green"
            Write-ColorText "🗄️  PostgreSQL available at: localhost:5432" "Yellow"
        }
    }
    
    "api-only" {
        Write-ColorText "Starting only HAL9001 API..." "Green"
        if ($Build) {
            docker-compose up --build hal9001-api -d
        } else {
            docker-compose up hal9001-api -d
        }
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ API started successfully!" "Green"
            Write-ColorText "🌐 API available at: http://localhost:8000" "Yellow"
        }
    }
    
    "status" {
        Write-ColorText "Checking service status..." "Blue"
        docker-compose ps
        Write-ColorText "`nDocker networks:" "Blue"
        docker network ls | Select-String "hal9001"
        Write-ColorText "`nContainer health:" "Blue"
        docker-compose exec postgres pg_isready -U hal_user -d hal9001_db 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ PostgreSQL is healthy" "Green"
        } else {
            Write-ColorText "❌ PostgreSQL is not responding" "Red"
        }
    }
}

Write-ColorText "`n🔧 Usage examples:" "Cyan"
Write-ColorText "  .\run-docker.ps1 up          # Start all services" "Gray"
Write-ColorText "  .\run-docker.ps1 up -Build   # Start with rebuild" "Gray"
Write-ColorText "  .\run-docker.ps1 db-only     # Start only database" "Gray"
Write-ColorText "  .\run-docker.ps1 logs        # View logs" "Gray"
Write-ColorText "  .\run-docker.ps1 status      # Check status" "Gray"
Write-ColorText "  .\run-docker.ps1 down        # Stop all services" "Gray"
