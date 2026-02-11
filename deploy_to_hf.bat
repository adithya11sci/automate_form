@echo off
echo ==================================================
echo   🚀 Deploying AutoFill Pro to Hugging Face
echo ==================================================
echo.

cd hf_space

echo Setting remote URL (just in case)...
git remote set-url origin https://huggingface.co/spaces/Adithya11111111/autofill-pro

echo Adding files...
git add .

echo Committing...
git commit -m "Deploy latest version"

echo Pushing to Hugging Face...
echo (You may be asked to log in. Check for a popup window!)
git push

echo.
echo ==================================================
if %errorlevel% neq 0 (
    echo ❌ Deployment Failed! Check the error above.
    echo likely need to log in or configure Git credentials.
) else (
    echo ✅ Deployment Successful!
    echo Go to: https://huggingface.co/spaces/Adithya11111111/autofill-pro
)
echo ==================================================
pause
