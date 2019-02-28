import cherrypy
import os
import time
import speech_recognition as sr
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('html'))


class Root(object):
    @cherrypy.expose
    def index(self):
        tmpl = env.get_template('index.html')
        return tmpl.render()

    @cherrypy.expose
    def upload(self, ufile):
        # Save the file to the directory where app.py is:
        upload_path = os.path.dirname(__file__)

        # Save the file using the filename sent by the client, with an added timestamp:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        upload_filename = timestamp + ufile.filename

        upload_file = os.path.normpath(
            os.path.join(upload_path, upload_filename))
        size = 0
        with open(upload_file, 'wb') as out:
            while True:
                data = ufile.file.read(8192)
                if not data:
                    break
                out.write(data)
                size += len(data)
        upload_success = '''
        File received successfully.
        Filename: {}
        Length: {}
        Mime-type: {}
        '''.format(upload_filename, size, ufile.content_type, data)
        cherrypy.log(upload_success)

        # Now that we have the file saved on the disk, proceed to do the speech processing
        # use the audio file as the audio source
        # audio file should be in the .wav format
        r = sr.Recognizer()
        with sr.AudioFile(upload_filename) as source:
            audio = r.record(source)  # read the entire audio file
            result_text = r.recognize_google(audio)

        tmpl = env.get_template('result.html')
        return tmpl.render(message=result_text)


if __name__ == '__main__':
    config = {
        'global': {
            'server.socket_host': '127.0.0.1',  # '0.0.0.0',
            'server.socket_port': int(os.environ.get('PORT', 5000)),
        },
        '/assets': {
            'tools.staticdir.root': os.path.dirname(os.path.abspath(__file__)),
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'assets',
        }
    }
    cherrypy.quickstart(Root(), '/', config=config)
