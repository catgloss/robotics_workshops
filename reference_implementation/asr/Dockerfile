FROM python:3.8.10

WORKDIR /asr_app/

# Copy requirements.
COPY requirements.txt requirements.txt

# Install libsndfile.
RUN apt-get update \
&& apt-get upgrade -y \
&& apt-get install -y \
&& apt-get -y install apt-utils gcc libpq-dev libsndfile-dev \
&& apt-get install -y ffmpeg

# Install deps.
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Copy source code.
COPY . .
# RUN chmod +x ./wait-for-it.sh ./docker-entrypoint.sh
ENTRYPOINT [ "./docker-entrypoint.sh" ]
CMD [ "flask", "run", "--host=0.0.0.0" ]
EXPOSE 5000
