mkdir /tmp/app
cp requirements.txt /tmp/app
cp api.py /tmp/app
cp -R backends /tmp/app
cp -R configuration /tmp/app
cp -R ui/* /tmp/app
mkdir /tmp/app/data
cp -R data/intermediate /tmp/app/data
cp deploy/.buildpacks /tmp/app
cp deploy/Procfile /tmp/app
cp deploy/nginx.conf /tmp/app
pushd /tmp/
rm -rf /tmp/app/node_modules

tar czvf app.tar.gz --exclude='app/data/input' --exclude='app/.git' --exclude='app/.vscode' --exclude='app/venv' --exclude='app/node_modules' --exclude='app/__pycache__' --exclude='app/backends/__pycache__' --exclude='app/configuration/__pycache__' --exclude='app/.DS_Store' app
scalingo deploy --app adb-skills-finder app.tar.gz v0.0.7
