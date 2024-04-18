#FROM nvcr.io/nvidia/modulus/modulus:24.01    

FROM python:3.8
## base image
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
COPY conf conf
COPY modulus modulus
COPY app.py app.py
# Expose the port that Streamlit runs on
EXPOSE 8000

# Run the Streamlit app
#CMD ["streamlit", "hello", "--server.address", "0.0.0.0", "--server.port", "8000"]
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8000"]
