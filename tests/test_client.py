import json
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

from commspliant import APIError, Client


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path == "/api/v1/render/html":
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            if body["templateId"] != "550e8400-e29b-41d4-a716-446655440000":
                self.send_response(400)
                self.end_headers()
                return

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("X-Request-ID", "req-123")
            self.end_headers()
            self.wfile.write(b"<html>ok</html>")
            return

        if self.path == "/api/v1/render/pdf":
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.end_headers()
            self.wfile.write(b"%PDF-1.4")
            return

        if self.path == "/api/v1/render/error":
            self.send_response(404)
            self.send_header("X-Request-ID", "req-404")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "template not found"}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args) -> None:
        return


class ClientTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = HTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()

    def test_render_html_success(self) -> None:
        client = Client("ck_test", base_url=self.base_url)
        result = client.render_html(
            template_id="550e8400-e29b-41d4-a716-446655440000",
            variables={"title": "Monthly Report"},
        )
        self.assertEqual(result.body, b"<html>ok</html>")
        self.assertEqual(result.request_id, "req-123")

    def test_render_pdf_success(self) -> None:
        client = Client("ck_test", base_url=self.base_url)
        result = client.render_pdf(
            template_id="550e8400-e29b-41d4-a716-446655440000",
            variables={},
        )
        self.assertTrue(result.body.startswith(b"%PDF"))

    def test_missing_template_id(self) -> None:
        client = Client("ck_test", base_url=self.base_url)
        with self.assertRaisesRegex(ValueError, "template_id is required"):
            client.render_html(template_id="", variables={})

    def test_api_error(self) -> None:
        client = Client("ck_test", base_url=self.base_url)
        with self.assertRaises(APIError) as ctx:
            client._post_render(
                "/api/v1/render/error",
                template_id="550e8400-e29b-41d4-a716-446655440000",
                variables={},
                template_version_id=None,
            )
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(ctx.exception.message, "template not found")
        self.assertEqual(ctx.exception.request_id, "req-404")


if __name__ == "__main__":
    unittest.main()
