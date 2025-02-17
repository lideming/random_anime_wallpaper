FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ \
    "python3", "-m" , "flask", \
    "--app", "random_anime_wallpaper.py", \
    "run", \
    "--host=0.0.0.0" \
]
