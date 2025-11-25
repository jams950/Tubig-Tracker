@echo off
echo Enter your GitHub repository URL (e.g., https://github.com/username/tubig-tracker.git):
set /p REPO_URL=

echo Adding remote origin...
git remote add origin %REPO_URL%

echo Setting main branch...
git branch -M main

echo Pushing to GitHub...
git push -u origin main

echo Deployment files pushed successfully!
echo Now go to render.com to deploy your app.

pause