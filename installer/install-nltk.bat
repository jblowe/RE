@echo off
set PYTHON=C:\msys64\ucrt64\bin\python.exe
set PATH=C:\msys64\ucrt64\bin;C:\msys64\usr\bin;%PATH%
set LOG=C:\msys64\tmp\re-setup.log

echo === Installing NLTK === >> %LOG%

rem Determine the actual site-packages directory for this Python
for /f "tokens=*" %%p in ('"%PYTHON%" -c "import sysconfig; print(sysconfig.get_path(\"purelib\"))"') do set SITEPACKAGES=%%p
echo Installing NLTK to %SITEPACKAGES% >> %LOG%

"%PYTHON%" -m pip install --target="%SITEPACKAGES%" nltk >> %LOG% 2>&1
if errorlevel 1 (
  echo pip install nltk FAILED >> %LOG%
  exit /b 1
)

echo Downloading NLTK corpora... >> %LOG%
"%PYTHON%" -m nltk.downloader stopwords wordnet omw-1.4 >> %LOG% 2>&1
if errorlevel 1 (
  echo nltk.downloader FAILED >> %LOG%
  exit /b 1
)

echo NLTK setup complete. >> %LOG%
