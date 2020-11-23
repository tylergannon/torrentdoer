"""
Main module, executed when invoking torrent-doer from
python -m torrentdoer
"""
import sys
from .entrypoint import cli

cli.main(args=sys.argv[1:], prog_name="torrentdoer")
