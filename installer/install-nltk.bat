@echo off
set PATH=C:\msys64\ucrt64\bin;C:\msys64\usr\bin;%PATH%
set LOG=C:\msys64\tmp\re-setup.log

echo === Installing NLTK and downloading corpora === >> %LOG%
"C:\msys64\ucrt64\bin\python.exe" "C:\msys64\tmp\bootstrap-nltk.py" >> %LOG% 2>&1

echo === NLTK done === >> %LOG%
