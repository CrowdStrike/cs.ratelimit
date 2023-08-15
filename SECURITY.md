![CrowdStrike cs.ratelimit](https://raw.githubusercontent.com/CrowdStrike/cs.ratelimit/main/docs/asset/cs-logo.png)

# Security Policy
This document outlines security policy and procedures for the CrowdStrike `cs.ratelimit` project.

+ [Supported Python versions](#supported-python-versions)
+ [Supported cs.ratelimit versions](#supported-csratelimit-versions)
+ [Reporting a potential security vulnerability](#reporting-a-potential-security-vulnerability)
+ [Disclosure and Mitigation Process](#disclosure-and-mitigation-process)

## Supported Python versions

cs.ratelimit supports the following versions of Python.

| Version   | Supported  |
| :-------- | :--------: |
| 3.12.x    | ![Yes](https://img.shields.io/badge/-YES-green) |
| 3.11.x    | ![Yes](https://img.shields.io/badge/-YES-green) |
| 3.10.x    | ![Yes](https://img.shields.io/badge/-YES-green) |
| 3.9.x     | ![Yes](https://img.shields.io/badge/-YES-green) |
| 3.8.x     | ![Yes](https://img.shields.io/badge/-YES-green) |
| <= 3.7.x  | ![No](https://img.shields.io/badge/-NO-red) |
| <= 2.x.x  | ![No](https://img.shields.io/badge/-NO-red) |

## Supported cs.ratelimit versions

When discovered, we release security vulnerability patches for the most recent release at an accelerated cadence.

## Reporting a potential security vulnerability

We have multiple avenues to receive security-related vulnerability reports.

Please report suspected security vulnerabilities by:
+ Submitting a [bug](https://github.com/CrowdStrike/cs.ratelimit/issues/new?assignees=&labels=bug+%3Abug%3A&template=bug_report.md&title=%5B+BUG+%5D+...).
+ Submitting a [pull request](https://github.com/CrowdStrike/cs.ratelimit/pulls) to potentially resolve the issue. (New contributors: please review the content located [here](https://github.com/CrowdStrike/cs.ratelimit/blob/main/CONTRIBUTING.md).)
+ Sending an email to __oss-security@crowdstrike.com__.

## Disclosure and mitigation process

Upon receiving a security bug report, the issue will be assigned to one of the project maintainers. This person will coordinate the related fix and release
process, involving the following steps:
+ Communicate with you to confirm we have received the report and provide you with a status update.
    - You should receive this message within 48 - 72 business hours.
+ Confirmation of the issue and a determination of affected versions.
+ An audit of the codebase to find any potentially similar problems.
+ Preparation of patches for all releases still under maintenance.
    - These patches will be submitted as a separate pull request and contain a version update.
    - This pull request will be flagged as a security fix.
    - Once merged, and after post-merge unit testing has been completed, the patch will be immediately published to both PyPI repositories.


---

<p align="center">
  <img src="https://raw.githubusercontent.com/CrowdStrike/cs.ratelimit/main/docs/img/cs-logo-footer.png"><br/>
  <img width="300px" src="https://raw.githubusercontent.com/CrowdStrike/cs.ratelimit/main/docs/img/adversary-goblin-panda.png">
</p>
<h3><p align="center">WE STOP BREACHES</p></h3>