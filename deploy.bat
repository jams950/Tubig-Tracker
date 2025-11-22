@echo off
echo Installing Git...
winget install --id Git.Git -e --source winget

echo Waiting for Git installation...
timeout /t 10

echo Refreshing PATH...
call refreshenv

echo Initializing Git repository...
git init

echo Adding all files...
git add .

echo Creating initial commit...
git commit -m "Initial commit - Tubig Tracker Django App"

echo Please create a repository on GitHub first, then run:
echo git remote add origin https://github.com/yourusername/tubig-tracker.git
echo git branch -M main
echo git push -u origin main

pause