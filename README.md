# `black-codeclimate`

Convert the output of `black --diff` to a report conforming to the [Code Climate spec](https://github.com/codeclimate/platform/blob/master/spec/analyzers/SPEC.md). It is aimed at GitLab CI, for which it can generate a [Code Quality report](https://docs.gitlab.com/ee/ci/testing/code_quality.html).

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
black-codeclimate --severity blocker --description "Would reformat" --check-name "black" black.diff > black_report.json
```

To include in GitLab CI:

```yaml
lint:black:
  stage: lint
  script:
    - # Install black and black-codeclimate...
    - black --diff src/ | black-codeclimate > black_report.json
  artifacts:
    reports:
      codequality: black_report.json
    when: always
```
