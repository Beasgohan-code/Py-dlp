"""Command line entrypoint for Py-dlp."""

from __future__ import annotations

import sys
from typing import List, Optional

from pydlp.core.progress import TerminalColors, colorize, format_table
from pydlp.extractor import list_extractors
from pydlp.options import build_arg_parser, parse_cli_args
from pydlp.pydlp import PyDLP
from pydlp.version import __version__


def main(args: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    parsed, opts = parse_cli_args(args)

    # 1. Start Web Dashboard if requested
    if opts.get("serve", False):
        from pydlp.server.app import run_server
        host = opts.get("host", "0.0.0.0")
        port = int(opts.get("port", 8000))
        run_server(host=host, port=port)
        return 0

    # 2. List Extractors if requested
    if opts.get("list_extractors", False) or opts.get("listextractors", False):
        extractors = list_extractors()
        headers = ["EXTRACTOR NAME", "DESCRIPTION"]
        rows = [[ie.IE_NAME, ie.IE_DESC or ""] for ie in extractors]
        print(colorize(f"Py-dlp (v{__version__}) Supported Extractors ({len(extractors)}):", TerminalColors.BOLD, opts.get("color", True)))
        print(format_table(headers, rows))
        return 0

    # 3. Check for input URLs
    urls = opts.get("urls", [])
    if not urls:
        parser = build_arg_parser()
        parser.print_help()
        return 1

    # 4. Instantiate PyDLP and run
    try:
        engine = PyDLP(opts)
        exit_code = engine.download(urls)
        return exit_code
    except KeyboardInterrupt:
        print("\n[info] Interrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"\n[error] Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
