import os.path
import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.web import asynchronous, StaticFileHandler

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("/Users/dayvson/uploader/test/javascript/SpecRunner.html")

def get_app():
    return tornado.web.Application([
        (r"/lib/(.*)",   StaticFileHandler,
                        {"path": "/Users/dayvson/uploader/test/javascript/lib/"}),
        (r"/spec/(.*)",   StaticFileHandler,
                        {"path": "/Users/dayvson/uploader/test/javascript/spec/"}),
        (r"/",  MainHandler)
    ])

def run():
    application = get_app() 
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen("8889", "0.0.0.0")
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    run()
