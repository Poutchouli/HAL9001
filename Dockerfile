# ---- Builder Stage ----
# Use a full Python image to install dependencies, which may require build tools.
FROM python:3.11 as builder

# Set the working directory in the container
WORKDIR /app

# Create and activate a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only the requirements file to leverage Docker's layer caching.
# This layer is only rebuilt if the requirements change.
COPY ./hal9001-backend/requirements.txt .

# Install the Python dependencies into the virtual environment
RUN pip install --no-cache-dir -r requirements.txt


# ---- Final Stage ----
# Use a lightweight "slim" image for the final production container.
FROM python:3.11-slim

WORKDIR /app

# Copy the virtual environment with installed packages from the builder stage.
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application source code into the final image.
COPY ./hal9001-backend /app

# Copy the UI.html file to the parent directory where the app expects it
COPY ./UI.html /UI.html

# Command to run the application using the Uvicorn server.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]