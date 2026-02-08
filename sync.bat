@echo off
cd /d C:\Users\Ashok\.openclaw\workspace\cron-dashboard
python monitor.py
git add .
git commit -m "Auto-update cron status"
git push origin main
