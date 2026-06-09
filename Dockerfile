FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir streamlit yfinance ta pandas numpy requests scipy plotly

COPY . .

EXPOSE 7860

ENTRYPOINT ["streamlit", "run", "App.py", "--server.port=7860", "--server.address=0.0.0.0"]
