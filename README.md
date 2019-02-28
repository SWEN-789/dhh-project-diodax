# dhh-project-diodax

A demo for a web-based transcriber of podcasts and other audio files to written text. 

## About

This project uses [cherrypy](http://www.cherrypy.org/) for the web server, and [jinja2](http://jinja.pocoo.org/docs/dev/) for html rendering. The audio files are transcribed server-side using the [Google Cloud Speech API](https://cloud.google.com/speech-to-text/). 

Example audio files are located on the `/examples` folder.

## Setting up locally

Make sure you have [Python](https://www.python.org/) and [pip](https://pip.pypa.io/en/stable/installing/) installed.

```bash
git clone https://github.com/SWEN-789/dhh-project-diodax.git
cd dhh-project-diodax
pip install -r requirements.txt
python app.py
```

The web server should now be running locally on http://localhost:5000. 