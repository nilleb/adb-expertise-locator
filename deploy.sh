pushd ui
rm -rf dist
yarn build
popd
mkdir /tmp/app
cp requirements.txt /tmp/app
cp api.py /tmp/app
cp nltk.txt /tmp/app
cp -R backends /tmp/app
cp -R configuration /tmp/app
rm -rf /tmp/app/ui
mkdir /tmp/app/ui
cp -R ui/dist /tmp/app/ui/dist
mkdir /tmp/app/data
cp -R data/intermediate /tmp/app/data
mkdir /tmp/app/data/faces
cp data/faces/all_faces_urls.json /tmp/app/data/faces
cp deploy/Procfile /tmp/app
pushd /tmp/

rm app.tar.gz
tar czvf app.tar.gz --exclude='app/data/input' --exclude='app/.git' --exclude='app/.vscode' --exclude='app/venv' --exclude='app/node_modules' --exclude='app/__pycache__' --exclude='app/backends/__pycache__' --exclude='app/configuration/__pycache__' --exclude='app/.DS_Store' app
scalingo deploy --app adb-skills-finder app.tar.gz v0.0.8
popd
