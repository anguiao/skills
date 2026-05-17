#!/usr/bin/env python3
"""Select a current Gemini model from Models.dev."""

from __future__ import annotations

import argparse
import json
import shlex
import sys
import urllib.request
from dataclasses import dataclass
from typing import Any, Iterable


DEFAULT_API_URL = "https://models.dev/api.json"
EXCLUDED_ID_PARTS = ("embedding", "embed", "image", "tts", "live", "audio", "customtools")


@dataclass(frozen=True)
class Candidate:
    provider: str
    model_id: str
    name: str
    status: str
    release_date: str
    last_updated: str
    reasoning: bool
    context: int
    raw: dict[str, Any]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch Models.dev data and choose the best available Google Gemini model."
    )
    parser.add_argument("--api-url", default=DEFAULT_API_URL)
    parser.add_argument("--input", help="Read Models.dev-compatible JSON from a file, or '-' for stdin.")
    parser.add_argument("--provider", default="google")
    parser.add_argument("--prefer", default="pro", help="Preferred model family token.")
    parser.add_argument("--stable-only", action="store_true", help="Exclude preview, alpha, and beta models.")
    parser.add_argument("--list", action="store_true", help="Print all matching Gemini candidates.")
    parser.add_argument("--format", choices=("id", "json", "shell"), default="id")
    return parser.parse_args()


def load_json(args: argparse.Namespace) -> Any:
    if args.input == "-":
        return json.load(sys.stdin)
    if args.input:
        with open(args.input, "r", encoding="utf-8") as file:
            return json.load(file)

    request = urllib.request.Request(
        args.api_url,
        headers={"User-Agent": "codex-gemini-designer-skill/1.0"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def normalized_provider_id(key: str | None, provider: Any) -> str:
    if isinstance(provider, dict):
        for field in ("id", "provider", "provider_id"):
            value = provider.get(field)
            if isinstance(value, str):
                return value
    return key or ""


def iter_model_container(container: Any) -> Iterable[tuple[str, dict[str, Any]]]:
    if isinstance(container, dict):
        for model_id, model in container.items():
            if isinstance(model, dict):
                yield str(model.get("id") or model_id), model
    elif isinstance(container, list):
        for model in container:
            if isinstance(model, dict):
                model_id = model.get("id") or model.get("model") or model.get("model_id")
                if model_id:
                    yield str(model_id), model


def iter_records(data: Any, provider_id: str) -> Iterable[tuple[str, str, dict[str, Any]]]:
    if isinstance(data, dict):
        for key, value in data.items():
            if not isinstance(value, dict):
                continue
            current_provider = normalized_provider_id(str(key), value)
            if current_provider == provider_id and "models" in value:
                for model_id, model in iter_model_container(value.get("models")):
                    yield current_provider, model_id, model
            elif normalized_provider_id(None, value) == provider_id:
                model_id = value.get("id") or value.get("model") or key
                yield provider_id, str(model_id), value
    elif isinstance(data, list):
        for value in data:
            if not isinstance(value, dict):
                continue
            current_provider = normalized_provider_id(None, value)
            if current_provider == provider_id and "models" in value:
                for model_id, model in iter_model_container(value.get("models")):
                    yield current_provider, model_id, model
            elif current_provider == provider_id:
                model_id = value.get("id") or value.get("model") or value.get("model_id")
                if model_id:
                    yield current_provider, str(model_id), value


def modality_has_text(model: dict[str, Any]) -> bool:
    modalities = model.get("modalities")
    if not isinstance(modalities, dict):
        return True
    output = modalities.get("output")
    if not output:
        return True
    return any(str(item).lower() == "text" for item in output)


def parse_limit_context(model: dict[str, Any]) -> int:
    limit = model.get("limit")
    if isinstance(limit, dict):
        value = limit.get("context") or limit.get("input")
        if isinstance(value, int):
            return value
    value = model.get("context") or model.get("context_length")
    return value if isinstance(value, int) else 0


def build_candidate(provider: str, model_id: str, model: dict[str, Any]) -> Candidate | None:
    name = str(model.get("name") or model_id)
    haystack = f"{model_id} {name}".lower()
    status = str(model.get("status") or "").lower()

    if "gemini" not in haystack:
        return None
    if "gemma" in haystack:
        return None
    if any(part in haystack for part in EXCLUDED_ID_PARTS):
        return None
    if status == "deprecated":
        return None
    if not modality_has_text(model):
        return None

    return Candidate(
        provider=provider,
        model_id=model_id,
        name=name,
        status=status,
        release_date=str(model.get("release_date") or ""),
        last_updated=str(model.get("last_updated") or ""),
        reasoning=bool(model.get("reasoning")),
        context=parse_limit_context(model),
        raw=model,
    )


def date_key(value: str) -> tuple[int, int, int]:
    parts = value.split("-")
    try:
        year = int(parts[0]) if len(parts) > 0 and parts[0] else 0
        month = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        day = int(parts[2]) if len(parts) > 2 and parts[2] else 0
        return year, month, day
    except ValueError:
        return 0, 0, 0


def score(candidate: Candidate, prefer: str, stable_only: bool) -> tuple[Any, ...]:
    haystack = f"{candidate.model_id} {candidate.name}".lower()
    status = candidate.status.lower()
    is_preview = "preview" in haystack or status in {"alpha", "beta"}
    if stable_only and is_preview:
        return ()

    return (
        prefer.lower() in haystack,
        date_key(candidate.last_updated),
        date_key(candidate.release_date),
        candidate.reasoning,
        candidate.context,
        "flash" not in haystack,
        candidate.model_id,
    )


def candidate_to_json(candidate: Candidate) -> dict[str, Any]:
    return {
        "provider": candidate.provider,
        "id": candidate.model_id,
        "name": candidate.name,
        "status": candidate.status or None,
        "release_date": candidate.release_date or None,
        "last_updated": candidate.last_updated or None,
        "reasoning": candidate.reasoning,
        "context": candidate.context or None,
    }


def print_candidates(candidates: list[Candidate], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps([candidate_to_json(item) for item in candidates], indent=2, ensure_ascii=False))
    elif output_format == "shell":
        for item in candidates:
            print(f"GEMINI_MODEL={shlex.quote(item.model_id)}")
    else:
        for item in candidates:
            print(item.model_id)


def main() -> int:
    args = parse_args()
    data = load_json(args)
    candidates = [
        candidate
        for provider, model_id, model in iter_records(data, args.provider)
        if (candidate := build_candidate(provider, model_id, model))
    ]
    scored = [
        (candidate_score, candidate)
        for candidate in candidates
        if (candidate_score := score(candidate, args.prefer, args.stable_only))
    ]
    scored.sort(key=lambda item: item[0], reverse=True)
    ordered = [candidate for _, candidate in scored]

    if not ordered:
        print("No available Gemini text model found in Models.dev data.", file=sys.stderr)
        return 1

    if args.list:
        print_candidates(ordered, args.format)
        return 0

    print_candidates([ordered[0]], args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
