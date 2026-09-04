"""Command line entrypoint for Py-dlp."""

from __future__ import annotations

import sys
from typing import List, Optional

from pydlp.core.browser_cookies import BrowserCookieLoader
from pydlp.core.doctor import run_doctor
from pydlp.core.progress import TerminalColors, colorize, format_table
from pydlp.extractor import list_extractors
from pydlp.extractor.sites_db import get_platform_catalog
from pydlp.options import build_arg_parser, parse_cli_args
from pydlp.pydlp import PyDLP
from pydlp.version import __version__


def main(args: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    parsed, opts = parse_cli_args(args)

    # 1. Launch TUI Dashboard if requested
    if opts.get("tui", False):
        from pydlp.core.tui import launch_tui
        return launch_tui()

    # 2. Setup Termux Environment if requested
    if opts.get("setup_termux", False):
        from pydlp.core.termux import setup_termux_environment
        return setup_termux_environment()

    # 3. Run Self-Updater if requested
    if opts.get("update", False):
        from pydlp.core.updater import SelfUpdater
        return SelfUpdater(color=opts.get("color", True)).update()

    # 3. Generate Shell Completion if requested
    completion_shell = opts.get("generate_completion")
    if completion_shell:
        from pydlp.core.completion import generate_completion_script
        print(generate_completion_script(completion_shell))
        return 0

    # 4. Run Doctor / System Diagnostics if requested
    if opts.get("doctor", False):
        return run_doctor()

    # 5. Search Sites Catalog if requested
    search_query = opts.get("search_sites")
    if search_query:
        catalog = get_platform_catalog()
        matches = []
        q = search_query.lower().strip()
        for domain, info in catalog.items():
            if q in domain.lower() or q in info.get("desc", "").lower() or q in info.get("category", "").lower():
                matches.append([domain, info.get("category", ""), info.get("desc", "")])

        headers = ["PLATFORM", "CATEGORY", "DESCRIPTION"]
        print(colorize(f"Py-dlp Universal Catalog Results for '{search_query}' ({len(matches)} matches):", TerminalColors.BOLD, opts.get("color", True)))
        if matches:
            print(format_table(headers, matches))
        else:
            print(f"No exact matches found for '{search_query}'. The Universal Catalog Engine matches any standard media URL automatically.")
        return 0

    # 5. Start Web Dashboard if requested
    if opts.get("serve", False):
        from pydlp.server.app import run_server
        host = opts.get("host", "0.0.0.0")
        port = int(opts.get("port", 8000))
        run_server(host=host, port=port)
        return 0

    # 6. List Extractors if requested
    if opts.get("list_extractors", False) or opts.get("listextractors", False):
        extractors = list_extractors()
        headers = ["EXTRACTOR NAME", "DESCRIPTION"]
        rows = [[ie.IE_NAME, ie.IE_DESC or ""] for ie in extractors]
        print(colorize(f"Py-dlp (v{__version__}) Supported Extractors ({len(extractors)}):", TerminalColors.BOLD, opts.get("color", True)))
        print(format_table(headers, rows))
        return 0

    # 7. Check for input URLs, batch file, or bookmark/m3u imports
    urls = list(opts.get("urls", []))
    batch_file = opts.get("batchfile")
    if batch_file:
        try:
            if batch_file == "-":
                lines = sys.stdin.read().splitlines()
            else:
                with open(batch_file, "r", encoding="utf-8") as bf:
                    lines = bf.read().splitlines()
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line)
        except Exception as e:
            print(f"[error] Failed to read batch file {batch_file}: {e}", file=sys.stderr)
            return 1

    # Check Bookmark / Playlist Importers
    import_bm = opts.get("import_bookmarks")
    if import_bm:
        from pydlp.core.bookmarks import BookmarkImporter
        imported = BookmarkImporter.import_file(import_bm)
        print(f"[info] Imported {len(imported)} URLs from bookmarks: {import_bm}")
        urls.extend(imported)

    import_m3u = opts.get("import_m3u")
    if import_m3u:
        from pydlp.core.bookmarks import BookmarkImporter
        imported = BookmarkImporter.parse_m3u_playlist(import_m3u)
        print(f"[info] Imported {len(imported)} URLs from playlist: {import_m3u}")
        urls.extend(imported)

    if not urls:
        parser = build_arg_parser()
        parser.print_help()
        return 1

    # 8. Check Browser Cookies
    browser = opts.get("cookies_from_browser")
    if browser:
        jar = BrowserCookieLoader.load_cookies(browser)
        opts["cookie_jar"] = jar

    # 9. Check Direct Play Mode
    if opts.get("play", False):
        from pydlp.core.stream_player import StreamPlayer
        engine = PyDLP(opts)
        player = StreamPlayer(opts.get("player"))
        for url in urls:
            info = engine.extract_info(url, download=False)
            if info and info.formats:
                selected_fmts = engine.format_selector.select_formats(info)
                fmt = selected_fmts[0] if selected_fmts else info.formats[0]
                player.play(info, fmt)
        return 0

    # 10. Check Watcher Daemon Mode
    if opts.get("watch", False):
        from pydlp.core.watcher import WatcherDaemon
        engine = PyDLP(opts)
        daemon = WatcherDaemon(engine, urls, interval=int(opts.get("watch_interval", 60)))
        daemon.run()
        return 0

    # 11. Instantiate PyDLP and run download
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
