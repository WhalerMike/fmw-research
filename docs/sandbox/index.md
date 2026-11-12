# ServiceNow sandbox test packs

!!! info "Research notes, not workbook guidance"
    **Status:** Open · **Last checked:** 2026-11-12 · **Baseline:** Microsoft 365 GCC Moderate

These packs turn the open questions from
[Scheduling a daily report job](../topics/daily-report-scheduling.md) into tests you can run in a
ServiceNow sandbox. They are written to be copied into a work environment and run there.

!!! warning "Steps are drafts until a sandbox run confirms them"
    The steps come from ServiceNow and Microsoft documentation and community reports, not from a
    run in a real instance. Menu names and script APIs differ between ServiceNow releases. Where
    a step fails, the failure is itself a finding: record it.

## How the packs are used

| Here (public) | At work |
|---|---|
| The pack: steps, commands, pass criteria, a Copilot prompt | Run the pack in the sandbox |
| A blank [results template](results-template.md) | Fill it in and keep it on work storage |
| The research log | Retype only a **generic** finding for it, with no instance names, hosts, accounts or screenshots |

Placeholders look like `<mid-server-name>`. Replace each one at work. Example names such as
`gmsa-midrpt` are fictional.

## What is a MID Server?

ServiceNow runs in the cloud and can't reach inside your network by itself. A **MID Server**
(Management, Instrumentation and Discovery Server) is a small Java application that you install
on a Windows or Linux server **inside** your network. It runs as a Windows service.

- It **calls out** to the ServiceNow instance over HTTPS and asks for work. The instance never
  connects in to it, so no inbound firewall opening is needed.
- The instance hands it jobs (Discovery scans, PowerShell commands, LDAP or JDBC reads, scripts).
  The MID Server runs them locally and posts the results back.
- Jobs run under the **Windows account the service runs as**, unless the job uses a credential
  stored in the instance. That is why the MID Server can run as a gMSA: the account's password
  is managed by Active Directory, and the instance stores nothing.
- Work passes through the **ECC queue** (External Communication Channel) table in the instance:
  an *output* record is a job sent to the MID Server; an *input* record is its result.

In the daily report design, the MID Server does the on-premises reads that today's scheduled
task does, and the instance does the schedule, the record and the mail.

## The packs

| Pack | Question it answers | Status |
|---|---|---|
| [1. MID Server running as a gMSA](pack-1-mid-server-gmsa.md) | Can the MID Server service run as a gMSA, and does it need local admin? | Open |
| [2. Using the service account for on-premises reads](pack-2-service-account-credential.md) | Do jobs on the MID Server read AD as the gMSA, with no stored password? Does the AD v2 spoke? | Open |
| [3. Scheduled job on workdays](pack-3-scheduled-workdays.md) | Does a daily schedule skip weekends and start on time? | Open |
| [4. Graph from the instance with a certificate](pack-4-graph-certificate.md) | Can the instance call Microsoft Graph with a certificate instead of a secret? | Open |
| [5. Report as a record plus instance email](pack-5-record-and-email.md) | Can the report be kept as a record and mailed by the instance, and what retention applies? | Open |

Run them in order. Packs 2 and 5 need pack 1; pack 5 can use pack 3's schedule.

## Getting the packs to work

[:material-download: Download the sandbox packs (zip)](https://whalermike.github.io/fmw-research/downloads/fmw-sandbox-packs.zip){ .md-button .md-button--primary }

The zip comes from this website, not GitHub, and is rebuilt every time the site changes, so it
always matches these pages. It holds the [InBox overview](../inbox/index.md), the Copilot
[start package](../inbox/001-start-package.md), this overview, the five packs, the results
template, the three research topics behind them with the sources page, and a `README.txt`,
all as Markdown. Every link inside points back to this site.

A fixed snapshot is also kept on GitHub as the
[sandbox-packs-2026-11-12 release](https://github.com/WhalerMike/fmw-research/releases/tag/sandbox-packs-2026-11-12). Nothing at work needs to connect back to this repository.
