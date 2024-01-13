FROM python:3.10

RUN useradd --create-home  --system --uid=99 appuser 

# Create and step in the project directory inside the container
WORKDIR /server-monitor

# Copy the requirements to the container
COPY requirements.txt .

# Install all the requirements
RUN pip install -r requirements.txt

# Copy all project contents to the project directory inside the container
COPY . .

USER appuser

# Set the entrypoint to the bash script
ENTRYPOINT ["python3", "/server-monitor/server_monitor/__main__.py"]
