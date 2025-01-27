# Use a slim Python base image
FROM python:3.12-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements and application code
COPY requirements.txt ./
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose Streamlit's default port (8501)
EXPOSE 8501

# Set Streamlit environment variables (optional, configure for production)
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_HEADLESS=true

# Start the Streamlit app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
