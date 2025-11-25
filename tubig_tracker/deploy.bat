@echo off
echo Starting deployment process...

echo.
echo 1. Adding all files to git...
git add .

echo.
echo 2. Committing changes...
git commit -m "Deploy: Fixed admin dashboard with working map pins and report counts"

echo.
echo 3. Pushing to main branch...
git push origin main

echo.
echo Deployment complete! 
echo Check your Render dashboard for build status.
echo.
pause