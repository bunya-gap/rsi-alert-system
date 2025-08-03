@echo off
echo RSI Alert System Scheduler Setup
echo.

echo Creating Windows Task Scheduler entry...
echo Task Name: RSI_Alert_Daily
echo Schedule: Daily at 16:35 (After market close)
echo.

schtasks /create ^
/tn \"RSI_Alert_Daily\" ^
/tr \"python %~dp0main.py\" ^
/sc daily ^
/st 16:35 ^
/f

if %errorlevel% equ 0 (
    echo.
    echo ✅ Task created successfully!
    echo.
    echo The RSI Alert System will now run automatically:
    echo - Every day at 16:35 (4:35 PM)
    echo - Monitoring TECL and SOXL
    echo - Sending LINE alerts when RSI crosses thresholds
    echo.
    echo To test immediately, run:
    echo python main.py
    echo.
    echo To view scheduled tasks:
    echo schtasks /query /tn \"RSI_Alert_Daily\"
    echo.
    echo To delete the task:
    echo schtasks /delete /tn \"RSI_Alert_Daily\" /f
) else (
    echo.
    echo ❌ Failed to create task. Please run as Administrator.
)

echo.
pause
