import cherrypy
import os
import time
import speech_recognition as sr
from pydub import AudioSegment
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('html'))


def split_audio(input_path, output_path):
    """
    Method used to split the .WAV file into multiple 30sec chunks, circumventing Google's API limitation
    """
    audio_file = AudioSegment.from_wav(input_path)
    for i, chunk in enumerate(audio_file[::30 * 1000]):
        chunk.export(output_path + "/out{:>08d}.wav".format(i), format="wav")
    return audio_file.duration_seconds


class Root(object):
    @cherrypy.expose
    def index(self):
        tmpl = env.get_template('index.html')
        return tmpl.render()

    @cherrypy.expose
    def upload(self, ufile):
        # Save the file to the directory where app.py is:
        upload_path = os.path.dirname(__file__) + '/uploads'

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

        audio_length = split_audio('uploads/' + upload_filename, 'parts')

        # Now that we have the file saved on the disk, proceed to do the speech processing
        # use the audio file as the audio source
        # audio file should be in the .wav format
        r = sr.Recognizer()
        files = sorted(os.listdir('parts/'))
        all_text = []

        for f in files:
            if f.endswith(".wav"):
                name = "parts/" + f
                # Load audio file
                with sr.AudioFile(name) as source:
                    audio = r.record(source)  # read the segment of the audio file
                # Transcribe audio file
                text = r.recognize_google(audio)
                all_text.append(text)

        # Remove the file(s) after use
        os.remove(upload_file)

        for filename in os.listdir(os.path.dirname(__file__) + '/parts'):
            if filename.endswith('.wav'):
                os.remove(os.path.normpath(os.path.join(os.path.dirname(__file__) + '/parts', filename)))

        # Prepare the transcript
        transcript = []
        for i, t in enumerate(all_text):
            total_seconds = i * 30
            # Method to get hours, minutes and seconds
            m, s = divmod(total_seconds, 60)
            h, m = divmod(m, 60)

            # Format time as h:m:s - 30 seconds of text
            segment = ("{:0>2d}:{:0>2d}:{:0>2d}".format(h, m, s), t)
            transcript.append(segment)

        # Prepare the audio length timestamp
        m, s = divmod(int(audio_length), 60)
        h, m = divmod(m, 60)
        length_string = "{:0>2d}:{:0>2d}:{:0>2d}".format(h, m, s)

        tmpl = env.get_template('result.html')
        return tmpl.render(message=transcript, length=length_string)


if __name__ == '__main__':
    config = {
        'global': {
            'server.socket_host': '0.0.0.0',  # '127.0.0.1',
            'server.socket_port': int(os.environ.get('PORT', 5000)),
        },
        '/assets': {
            'tools.staticdir.root': os.path.dirname(os.path.abspath(__file__)),
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'assets',
        }
    }
    cherrypy.quickstart(Root(), '/', config=config)
