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


def create_issue(
    fingerprint: str,
    path: str,
    begin: int,
    end: int,
    severity: str,
    description: str,
    check_name: str,
) -> CodeClimateIssue:
    return {
        "fingerprint": hashlib.sha256(fingerprint.encode("utf-8")).hexdigest(),
        "location": {
            "path": path,
            "lines": {"begin": begin, "end": end},
        },
        "severity": severity,
        "description": description,
        "check_name": check_name,
        "type": "issue",
        "categories": ["Style"],
    }


def generate_report(
    patch_set: PatchSet, severity: str, description: str, check_name: str
) -> List[CodeClimateIssue]:
    issues: List[CodeClimateIssue] = []

    for patched_file in patch_set:
        for hunk in patched_file:
            source_lines = list(hunk.source_lines())

            line_i = 0

            # There might be several unrelated changes in a single hunk.
            # We detect that by collecting contiguous non-context lines
            # and generating a different issue for each block.
            while True:
                block_lines = []

                # Skip context lines
                while line_i < len(source_lines) and source_lines[line_i].is_context:
                    line_i += 1
                    continue

                if line_i >= len(source_lines):
                    break

                line = source_lines[line_i]

                if line.source_line_no:
                    # Line was removed, set this as the starting line
                    begin = line.source_line_no
                else:
                    # Line was added, get the source_line_no from one line back + 1
                    begin = (source_lines[line_i - 1].source_line_no or 0) + 1

                # Add changed lines to block_lines
                while line_i < len(source_lines) and not line.is_context:
                    line = source_lines[line_i]
                    block_lines.append(line)

                    line_i += 1

                # Count removed lines and prepare fingerprint
                line_count = 0
                fingerprint = ""
                for line in block_lines:
                    if line.is_removed:
                        line_count += 1
                        line_no = line.target_line_no
                    else:
                        line_no = line.source_line_no

                    fingerprint += (
                        f"{patched_file}:{line_no}:{line.line_type}{line.value}"
                    )

                # Only added lines. Set the line_count to 1 to make sure
                # we don't report a location end that's before the start
                if line_count == 0:
                    line_count = 1

                issues.append(
                    create_issue(
                        fingerprint=fingerprint,
                        path=patched_file.source_file,
                        begin=begin,
                        end=begin + line_count - 1,
                        severity=severity,
                        description=description,
                        check_name=check_name,
                    )
                )

    return issues
