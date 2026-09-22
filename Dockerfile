# Start from an official, lightweight Python image -- avoids installing
# Python from scratch, and "slim" keeps the image smaller than the default.
FROM python:3.11-slim

# All following commands run from this folder inside the container.
WORKDIR /app

# Copy just requirements.txt first, then install -- this is a real
# optimization: Docker caches this step, so if you only change your code
# later (not your dependencies), it won't reinstall pandas every rebuild.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Now copy your actual pipeline code into the container.
COPY bronze.py .
COPY SILVER_to_gold.py .

# What runs automatically when someone starts a container from this image.
CMD ["sh", "-c", "python bronze.py && python SILVER_to_gold.py"]