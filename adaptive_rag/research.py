from __future__ import annotations

import ipaddress
import json
import re
import socket
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlparse
from urllib.request import Request, urlopen

from .models import Evidence
from .services import ingest_text


@dataclass(frozen=True)
class ResearchSource:
    source: str
    text: str
    kind: str


@dataclass(frozen=True)
class ResearchReport:
    question: str
    aspects: list[str]
    sources: list[ResearchSource]
    evidence: list[Evidence]
    warnings: list[str]


class MultiAspectResearch:
    """Cloud-optional research with safe URL and local-file fallbacks."""

    def __init__(self, cloud_endpoint: str = "", timeout: float = 10.0):
        self.cloud_endpoint = cloud_endpoint.strip()
        self.timeout = timeout

    @staticmethod
    def aspects(question: str) -> list[str]:
        q = question.lower()
        aspects = [
            "core facts",
            "evidence and sources",
            "risks and limitations",
        ]

        if any(
            word in q
            for word in ("compare", "versus", " vs ", "difference")
        ):
            aspects += [
                "comparison criteria",
                "trade-offs",
            ]

        if any(
            word in q
            for word in ("how", "build", "implement", "architecture")
        ):
            aspects += [
                "implementation approach",
                "architecture and workflow",
            ]

        if any(
            word in q
            for word in ("latest", "current", "today", "recent")
        ):
            aspects += ["recent developments"]

        return list(dict.fromkeys(aspects))

    @staticmethod
    def _validate_url(url: str) -> None:
        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            raise ValueError(
                f"unsupported URL scheme: {parsed.scheme}"
            )

        if not parsed.hostname:
            raise ValueError("URL hostname is required")

        hostname = parsed.hostname.strip().lower()

        if hostname in {
            "localhost",
            "localhost.localdomain",
            "ip6-localhost",
            "ip6-loopback",
        }:
            raise ValueError(
                f"blocked internal hostname: {hostname}"
            )

        try:
            direct_ip = ipaddress.ip_address(hostname)
        except ValueError:
            direct_ip = None

        if direct_ip is not None:
            if (
                direct_ip.is_private
                or direct_ip.is_loopback
                or direct_ip.is_link_local
                or direct_ip.is_reserved
                or direct_ip.is_multicast
                or direct_ip.is_unspecified
            ):
                raise ValueError(
                    f"blocked internal IP address: {direct_ip}"
                )
            return

        try:
            addresses = socket.getaddrinfo(
                hostname,
                parsed.port or (443 if parsed.scheme == "https" else 80),
                type=socket.SOCK_STREAM,
            )
        except OSError as exc:
            raise ValueError(
                f"hostname resolution failed: {hostname}"
            ) from exc

        resolved_ips = {
            sockaddr[4][0]
            for sockaddr in addresses
            if sockaddr and sockaddr[4]
        }

        if not resolved_ips:
            raise ValueError(
                f"hostname resolved to no addresses: {hostname}"
            )

        for address in resolved_ips:
            ip = ipaddress.ip_address(address)

            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_reserved
                or ip.is_multicast
                or ip.is_unspecified
            ):
                raise ValueError(
                    f"blocked internal address for {hostname}: {ip}"
                )

    def _cloud(
        self,
        query: str,
        top_k: int,
    ) -> list[ResearchSource]:
        if not self.cloud_endpoint:
            return []

        self._validate_url(self.cloud_endpoint)

        separator = "&" if "?" in self.cloud_endpoint else "?"
        url = (
            f"{self.cloud_endpoint}"
            f"{separator}q={quote_plus(query)}&limit={top_k}"
        )

        request = Request(
            url,
            headers={"User-Agent": "AdaptiveRAG-X/1.2"},
        )

        with urlopen(request, timeout=self.timeout) as response:
            payload = json.load(response)

        results = payload.get(
            "results",
            payload if isinstance(payload, list) else [],
        )

        return [
            ResearchSource(
                source=str(item.get("url", "cloud")),
                text=str(
                    item.get(
                        "text",
                        item.get(
                            "snippet",
                            item.get("title", ""),
                        ),
                    )
                ),
                kind="cloud",
            )
            for item in results[:top_k]
            if item.get(
                "text",
                item.get(
                    "snippet",
                    item.get("title", ""),
                ),
            )
        ]

    def _url(self, url: str) -> ResearchSource:
        self._validate_url(url)

        request = Request(
            url,
            headers={"User-Agent": "AdaptiveRAG-X/1.2"},
        )

        with urlopen(request, timeout=self.timeout) as response:
            raw = response.read().decode(
                "utf-8",
                errors="ignore",
            )

        text = re.sub(
            r"<script[\s\S]*?</script>|<style[\s\S]*?</style>",
            " ",
            raw,
            flags=re.IGNORECASE,
        )
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        return ResearchSource(
            source=url,
            text=text[:120_000],
            kind="direct_url",
        )

    @staticmethod
    def _local(path: str) -> ResearchSource:
        file_path = Path(path).expanduser().resolve()

        if not file_path.is_file():
            raise FileNotFoundError(file_path)

        text = file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        return ResearchSource(
            source=str(file_path),
            text=text[:120_000],
            kind="local",
        )

    def run(
        self,
        question: str,
        *,
        urls: list[str] | None = None,
        files: list[str] | None = None,
        top_k: int = 5,
    ) -> ResearchReport:
        aspects = self.aspects(question)
        sources: list[ResearchSource] = []
        warnings: list[str] = []

        try:
            for aspect in aspects:
                sources.extend(
                    self._cloud(
                        f"{question} {aspect}",
                        top_k,
                    )
                )
        except (
            HTTPError,
            URLError,
            TimeoutError,
            OSError,
            ValueError,
        ) as exc:
            warnings.append(
                f"cloud search unavailable: {exc}"
            )

        for url in urls or []:
            try:
                sources.append(self._url(url))
            except (
                HTTPError,
                URLError,
                TimeoutError,
                OSError,
                ValueError,
            ) as exc:
                warnings.append(
                    f"direct URL failed ({url}): {exc}"
                )

        for path in files or []:
            try:
                sources.append(self._local(path))
            except (
                OSError,
                UnicodeError,
            ) as exc:
                warnings.append(
                    f"local file failed ({path}): {exc}"
                )

        if not sources:
            warnings.append(
                "no external sources available; "
                "research returned an empty evidence set"
            )

        unique: dict[str, ResearchSource] = {}

        for source in sources:
            unique.setdefault(
                f"{source.source}:{source.text[:200]}",
                source,
            )

        sources = list(unique.values())

        evidence = [
            Evidence(
                document_id=f"research-{index}",
                text=source.text,
                score=max(
                    0.1,
                    1.0 - index * 0.05,
                ),
                source=source.source,
                rank=index,
                metadata={"kind": source.kind},
            )
            for index, source in enumerate(
                sources[: max(top_k * 4, top_k)],
                start=1,
            )
        ]

        return ResearchReport(
            question,
            aspects,
            sources,
            evidence,
            warnings,
        )

    def ingest(self, report: ResearchReport):
        """Convert research evidence into pipeline documents."""
        documents = []

        for source in report.sources:
            documents.extend(
                ingest_text(
                    source.text,
                    source.source,
                    {"research_kind": source.kind},
                )
            )

        return documents