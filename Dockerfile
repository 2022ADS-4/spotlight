FROM python:3.6
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN mkdir -p app
RUN python run_update_data.py --compress --demo-file
EXPOSE 80
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
