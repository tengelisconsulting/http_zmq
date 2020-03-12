#!/usr/bin/env python3.8

import asyncio

import mongrel2


async def handle(
        con: mongrel2.MG2Connection,
        req: mongrel2.MG2Request
)-> None:
    if req.method != "JSON":
        mongrel2.reply(
            con, req, "Echo!"
        )


async def main():
    con = mongrel2.connect(None, "127.0.0.1", 5000, 5001)
    while True:
        req = await mongrel2.recv(con)
        print("got req")
        print(req)
        asyncio.create_task(
            handle(con, req)
        )


if __name__ == "__main__":
    asyncio.run(main())
