import json
from typing import Dict
from typing import NamedTuple

import zmq
import zmq.asyncio

import tnetstrings


MAX_IDENTS = 100

HTTP_FORMAT = "HTTP/1.1 %(code)s %(status)s\r\n%(headers)s\r\n\r\n%(body)s"


class MG2Connection(NamedTuple):
    ctx: zmq.Context
    pull: zmq.Socket
    pub: zmq.Socket


class MG2Request(NamedTuple):
    sender: str
    conn_id: str
    method: str
    path: str
    headers: Dict
    body: str


def http_response(
        body: str,
        code: int,
        status: str,
        headers: Dict
):
    payload = {'code': code, 'status': status, 'body': body}
    headers['Content-Length'] = len(body)
    payload['headers'] = "\r\n".join('%s: %s' % (k,v) for k,v in
                                     headers.items())
    return HTTP_FORMAT % payload


def connect(
        sender_id,
        mongrel_host: str,
        pull_port: int,
        pub_port: int
)-> MG2Connection:
    ctx = zmq.asyncio.Context()
    pull = ctx.socket(zmq.PULL)
    pub = ctx.socket(zmq.PUB)
    if sender_id:
        pub.setsockopt(zmq.IDENTITY, sender_id)
    pull.connect(f"tcp://{mongrel_host}:{pull_port}")
    pub.connect(f"tcp://{mongrel_host}:{pub_port}")
    return MG2Connection(
        ctx = ctx,
        pull = pull,
        pub = pub
    )


async def recv(
        con: MG2Connection
)-> MG2Request:
    raw_work = await con.pull.recv_multipart()
    msg = raw_work[0].decode("utf-8")
    sender, conn_id, path, rest = msg.split(' ', 3)
    headers, rest = tnetstrings.parse(rest)
    body, _ = tnetstrings.parse(rest)
    if type(headers) is str:
        headers = json.loads(headers)
    return MG2Request(
        sender = sender,
        conn_id = conn_id,
        method = headers["METHOD"],
        path = path,
        headers = headers,
        body = body
    )


def reply(
        con: MG2Connection,
        req: MG2Request,
        body: str,
        headers: Dict = None,
        code: int = 200,
        status: str = "OK"
)-> None:
    if headers is None:
        headers = default_headers()
    response = http_response(
        body, code, status, headers
    )
    mg2_header = "%s %d:%s," % (
        req.sender,
        len(str(req.conn_id)),
        str(req.conn_id)
    )
    mg2_response = mg2_header + " " + response
    con.pub.send(mg2_response.encode("utf-8"))


def default_headers() -> Dict:
    return {
        "content-type": "application/json",
    }
