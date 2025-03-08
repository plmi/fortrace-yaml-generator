FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the files in the current directory to the container
COPY . ./

EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "app.py"]