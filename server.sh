if [[ ! -d "venv" ]]; then
    python3 -m venv venv
    . venv/bin/activate
    pip install -r requirements.txt
    pip install -r dev-requirements.txt
fi

. venv/bin/activate
uvicorn api:app --reload
