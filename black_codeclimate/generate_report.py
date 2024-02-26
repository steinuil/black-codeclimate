import hashlib
from typing import List, TypedDict

from unidiff import PatchSet


class CodeClimateIssueLocationLines(TypedDict):
    begin: int
    end: int


class CodeClimateIssueLocation(TypedDict):
    path: str
    lines: CodeClimateIssueLocationLines


class CodeClimateIssue(TypedDict):
    type: str
    fingerprint: str
    location: CodeClimateIssueLocation
    categories: List[str]
    severity: str
    description: str
    check_name: str


def generate_report(
    patch_set: PatchSet, severity: str, description: str, check_name: str
) -> List[CodeClimateIssue]:
    issues: List[CodeClimateIssue] = []

    for patched_file in patch_set:
        for hunk in patched_file:
            # Note: this reports only one issue even if multiple separated in a
            # single hunk are affected but whatever
            begin: int = 0
            for line in hunk.source_lines():
                if line.is_removed:
                    begin = line.source_line_no

            if not begin:
                continue

            # This also kind of breaks when there's more than one chunk of separated lines
            # affected.
            line_count: int = 0
            for line in hunk.source_lines():
                if line.is_removed:
                    line_count += 1

            fingerprint = ""

            for line in hunk:
                if line.is_added:
                    line_no = line.target_line_no
                elif line.is_removed:
                    line_no = line.source_line_no
                else:
                    continue

                fingerprint += f"{patched_file}:{line_no}:{line.line_type}{line.value}"

            issues.append(
                {
                    "fingerprint": hashlib.sha256(
                        fingerprint.encode("utf-8")
                    ).hexdigest(),
                    "location": {
                        "path": patched_file.source_file,
                        "lines": {"begin": begin, "end": begin + line_count - 1},
                    },
                    "severity": severity,
                    "description": description,
                    "check_name": check_name,
                    "type": "issue",
                    "categories": ["Style"],
                }
            )

    return issues
