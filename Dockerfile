# ---- base image ----
FROM python:3.11-slim

# ---- setup ----
WORKDIR /app
COPY requirements.txt ./        # create this file if you don’t have one yet
RUN pip install --no-cache-dir -r requirements.txt

# ---- copy source ----
COPY . .

# ---- expose & launch ----
EXPOSE 8501
CMD ["streamlit", "run", "main.py", "--server.port", "0", "--server.address", "0.0.0.0"]
