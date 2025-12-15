ARG image=dependencies

FROM $image AS build-stage

COPY . $APP_PATH

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]