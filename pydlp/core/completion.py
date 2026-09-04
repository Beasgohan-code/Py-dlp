"""Shell auto-completion generator for Py-dlp.

Generates tab-completion scripts for Bash, Zsh, and Fish shells.
"""

from __future__ import annotations

import sys
from typing import List

from pydlp.options import build_arg_parser


def generate_completion_script(shell: str = "bash") -> str:
    """Generates an auto-completion script for the specified shell."""
    shell = shell.lower().strip()
    parser = build_arg_parser()
    options: List[str] = []

    for action in parser._actions:
        options.extend(action.option_strings)

    options_str = " ".join(sorted(set(options)))

    if shell == "bash":
        return f"""# Py-dlp Bash completion script
_pydlp_completion() {{
    local cur prev opts
    COMPREPLY=()
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    prev="${{COMP_WORDS[COMP_CWORD-1]}}"
    opts="{options_str}"

    if [[ ${{cur}} == -* ]] ; then
        COMPREPLY=( $(compgen -W "${{opts}}" -- ${{cur}}) )
        return 0
    fi
}}
complete -F _pydlp_completion pydlp
complete -F _pydlp_completion py-dlp
"""

    elif shell == "zsh":
        return f"""#compdef pydlp py-dlp
# Py-dlp Zsh completion script
_pydlp() {{
    local -a opts
    opts=({options_str})
    _arguments '*: :_files'
}}
compdef _pydlp pydlp py-dlp
"""

    elif shell == "fish":
        lines = ["# Py-dlp Fish completion script"]
        for opt in sorted(set(options)):
            if opt.startswith("--"):
                flag_name = opt.lstrip("-")
                lines.append(f"complete -c pydlp -l {flag_name} -d '{flag_name} option'")
                lines.append(f"complete -c py-dlp -l {flag_name} -d '{flag_name} option'")
            elif opt.startswith("-") and len(opt) == 2:
                short_flag = opt.lstrip("-")
                lines.append(f"complete -c pydlp -s {short_flag}")
                lines.append(f"complete -c py-dlp -s {short_flag}")
        return "\n".join(lines) + "\n"

    else:
        return f"# Unsupported shell: {shell}. Choose bash, zsh, or fish."
