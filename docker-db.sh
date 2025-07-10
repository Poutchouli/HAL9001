#!/bin/bash
# HAL9001 Docker Management Script

case "$1" in
    start)
        echo "Starting HAL9001 PostgreSQL container..."
        docker-compose up -d postgres
        echo "Waiting for PostgreSQL to be ready..."
        sleep 10
        docker-compose logs postgres
        ;;
    stop)
        echo "Stopping HAL9001 PostgreSQL container..."
        docker-compose down
        ;;
    restart)
        echo "Restarting HAL9001 PostgreSQL container..."
        docker-compose restart postgres
        ;;
    logs)
        echo "Showing PostgreSQL logs..."
        docker-compose logs -f postgres
        ;;
    status)
        echo "Checking PostgreSQL status..."
        docker-compose ps postgres
        ;;
    connect)
        echo "Connecting to PostgreSQL..."
        docker-compose exec postgres psql -U hal_user -d hal9001_db
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|status|connect}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the PostgreSQL container"
        echo "  stop    - Stop the PostgreSQL container"
        echo "  restart - Restart the PostgreSQL container"
        echo "  logs    - Show PostgreSQL logs"
        echo "  status  - Check container status"
        echo "  connect - Connect to PostgreSQL CLI"
        exit 1
        ;;
esac
