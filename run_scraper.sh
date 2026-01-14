#!/bin/bash

# Run the DI.se scraper during market hours only
# Swedish market hours: 9:00 - 17:30 CET/CEST, Monday-Friday

# Get current hour and minute
HOUR=$(date +%H)
MINUTE=$(date +%M)
DAY=$(date +%u)  # 1=Monday, 7=Sunday

# Check if it's a weekday (1-5)
if [ $DAY -ge 6 ]; then
    echo "Weekend - skipping scrape"
    exit 0
fi

# Check if within market hours (9:00 - 17:30)
if [ $HOUR -lt 9 ] || [ $HOUR -gt 17 ]; then
    echo "Outside market hours - skipping scrape"
    exit 0
fi

# If it's 17:xx, only run if minute <= 30
if [ $HOUR -eq 17 ] && [ $MINUTE -gt 30 ]; then
    echo "Market closed - skipping scrape"
    exit 0
fi

# Run the scraper
cd /home/onelock/workspace/stockster/di_scraper
/home/onelock/workspace/stockster/.stockster_venv/bin/python3 scrape_di.py
