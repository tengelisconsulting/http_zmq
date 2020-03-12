#!/usr/bin/env python3.8

import mongrel2


def main():
    con = mongrel2.connect(None, "127.0.0.1", 5000, 5001)
    while True:
        req = mongrel2.recv(con)
        print("got req")
        print(req)
        if req.method != "JSON":
            mongrel2.reply(
                con, req, "Echo!"
            )


if __name__ == "__main__":
    main()
