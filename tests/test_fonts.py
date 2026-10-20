import threading
import unittest
from http.client import HTTPConnection
from http.server import HTTPServer
from relay.web import ReviewApp, handler_for


class FontTest(unittest.TestCase):
    def test_fonts_served_as_woff2(self):
        server = HTTPServer(('127.0.0.1', 0), handler_for(ReviewApp()))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            port = server.server_port
            for name in ('jetbrains-mono', 'ibm-plex-sans'):
                conn = HTTPConnection('127.0.0.1', port)
                conn.request('GET', f'/fonts/{name}.woff2', headers={'Host': f'127.0.0.1:{port}'})
                res = conn.getresponse()
                self.assertEqual(res.status, 200)
                self.assertEqual(res.getheader('Content-Type'), 'font/woff2')
                self.assertEqual(res.read()[:4], b'wOF2')
        finally:
            server.shutdown()


if __name__ == '__main__':
    unittest.main()
