# Serves http://<host>/<path> for hosts mapped to 127.0.0.1 in /etc/hosts by fetching
# https://<host>/<path> (the origins now redirect http->https, which JDK 1.5 cannot follow).
import http.server, os, sys, urllib.request
ROOT = sys.argv[1]
# Resolve the real origins now, before /etc/hosts points them at 127.0.0.1.
import socket
_real = socket.getaddrinfo
_cache = {h: _real(h, 443, proto=socket.IPPROTO_TCP) for h in sys.argv[2:]}
def _gai(host, port, *a, **k):
    if host in _cache:
        return [(f, t, pr, c, (sa[0], port) + tuple(sa[2:])) for f, t, pr, c, sa in _cache[host]]
    return _real(host, port, *a, **k)
socket.getaddrinfo = _gai
class H(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        host = (self.headers.get('Host') or '').split(':')[0]
        p = path.split('?', 1)[0]
        f = os.path.join(ROOT, host, p.lstrip('/'))
        if p.endswith('/'):
            f = os.path.join(f, 'index.html')
        if not os.path.isfile(f):
            try:
                req = urllib.request.Request('https://' + host + path, headers={'User-Agent': 'Mozilla/5.0'})
                data = urllib.request.urlopen(req, timeout=60).read()
                os.makedirs(os.path.dirname(f), exist_ok=True)
                open(f, 'wb').write(data)
                sys.stderr.write('mirror: fetched https://%s%s\n' % (host, path))
            except Exception as e:
                sys.stderr.write('mirror: MISS https://%s%s (%s)\n' % (host, path, e))
        return f
    def guess_type(self, path):
        return 'text/xml'
http.server.ThreadingHTTPServer(('127.0.0.1', 80), H).serve_forever()
