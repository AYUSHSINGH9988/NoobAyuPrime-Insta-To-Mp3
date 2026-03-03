FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install FFmpeg (Bohot zaruri hai yt-dlp se mp3 nikalne ke liye)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files to container
COPY . .

# Create downloads folder
RUN mkdir -p downloads

# Run the bot
CMD ["python", "main.py"]
