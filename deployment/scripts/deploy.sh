#!/bin/bash

# Production Deployment Script for Data Intelligence Platform
# Usage: ./deploy.sh [--staging|--production] [--skip-build] [--rollback]

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.prod.yml"
ENV_FILE="$PROJECT_DIR/.env.prod"
BACKUP_DIR="/var/backups/data-intelligence"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

# Parse arguments
ENVIRONMENT="production"
SKIP_BUILD=false
ROLLBACK=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --staging)
            ENVIRONMENT="staging"
            COMPOSE_FILE="$PROJECT_DIR/docker-compose.staging.yml"
            ENV_FILE="$PROJECT_DIR/.env.staging"
            shift
            ;;
        --production)
            ENVIRONMENT="production"
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --rollback)
            ROLLBACK=true
            shift
            ;;
        *)
            error "Unknown option: $1"
            exit 1
            ;;
    esac
done

log "Starting deployment to $ENVIRONMENT environment"

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Check if docker-compose is available
    if ! command -v docker-compose >/dev/null 2>&1; then
        error "docker-compose is not installed. Please install docker-compose and try again."
        exit 1
    fi
    
    # Check if environment file exists
    if [[ ! -f "$ENV_FILE" ]]; then
        error "Environment file not found: $ENV_FILE"
        error "Please create the environment file with required variables."
        exit 1
    fi
    
    # Check if compose file exists
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        error "Docker compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    
    # Check required directories
    sudo mkdir -p /var/lib/data-intelligence/{postgres,redis,uploads}
    sudo mkdir -p /var/log/data-intelligence
    sudo mkdir -p "$BACKUP_DIR"
    
    log "Prerequisites check completed"
}

# Create backup
create_backup() {
    if [[ "$ROLLBACK" == "true" ]]; then
        return 0
    fi
    
    log "Creating backup..."
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_path="$BACKUP_DIR/backup_$timestamp"
    
    mkdir -p "$backup_path"
    
    # Backup database
    if docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps postgres | grep -q "Up"; then
        info "Creating database backup..."
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T postgres \
            pg_dump -U app_user data_intelligence_prod > "$backup_path/database.sql"
    fi
    
    # Backup uploads
    if [[ -d "/var/lib/data-intelligence/uploads" ]]; then
        info "Creating uploads backup..."
        sudo tar -czf "$backup_path/uploads.tar.gz" -C /var/lib/data-intelligence uploads/
    fi
    
    # Backup configuration
    cp "$ENV_FILE" "$backup_path/"
    cp "$COMPOSE_FILE" "$backup_path/"
    
    log "Backup created: $backup_path"
    echo "$backup_path" > "$BACKUP_DIR/latest_backup"
}

# Rollback to previous version
rollback() {
    log "Rolling back to previous version..."
    
    if [[ ! -f "$BACKUP_DIR/latest_backup" ]]; then
        error "No backup found for rollback"
        exit 1
    fi
    
    local backup_path=$(cat "$BACKUP_DIR/latest_backup")
    
    if [[ ! -d "$backup_path" ]]; then
        error "Backup directory not found: $backup_path"
        exit 1
    fi
    
    # Stop current services
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
    
    # Restore database
    info "Restoring database..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d postgres
    sleep 10
    
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T postgres \
        psql -U app_user -d data_intelligence_prod < "$backup_path/database.sql"
    
    # Restore uploads
    if [[ -f "$backup_path/uploads.tar.gz" ]]; then
        info "Restoring uploads..."
        sudo tar -xzf "$backup_path/uploads.tar.gz" -C /var/lib/data-intelligence/
    fi
    
    log "Rollback completed"
    return 0
}

# Build images
build_images() {
    if [[ "$SKIP_BUILD" == "true" ]]; then
        log "Skipping build (--skip-build flag)"
        return 0
    fi
    
    log "Building Docker images..."
    
    # Build frontend
    info "Building frontend..."
    docker build -t data-intelligence-frontend:latest -f "$PROJECT_DIR/data-insider-4/Dockerfile" "$PROJECT_DIR/data-insider-4/"
    
    # Build backend
    info "Building backend..."
    docker build -t data-intelligence-backend:latest -f "$PROJECT_DIR/backend/Dockerfile" "$PROJECT_DIR/backend/"
    
    log "Docker images built successfully"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    # Start database first
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d postgres redis
    
    # Wait for database to be ready
    info "Waiting for database to be ready..."
    timeout=60
    while ! docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec postgres pg_isready -U app_user -d data_intelligence_prod >/dev/null 2>&1; do
        sleep 2
        timeout=$((timeout - 2))
        if [[ $timeout -le 0 ]]; then
            error "Database failed to start within timeout"
            exit 1
        fi
    done
    
    # Run migrations
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" run --rm backend \
        python -m alembic upgrade head
    
    log "Database migrations completed"
}

# Deploy services
deploy_services() {
    log "Deploying services..."
    
    # Pull external images
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull nginx postgres redis prometheus grafana node_exporter
    
    # Start all services
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    
    log "Services deployed"
}

# Health checks
perform_health_checks() {
    log "Performing health checks..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        info "Health check attempt $attempt/$max_attempts"
        
        # Check backend health
        if curl -f http://localhost/api/health >/dev/null 2>&1; then
            log "Backend health check passed"
            break
        fi
        
        if [[ $attempt -eq $max_attempts ]]; then
            error "Health checks failed after $max_attempts attempts"
            return 1
        fi
        
        sleep 10
        attempt=$((attempt + 1))
    done
    
    # Additional service checks
    info "Checking individual services..."
    
    local services=("nginx" "frontend" "backend" "postgres" "redis")
    for service in "${services[@]}"; do
        if docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps "$service" | grep -q "Up"; then
            info "✓ $service is running"
        else
            warn "✗ $service is not running properly"
        fi
    done
    
    log "Health checks completed"
}

# Cleanup old images
cleanup() {
    log "Cleaning up old images..."
    
    # Remove dangling images
    docker image prune -f
    
    # Remove old backups (keep last 7 days)
    find "$BACKUP_DIR" -name "backup_*" -type d -mtime +7 -exec rm -rf {} + 2>/dev/null || true
    
    log "Cleanup completed"
}

# Send notifications
send_notifications() {
    local status="$1"
    local message="$2"
    
    # This would integrate with your notification system (Slack, email, etc.)
    info "Deployment $status: $message"
    
    # Example: Send to Slack webhook
    # curl -X POST -H 'Content-type: application/json' \
    #     --data "{\"text\":\"🚀 Data Intelligence Platform deployment $status: $message\"}" \
    #     $SLACK_WEBHOOK_URL
}

# Main deployment flow
main() {
    local start_time=$(date +%s)
    
    if [[ "$ROLLBACK" == "true" ]]; then
        rollback
        exit 0
    fi
    
    check_prerequisites
    create_backup
    
    # Trap to handle failures
    trap 'error "Deployment failed! Check logs for details."; send_notifications "FAILED" "Deployment to $ENVIRONMENT failed"; exit 1' ERR
    
    build_images
    run_migrations
    deploy_services
    perform_health_checks
    cleanup
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log "Deployment to $ENVIRONMENT completed successfully in ${duration}s"
    send_notifications "SUCCESS" "Deployment to $ENVIRONMENT completed in ${duration}s"
}

# Run main function
main "$@"