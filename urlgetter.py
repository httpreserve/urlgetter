"""urlgetter.py will retrieve the correct target for URIs even those
that are being redirected, vs. curl --head <> which you have to work
with "Location:" or "Host:" fields to determine the answer to this.

Usage:

    `python3 urlgetter.py [optional: <domains list>]
                          [optional: <output_file_name>]
                          [optional: <errors_file_name>]
    `

The script will either look for `domains.txt` or argv[1] can be
supplied pointing to a single-column on-disk file listing the domains.
The file can have a header, it just won't return a sensible output. It
won't break the script.
"""

import socket
import sys
import urllib
from http.client import InvalidURL
from time import sleep
from typing import Final
from urllib import request

opener = urllib.request.build_opener()

header: Final[dict] = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Charset": "utf-8;q=0.7,*;q=0.3",
    "Accept-Encoding": "none",
    "Accept-Language": "en-US,en;q=0.8",
    "Connection": "keep-alive",
    "Range": "bytes=0-50",
}


def process_domains():
    """Process domains from a list on-disk and output a results file."""
    domains = "domains.txt"
    try:
        domains = sys.argv[1]
    except IndexError:
        pass
    print(f"reading domains from: {domains}", file=sys.stderr)
    preprocessed = []
    links = []
    errs = []
    with open(domains, "r", encoding="utf-8") as file:
        for line in file:
            url = line.strip()
            if "http" not in url:
                # Theoretically http will redirect to https these days,
                # but I don't believe this assumption is error free.
                url = "http://{}".format(url).replace('"', "")
            preprocessed.append(url)
        len_ = len(set(preprocessed))
        for idx, url in enumerate(set(preprocessed), 1):
            print(f"processing [{idx:0>4} out of {len_:0>4}]: {url}", file=sys.stderr)
            req = request.Request(url, headers=header, method="HEAD")
            res = None
            try:
                res = opener.open(req, timeout=2)
                links.append(res.geturl().strip("/"))
            except urllib.error.URLError as err:
                errs.append(f"Broken: {url} {err}".replace("\n", ""))
            except InvalidURL as err:
                errs.append(f"Cannot process: {url} {err}".replace("\n", ""))
            except socket.timeout as err:
                errs.append(f"Socket timeout exception: {url} {err}".replace("\n", ""))
            except UnicodeEncodeError as err:
                errs.append(f"Unicode error: {url} {err}".replace("\n", ""))
            except ConnectionResetError as err:
                errs.append(f"Connection error: {url} {err}".replace("\n", ""))
            sleep(0.200)
    output = "output.txt"
    try:
        output = sys.argv[2]
    except IndexError:
        pass
    errors = "errors.txt"
    try:
        errors = sys.argv[3]
    except IndexError:
        pass
    print(f"outputting {len(set(links))} results to: {output}", file=sys.stderr)
    with open(output, "w", encoding="utf-8") as outfile:
        for link in set(links):
            outfile.write(f"{link}\n")
    print(f"outputting {len(errs)} errors to: {errors}", file=sys.stderr)
    with open(errors, "w", encoding="utf-8") as errorfile:
        for msg in set(errs):
            errorfile.write(f"{msg}\n")


if __name__ == "__main__":
    """Primary entry point for this script."""
    process_domains()
