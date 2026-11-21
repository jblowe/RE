@echo off
set PATH=C:\msys64\ucrt64\bin;C:\msys64\usr\bin;%PATH%
set LOG=C:\msys64\tmp\re-setup.log

echo === Installing NLTK === >> %LOG%
"C:\msys64\ucrt64\bin\python.exe" -m pip install nltk >> %LOG% 2>&1

echo === Downloading NLTK corpora === >> %LOG%
"C:\msys64\ucrt64\bin\python.exe" -m nltk.downloader stopwords wordnet omw-1.4 >> %LOG% 2>&1

echo === NLTK done === >> %LOG%
