"""HTML renderer."""

from __future__ import annotations

from html import escape
from pathlib import Path

from py_structure_tools.model import TreeNode
from py_structure_tools.stats import format_node_meta


def count_nodes(node: TreeNode) -> tuple[int, int]:
    """Count directories and files."""
    directories = 1 if node.is_dir else 0
    files = 1 if node.is_file else 0

    for child in node.children:
        child_directories, child_files = count_nodes(child)
        directories += child_directories
        files += child_files

    return directories, files


def render_html_tree(
    node: TreeNode,
    depth: int = 0,
    open_until_depth: int = 1,
) -> str:
    """Render a tree node as nested HTML lists."""
    safe_name = escape(node.name)
    meta = format_node_meta(node)
    # <em> (not <span>) so the ".file span::before" icon rule does not match it.
    info_html = f'<em class="info">{escape(meta)}</em>' if meta else ""

    if node.is_file:
        return f'<li class="file"><span>{safe_name}{info_html}</span></li>'

    children_html = (
        "\n".join(
            render_html_tree(
                child,
                depth=depth + 1,
                open_until_depth=open_until_depth,
            )
            for child in node.children
        )
        if node.children
        else '<li class="empty"><span>Empty directory</span></li>'
    )

    open_attr = " open" if depth <= open_until_depth else ""

    return f"""
<li class="directory">
  <details{open_attr}>
    <summary>
      <span class="name">{safe_name}</span>{info_html}
      <span class="count">{len(node.children)}</span>
    </summary>
    <ul>
      {children_html}
    </ul>
  </details>
</li>
""".strip()


def build_html_document(root_node: TreeNode, open_until_depth: int = 1) -> str:
    """Build a standalone HTML document."""
    safe_root_name = escape(root_node.name)
    tree_html = render_html_tree(root_node, open_until_depth=open_until_depth)
    directory_count, file_count = count_nodes(root_node)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Repository structure - {safe_root_name}</title>
  <style>
    :root {{
      --bg: #0f172a;
      --panel: #111827;
      --panel-soft: #1f2937;
      --text: #e5e7eb;
      --muted: #9ca3af;
      --line: #334155;
      --accent: #38bdf8;
      --hover: rgba(56, 189, 248, 0.10);
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
        "Liberation Mono", "Courier New", monospace;
      background: var(--bg);
      color: var(--text);
      line-height: 1.45;
    }}

    header {{
      position: sticky;
      top: 0;
      z-index: 10;
      padding: 16px 24px;
      background: rgba(15, 23, 42, 0.92);
      border-bottom: 1px solid var(--line);
      backdrop-filter: blur(10px);
    }}

    h1 {{
      margin: 0;
      font-size: 18px;
    }}

    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
      color: var(--muted);
      font-size: 13px;
    }}

    .badge {{
      padding: 3px 8px;
      background: var(--panel-soft);
      border: 1px solid var(--line);
      border-radius: 999px;
    }}

    .toolbar {{
      display: flex;
      gap: 8px;
      margin-top: 12px;
    }}

    button {{
      cursor: pointer;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel-soft);
      color: var(--text);
      padding: 6px 10px;
      font: inherit;
      font-size: 12px;
    }}

    button:hover {{
      border-color: var(--accent);
      background: rgba(56, 189, 248, 0.12);
    }}

    main {{ padding: 24px; }}

    .tree-panel {{
      max-width: 1200px;
      padding: 18px;
      background: rgba(17, 24, 39, 0.72);
      border: 1px solid var(--line);
      border-radius: 14px;
    }}

    ul {{
      list-style: none;
      margin: 0;
      padding-left: 22px;
      border-left: 1px solid var(--line);
    }}

    .tree-panel > ul {{
      border-left: none;
      padding-left: 0;
    }}

    li {{
      margin: 2px 0;
      position: relative;
    }}

    summary {{
      cursor: pointer;
      user-select: none;
      padding: 3px 6px;
      border-radius: 6px;
      outline: none;
    }}

    summary:hover,
    .file span:hover {{
      background: var(--hover);
    }}

    .directory > details > summary .name::before {{
      content: "📁 ";
    }}

    .directory > details[open] > summary .name::before {{
      content: "📂 ";
    }}

    .file span::before {{
      content: "📄 ";
    }}

    .file span,
    .empty span {{
      display: inline-block;
      padding: 3px 6px;
      border-radius: 6px;
    }}

    .empty {{
      color: var(--muted);
      font-style: italic;
    }}

    .count {{
      margin-left: 8px;
      color: var(--muted);
      font-size: 11px;
    }}

    .info {{
      margin-left: 8px;
      color: var(--muted);
      font-size: 11px;
      font-style: normal;
    }}

  </style>
</head>
<body>
  <header>
    <h1>Repository structure: {safe_root_name}</h1>

    <div class="meta">
      <span class="badge">{directory_count} directories</span>
      <span class="badge">{file_count} files</span>
      <span class="badge">Open depth: {open_until_depth}</span>
    </div>

    <div class="toolbar">
      <button type="button" onclick="setAllDetails(true)">Open all</button>
      <button type="button" onclick="setAllDetails(false)">Close all</button>
    </div>
  </header>

  <main>
    <section class="tree-panel">
      <ul>
        {tree_html}
      </ul>
    </section>
  </main>

  <script>
    function setAllDetails(open) {{
      document.querySelectorAll("details").forEach((details) => {{
        details.open = open;
      }});
    }}
  </script>
</body>
</html>
"""


def export_html(
    root_node: TreeNode,
    output_path: Path,
    open_until_depth: int,
) -> None:
    """Export tree as standalone HTML."""
    _ = output_path.write_text(
        build_html_document(root_node, open_until_depth=open_until_depth),
        encoding="utf-8",
    )
