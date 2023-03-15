FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -y python3.9 python3-distutils python3-pip python3-apt
RUN pip3 install boto3

WORKDIR /usr/src/app

COPY *.py ./

ENTRYPOINT ["python3", "./test.py"]
