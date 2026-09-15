FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py memory.py ./
COPY calendar_app ./calendar_app
COPY wishlist ./wishlist

# OpenShift may run the container with an arbitrary non-root user.
RUN chgrp -R 0 /app && chmod -R g=u /app

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
