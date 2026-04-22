"""C4: Notifications — Slack webhook and email digest."""

from __future__ import annotations

import json
import os
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests

from ..intelligence.analyzer import SegmentProposal


def _build_slack_payload(proposals: list[SegmentProposal], run_date: str, top_n: int) -> dict:
    top = proposals[:top_n]
    lines = [
        f"*AdTech Segment Proposals — {run_date}* ({len(proposals)} total)",
        "",
    ]
    for i, p in enumerate(top, 1):
        expiry = f" | exp. {p.expiry_date()}" if p.expiry_date() else ""
        lines.append(
            f"{i}. *{p.name}* — {p.iab_tier2_id} | score: {p.score}{expiry}"
        )
        lines.append(f"   _{p.description[:120]}_")

    return {"text": "\n".join(lines)}


def send_slack(proposals: list[SegmentProposal], run_date: str, top_n: int = 10) -> None:
    webhook = os.getenv("SLACK_WEBHOOK_URL", "")
    if not webhook:
        return
    try:
        payload = _build_slack_payload(proposals, run_date, top_n)
        resp = requests.post(
            webhook,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        resp.raise_for_status()
        print(f"[notifier] Slack notification sent ({len(proposals)} segments).")
    except Exception as exc:
        print(f"[notifier] Slack failed: {exc}")


def _build_html(proposals: list[SegmentProposal], run_date: str, top_n: int) -> str:
    rows = ""
    for i, p in enumerate(proposals[:top_n], 1):
        expiry = p.expiry_date() or "—"
        rows += (
            f"<tr><td>{i}</td><td><b>{p.name}</b><br><small>{p.description[:120]}</small></td>"
            f"<td>{p.iab_tier2_id}</td><td>{p.score}</td>"
            f"<td>{p.temporal_tag}</td><td>{expiry}</td></tr>\n"
        )
    return f"""
<html><body>
<h2>AdTech Segment Proposals — {run_date}</h2>
<p>Total segments proposed: <b>{len(proposals)}</b></p>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;font-family:sans-serif;font-size:13px;">
  <tr style="background:#f0f0f0;">
    <th>#</th><th>Segment</th><th>IAB</th><th>Score</th><th>Type</th><th>Expiry</th>
  </tr>
  {rows}
</table>
</body></html>
"""


def send_email(proposals: list[SegmentProposal], run_date: str, top_n: int = 10) -> None:
    recipient = os.getenv("NOTIFICATION_EMAIL", "")
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")

    if not all([recipient, smtp_host, smtp_user, smtp_password]):
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"AdTech Segment Proposals — {run_date} ({len(proposals)} segments)"
        msg["From"] = smtp_user
        msg["To"] = recipient

        html = _build_html(proposals, run_date, top_n)
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, recipient, msg.as_string())
        print(f"[notifier] Email sent to {recipient}.")
    except Exception as exc:
        print(f"[notifier] Email failed: {exc}")
