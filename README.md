# ForTrace Chatbot

This chatbot converts a forensic scenario into a YAML file for ForTrace.

## How to use

You can run the app either locally or with `docker`. Ensure to install all dependencies when running locally.

Add your OpenAI API key to `./.streamlit/secrets.toml`.

### Run app locally

Run app locally:
```bash
python -m venv env
source env/bin/activate
pip3 install -r requirements.txt
streamlit run app.py
```

### Run with docker

The configuration is mounted into the container.  
You can change the configuration and reload rerun the streamlit app by pressing `r`.
```bash
docker build -t streamlit-app .
docker run -p 8501:8501 -v $(pwd)/configuration.yaml:/app/configuration.yaml streamlit-app
```

Go to `http://localhost:8501`.

Alternatively you can mount the whole application and enable hot-reload.
Changes in the code will immediately take effect after pressing `r`.
```bash
docker build -t streamlit-app .
docker run -p 8501:8501 -v $(pwd):/app streamlit-app
```