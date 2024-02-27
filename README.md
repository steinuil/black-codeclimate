# `black-codeclimate`

[![PyPI version](https://badge.fury.io/py/black-codeclimate.svg)](https://badge.fury.io/py/black-codeclimate)

Convert the output of `black --diff` to a report conforming to the [Code Climate spec](https://github.com/codeclimate/platform/blob/master/spec/analyzers/SPEC.md).
It is made to be used in GitLab CI to generate a [Code Quality report](https://docs.gitlab.com/ee/ci/testing/code_quality.html), which will show a nice widget in merge requests listing the file and the lines affected by the reformatting.

`black-codeclimate` uses [unidiff](https://pypi.org/project/unidiff/) to parse a diff file and detect changes, and outputs a JSON array of Code Climate issue objects reporting the filename and line range of the change. In theory it could be used on any unified diff data, but I only tested it with `black --diff`'s output. Hit me up in the issues if you use it for anything else :)

## Usage

Pipe the output of `black --diff` into `black-codeclimate`:

```bash
black --diff src/ | black-codeclimate > black_report.json
```

Or specify a file to use as input:

```bash
black-codeclimate black.diff > black_report.json
```

You can also change the severity, description and check_name of the issues in the resulting report by specifying command line flags:

```bash
black-codeclimate --severity blocker --description "would reformat [black]" --check-name "black" black.diff > black_report.json
```

Run `black-codeclimate -h` to see a list of the available flags.

## Adding it to GitLab

Add this step to your `.gitlab-ci.yml` file:

```yaml
lint:black:
  stage: lint
  before_script:
    - # Install black and black-codeclimate...
  script:
    # --check fails the job if any inconsistent formatting is detected.
    - black --diff --check src/ > black.diff
  after_script:
    - black-codeclimate black.diff > black_report.json
  artifacts:
    reports:
      codequality: black_report.json
    when: always
```

This will upload the `black_report.json` as a GitLab Code Quality artifact. The lines that would be reformatted by `black` will show up as a [merge request widget](https://docs.gitlab.com/ee/ci/testing/code_quality.html#merge-request-widget).
