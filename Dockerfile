FROM tuttlibrary/python-base
MAINTAINER Jeremy Nelson <jermnelson@gmail.com>

ENV HOME /opt/marc-batch-app
RUN mkdir -p $HOME/instance && mkdir logs
COPY *.py $HOME/
COPY lib/ $HOME/lib/
COPY static/ $HOME/static/
COPY templates/ $HOME/templates/

EXPOSE 20157
WORKDIR $HOME
CMD ["nohup", "gunicorn", "-b", "0.0.0.0:20157", "app:parent_app"]
