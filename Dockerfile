FROM ubuntu

RUN apt update
RUN apt install python3 python3-dev ffmpeg
RUN pip3 install -U -r requirements.txt

CMD [ "python3", "-m", "bot" ]