FROM python:3.5-slim
MAINTAINER JS TAN "js@hellovelocity.com"
WORKDIR /app
ADD app /app
RUN apt-get update -y \
    && apt-get install -y python-pip python-dev build-essential \
    && pip install -r requirements.txt
EXPOSE 80
ENV PORT 80
ENTRYPOINT ["python"]
CMD ["app.py"]

