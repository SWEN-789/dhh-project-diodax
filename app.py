import cherrypy
import os
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('html'))


class Root(object):
    @cherrypy.expose
    def index(self):
        data_to_show = ['Hello', 'world']
        tmpl = env.get_template('index.html')
        return tmpl.render(data=data_to_show)


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
