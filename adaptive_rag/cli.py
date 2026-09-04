from __future__ import annotations

import argparse
import json

from .config import settings
from .research import MultiAspectResearch


def main() -> None:
    parser = argparse.ArgumentParser(prog="adaptive-rag", description="AdaptiveRAG-X command line interface")
    sub = parser.add_subparsers(dest="command", required=True)
    research = sub.add_parser("research", help="run multi-aspect research")
    research.add_argument("question")
    research.add_argument("--url", action="append", default=[])
    research.add_argument("--file", action="append", default=[])
    research.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    if args.command == "research":
        report = MultiAspectResearch(settings.web_search_url).run(
            args.question, urls=args.url, files=args.file, top_k=args.top_k
        )
        print(json.dumps({
            "question": report.question,
            "aspects": report.aspects,
            "sources": [s.__dict__ for s in report.sources],
            "warnings": report.warnings,
        }, indent=2, ensure_ascii=False))
