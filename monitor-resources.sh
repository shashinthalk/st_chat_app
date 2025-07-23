#!/bin/bash

# Resource Monitoring Script for Sentence Transformer API
# Monitor system resources and detect potential issues

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

CONTAINER_NAME="sentence-transformer-api"
LOG_FILE="logs/resource-monitor.log"

# Create log file if it doesn't exist
mkdir -p logs
touch $LOG_FILE

# Function to log with timestamp
log_with_timestamp() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# Function to check if container is running
check_container() {
    if ! docker ps | grep -q $CONTAINER_NAME; then
        echo -e "${RED}❌ Container $CONTAINER_NAME is not running${NC}"
        return 1
    fi
    return 0
}

# Function to get container stats
get_container_stats() {
    docker stats $CONTAINER_NAME --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}" 2>/dev/null
}

# Function to check memory usage and alert
check_memory_usage() {
    # Get container memory usage percentage
    MEM_PERCENT=$(docker stats $CONTAINER_NAME --no-stream --format "{{.MemPerc}}" 2>/dev/null | sed 's/%//')
    
    if [ -n "$MEM_PERCENT" ]; then
        # Convert to integer for comparison
        MEM_INT=$(echo $MEM_PERCENT | cut -d'.' -f1)
        
        if [ "$MEM_INT" -gt 85 ]; then
            echo -e "${RED}🚨 HIGH MEMORY USAGE: ${MEM_PERCENT}%${NC}"
            log_with_timestamp "HIGH MEMORY USAGE: ${MEM_PERCENT}%"
            return 1
        elif [ "$MEM_INT" -gt 70 ]; then
            echo -e "${YELLOW}⚠️ Elevated memory usage: ${MEM_PERCENT}%${NC}"
            log_with_timestamp "Elevated memory usage: ${MEM_PERCENT}%"
            return 2
        else
            echo -e "${GREEN}✅ Memory usage normal: ${MEM_PERCENT}%${NC}"
            return 0
        fi
    else
        echo -e "${RED}❌ Could not get memory stats${NC}"
        return 1
    fi
}

# Function to check API health
check_api_health() {
    HEALTH_URL="http://localhost:5001/health"
    
    if curl -f -s $HEALTH_URL >/dev/null 2>&1; then
        echo -e "${GREEN}✅ API health check passed${NC}"
        return 0
    else
        echo -e "${RED}❌ API health check failed${NC}"
        log_with_timestamp "API health check failed"
        return 1
    fi
}

# Function to check system resources
check_system_resources() {
    echo -e "${BLUE}📊 System Resource Overview:${NC}"
    
    # CPU usage
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
    echo "CPU Usage: ${CPU_USAGE}%"
    
    # Memory usage
    MEMORY_INFO=$(free -h | awk '/^Mem/ {printf "%.1f%% (%s/%s)", $3/$2*100, $3, $2}')
    echo "Memory Usage: $MEMORY_INFO"
    
    # Disk usage for root
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5 " (" $3 "/" $2 ")"}')
    echo "Disk Usage (/): $DISK_USAGE"
    
    # Load average
    LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}')
    echo "Load Average:$LOAD_AVG"
}

# Function to monitor container logs for errors
check_container_logs() {
    echo -e "${BLUE}📋 Recent Container Logs (last 10 lines):${NC}"
    docker logs $CONTAINER_NAME --tail=10 2>/dev/null | while read line; do
        if echo "$line" | grep -i -E "(error|timeout|kill|abort|fail)"; then
            echo -e "${RED}🚨 $line${NC}"
        elif echo "$line" | grep -i -E "(warn|warning)"; then
            echo -e "${YELLOW}⚠️ $line${NC}"
        else
            echo "$line"
        fi
    done
}

# Function to run continuous monitoring
continuous_monitor() {
    echo -e "${BLUE}🔍 Starting continuous monitoring (Ctrl+C to stop)...${NC}"
    
    while true; do
        clear
        echo "=== Sentence Transformer API Resource Monitor ==="
        echo "$(date)"
        echo ""
        
        if check_container; then
            echo -e "${BLUE}📊 Container Stats:${NC}"
            get_container_stats
            echo ""
            
            check_memory_usage
            MEM_STATUS=$?
            
            check_api_health
            API_STATUS=$?
            
            echo ""
            check_system_resources
            echo ""
            
            # Alert if issues detected
            if [ $MEM_STATUS -eq 1 ] || [ $API_STATUS -eq 1 ]; then
                echo -e "${RED}🚨 ISSUES DETECTED - Consider restarting the service${NC}"
                log_with_timestamp "Issues detected - High memory usage or API failure"
            fi
            
            echo ""
            echo "Press Ctrl+C to stop monitoring..."
        else
            echo -e "${RED}❌ Container not running. Start with: docker-compose -f docker-compose.production.yml up -d${NC}"
        fi
        
        sleep 10
    done
}

# Function to generate resource report
generate_report() {
    echo -e "${BLUE}📋 Generating Resource Report...${NC}"
    
    REPORT_FILE="logs/resource-report-$(date +%Y%m%d-%H%M%S).txt"
    
    {
        echo "=== Sentence Transformer API Resource Report ==="
        echo "Generated: $(date)"
        echo ""
        
        echo "=== Container Status ==="
        if check_container; then
            echo "Container Status: RUNNING"
            docker ps | grep $CONTAINER_NAME
        else
            echo "Container Status: NOT RUNNING"
        fi
        echo ""
        
        echo "=== Container Stats ==="
        get_container_stats
        echo ""
        
        echo "=== System Resources ==="
        free -h
        echo ""
        df -h
        echo ""
        top -bn1 | head -20
        echo ""
        
        echo "=== Recent Container Logs ==="
        docker logs $CONTAINER_NAME --tail=50 2>/dev/null
        echo ""
        
        echo "=== Docker Images ==="
        docker images | grep sentence
        echo ""
        
    } > $REPORT_FILE
    
    echo -e "${GREEN}✅ Report generated: $REPORT_FILE${NC}"
}

# Main menu
case "${1:-help}" in
    "monitor"|"m")
        continuous_monitor
        ;;
    "check"|"c")
        echo "=== Quick Resource Check ==="
        check_container && {
            get_container_stats
            check_memory_usage
            check_api_health
            check_system_resources
        }
        ;;
    "logs"|"l")
        check_container_logs
        ;;
    "report"|"r")
        generate_report
        ;;
    "help"|"h"|*)
        echo -e "${BLUE}Sentence Transformer API Resource Monitor${NC}"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  monitor, m    - Start continuous monitoring"
        echo "  check, c      - Quick resource check"
        echo "  logs, l       - Show recent container logs with error highlighting"
        echo "  report, r     - Generate detailed resource report"
        echo "  help, h       - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 monitor      # Start continuous monitoring"
        echo "  $0 check        # Quick health check"
        echo "  $0 logs         # View recent logs"
        ;;
esac 