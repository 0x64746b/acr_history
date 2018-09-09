#!/usr/bin/env python3
# coding: utf-8

from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from threading import Thread
import urllib.parse
from uuid import uuid4

from dotenv import load_dotenv


class SpotifyAuthorizer():

    class _AuthorizationCallback(BaseHTTPRequestHandler):
        def do_GET(self):
            params = urllib.parse.parse_qs(self.path[2:])
            if "code" in params:
                print(params)
                if params.get("state", [None])[0] == self.server._callback_nonce:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(
                        b"ACR importer has acquired access to your account."
                    )
                else:
                    self.send_error(401, "Invalid callback detected")
                    self.end_headers()
            else:
                self.send_response(
                    400,
                    "You need to allow ACR importer to access your account",
                    "Otherwise it cannot create the ACR playlist."
                )
                self.end_headers()

    def __init__(self):
        self._auth_state = None
        load_dotenv()

    def _wait_for_callback(self, nonce):
        http_server = HTTPServer(('', 5100), self._AuthorizationCallback)
        http_server._callback_nonce = nonce
        http_server.handle_request()

    def authorize(self):
        nonce = uuid4().hex
        Thread(
            target=self._wait_for_callback,
            kwargs={'nonce': nonce}
        ).start()

        authorize_url = urllib.parse.ParseResult(
            scheme="https",
            netloc="accounts.spotify.com",
            path="/authorize",
            params=None,
            query=urllib.parse.urlencode({
                "client_id": os.getenv("ACR_IMPORTER_CLIENT_ID"),
                "response_type": "code",
                "redirect_uri": "http://localhost:5100/",
                "state": nonce,
            }),
            fragment=None,
        )
        print(
            "Please visit {} to authorize this script to access your"
            " account".format(urllib.parse.urlunparse(authorize_url))
        )


if __name__ == "__main__":
    SpotifyAuthorizer().authorize()
