from html import escape
from typing import Any


def render_dashboard(runs: list[dict[str, Any]], tools: list[dict[str, Any]]) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Orka Dashboard</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8fb;
      --panel: #ffffff;
      --ink: #19202a;
      --muted: #657183;
      --line: #d9dee8;
      --accent: #1463ff;
      --ok: #117a3b;
      --warn: #a15c00;
      --bad: #b42318;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font: 14px/1.5 Arial, Helvetica, sans-serif;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      background: var(--panel);
      padding: 18px 28px;
    }}
    h1 {{ margin: 0; font-size: 22px; }}
    h2 {{ margin: 0 0 14px; font-size: 17px; }}
    main {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 320px;
      gap: 18px;
      padding: 20px 28px 32px;
    }}
    section {{
      min-width: 0;
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }}
    .metric, .run, .tool {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }}
    .metric strong {{ display: block; font-size: 22px; }}
    .metric span, .muted {{ color: var(--muted); }}
    .runs {{
      display: grid;
      gap: 12px;
    }}
    .run-head {{
      display: flex;
      align-items: start;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 10px;
    }}
    .run h3 {{
      margin: 0;
      font-size: 15px;
      overflow-wrap: anywhere;
    }}
    .badge {{
      display: inline-block;
      border-radius: 999px;
      border: 1px solid var(--line);
      padding: 3px 8px;
      font-size: 12px;
      white-space: nowrap;
    }}
    .completed {{ color: var(--ok); border-color: #9fd6b6; }}
    .awaiting_approval {{ color: var(--warn); border-color: #f0c889; }}
    .failed, .retry {{ color: var(--bad); border-color: #efaaa4; }}
    .steps {{
      margin: 10px 0 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 8px;
    }}
    .steps li {{
      border-left: 3px solid var(--accent);
      background: #f9fbff;
      padding: 8px 10px;
      overflow-wrap: anywhere;
    }}
    .tools {{
      display: grid;
      gap: 10px;
    }}
    code {{
      background: #eef2f8;
      border: 1px solid var(--line);
      border-radius: 4px;
      padding: 1px 4px;
    }}
    @media (max-width: 900px) {{
      main {{ grid-template-columns: 1fr; padding: 16px; }}
      header {{ padding: 16px; }}
      .summary {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Orka Dashboard</h1>
    <div class="muted">Run history, approval state, tool logs, and registered tool schemas.</div>
  </header>
  <main>
    <section>
      {render_metrics(runs)}
      <h2>Runs</h2>
      <div class="runs">
        {render_runs(runs)}
      </div>
    </section>
    <aside>
      <h2>Tools</h2>
      <div class="tools">
        {render_tools(tools)}
      </div>
    </aside>
  </main>
</body>
</html>"""


def render_metrics(runs: list[dict[str, Any]]) -> str:
    total = len(runs)
    completed = sum(1 for run in runs if run.get("status") == "completed")
    waiting = sum(1 for run in runs if run.get("status") == "awaiting_approval")
    failed = sum(1 for run in runs if run.get("errors"))
    return f"""
      <div class="summary">
        <div class="metric"><strong>{total}</strong><span>Total runs</span></div>
        <div class="metric"><strong>{completed}</strong><span>Completed</span></div>
        <div class="metric"><strong>{waiting}</strong><span>Waiting approval</span></div>
        <div class="metric"><strong>{failed}</strong><span>With errors</span></div>
      </div>
    """


def render_runs(runs: list[dict[str, Any]]) -> str:
    if not runs:
        return '<div class="run muted">No runs yet.</div>'

    return "\n".join(render_run(run) for run in runs)


def render_run(run: dict[str, Any]) -> str:
    status = str(run.get("status", "unknown"))
    run_id = escape(str(run.get("run_id", "")))
    user_input = escape(str(run.get("input") or "No input captured."))
    message = escape(str(run.get("message", "")))
    timestamp = escape(str(run.get("timestamp", "")))
    approved = "yes" if run.get("approved") else "no"
    errors = run.get("errors") or []
    error_html = ""
    if errors:
        error_html = "<ul class=\"steps\">" + "".join(f"<li>{escape(str(error))}</li>" for error in errors) + "</ul>"

    return f"""
      <article class="run">
        <div class="run-head">
          <div>
            <h3>{user_input}</h3>
            <div class="muted"><code>{run_id}</code> · {timestamp}</div>
          </div>
          <span class="badge {escape(status)}">{escape(status)}</span>
        </div>
        <div>{message}</div>
        <div class="muted">Approved: {approved}</div>
        {render_steps(run.get("steps") or [])}
        {error_html}
      </article>
    """


def render_steps(steps: list[dict[str, Any]]) -> str:
    if not steps:
        return '<div class="muted">No tool steps executed.</div>'

    items = []
    for step in steps:
        tool_name = escape(str(step.get("tool_name", "unknown_tool")))
        success = "success" if step.get("success") else "failed"
        error = step.get("error")
        detail = escape(str(error or step.get("output") or ""))
        items.append(f"<li><strong>{tool_name}</strong> · {success}<br><span class=\"muted\">{detail}</span></li>")
    return "<ul class=\"steps\">" + "".join(items) + "</ul>"


def render_tools(tools: list[dict[str, Any]]) -> str:
    if not tools:
        return '<div class="tool muted">No tools registered.</div>'

    cards = []
    for tool in tools:
        name = escape(str(tool.get("name", "")))
        description = escape(str(tool.get("description", "")))
        parameters = tool.get("parameters", {})
        required = parameters.get("required", []) if isinstance(parameters, dict) else []
        properties = parameters.get("properties", {}) if isinstance(parameters, dict) else {}
        fields = ", ".join(
            f"{escape(str(field))}: {escape(str(schema.get('type', 'string')))}"
            for field, schema in properties.items()
            if isinstance(schema, dict)
        )
        required_text = ", ".join(escape(str(field)) for field in required) or "none"
        cards.append(
            f"""
            <div class="tool">
              <strong>{name}</strong>
              <div class="muted">{description}</div>
              <div><code>{fields or "no parameters"}</code></div>
              <div class="muted">Required: {required_text}</div>
            </div>
            """
        )
    return "\n".join(cards)
