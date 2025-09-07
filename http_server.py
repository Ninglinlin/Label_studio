import http.server
import socketserver

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

if __name__ == '__main__':
    port = 8000
    with socketserver.TCPServer(("", port), CORSRequestHandler) as httpd:
        print(f"服务器已启动，访问端口：{port}")
        httpd.serve_forever()