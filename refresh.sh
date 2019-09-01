#
# helper script to deploy REwww on pythonanywhere
#
cd ~/mysite/RE/
git pull -v 
git branch -v
cp -r REwww/* ..
cd ..

# need to make a few changes to source code on pythonanywhere

perl -i -pe 's/^run/# run/' bottle_app.py 
perl -i -pe 's/# application/application/' bottle_app.py

perl -i -pe 's/python/python3/' run_make.py
perl -i -pe "s/os.chdir\('..'\)/os.chdir('RE')/" run_make.py
perl -i -pe "s/os.chdir\('REwww'\)/os.chdir('..')/" run_make.py
perl -i -pe "s/os.chdir\(os.path.join\('..', 'src'\)\)/os.chdir(os.path.join('RE', 'src'))/" run_make.py
perl -i -pe "s/os.chdir\(os.path.join\('..', 'REwww'\)\)/os.chdir(os.path.join('..', '..'))/" run_make.py

# don't forget to restart...

