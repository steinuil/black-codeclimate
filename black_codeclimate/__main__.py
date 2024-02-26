import argparse
import json
import sys

from unidiff import PatchSet

from black_codeclimate.generate_report import generate_report


def main():
    parser = argparse.ArgumentParser(
        prog="black-codeclimate",
        description="Convert the output of black --diff into a Code Climate report",
    )
    parser.add_argument(
        "--severity",
        help="Severity of the violations (default: major)",
        choices=["info", "minor", "major", "critical", "blocker"],
        default="major",
        type=str,
    )
    parser.add_argument(
        "--description",
        help="Description of the Code Climate issue (default: 'Black would reformat')",
        default="Black would reformat",
        type=str,
    )
    parser.add_argument(
        "--check-name",
        help="A unique name of the static analysis check that emitted this issue (default: inconsistent-format-black)",
        default="inconsistent-format-black",
        type=str,
    )
    parser.add_argument(
        "filename",
        help="File containing the output of black --diff. If not specified or specified as -, input from stdin will be used.",
        nargs="?",
        default="-",
        type=str,
    )
    args = parser.parse_args()

    if args.filename == "-":
        patch_set = PatchSet(sys.stdin)
    else:
        with open(args.filename) as f:
            patch_set = PatchSet(f)

    violations = generate_report(
        patch_set,
        severity=args.severity,
        description=args.description,
        check_name=args.check_name,
    )

    print(json.dumps(violations))


if __name__ == "__main__":
    main()
