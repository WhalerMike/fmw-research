# InBox 001: Start package for Copilot

| | |
|---|---|
| **To** | Copilot working inside the work environment (Microsoft 365 Copilot Chat or GitHub Copilot) |
| **From** | The FMW Research project (public side) |
| **Date** | 2026-11-12 |
| **Replaces** | Nothing. This is the first note. |
| **Read time** | About 15 minutes |

This note is published at
<https://whalermike.github.io/fmw-research/inbox/001-start-package/>.

This note gives you everything you need to help run the ServiceNow sandbox test packs inside
the work environment, without needing access to the public internet. Key facts are written out
in full here; links are for reference only.

---

## 1. Who you are working with and why

The person carrying this note runs a public research project called **FMW Research**. It sits
beside the Federal Modernization Workbook, a public set of books on federal IT modernization.
The research asks what cloud and service-management tools can do, and records the answers with
sources. It is not guidance, and it is kept separate from the workbook.

Some questions can only be answered by testing in a real ServiceNow instance. That sandbox is
inside the work environment. So the work splits in two:

| Public side (outside) | Your side (inside) |
|---|---|
| Writes research, test packs, prompts and notes like this one | Runs the tests in the ServiceNow sandbox |
| Never sees work data | Holds all real names, hosts, output and screenshots |
| Receives only a short generic finding, retyped by hand | Helps write up results and the generic finding |

Your job is to help with the inside half: understand a pack, adapt its placeholders to the
sandbox, run and troubleshoot the steps, fill in the results template, and draft the generic
finding.

---

## 2. Ground rules

These rules come first. If a request conflicts with them, point that out.

1. **Nothing inside goes outside automatically.** No pushes, syncs, forks, pull requests or
   copy-paste from the work environment to the public repository.
2. **Only the generic finding leaves.** It is one to three sentences with no instance, host,
   server, account, domain, tenant, mailbox or person names, no IDs, no output and no
   screenshots. The person retypes it by hand.
3. **Never name the organization** in anything meant for the outside, and never describe its
   status, systems or plans.
4. **Sandbox only.** Every pack is written for a ServiceNow sandbox and a test domain or test
   tenant. Don't run pack steps against production.
5. **No stored secrets beyond the test.** Pack 4 uses a 7-day client secret only to prove a
   call, then deletes it. Nothing else stores a password.
6. **Careful wording.** A tool *supports* or *addresses* a requirement. Don't write that it
   satisfies or meets one.
7. **The baseline is Microsoft 365 GCC Moderate** (or an equivalent tenant). In GCC Moderate,
   Entra ID runs in commercial Azure, and the endpoints are `login.microsoftonline.com` and
   `graph.microsoft.com`. GCC High and DoD differ; treat them only as side notes.
8. **Mark guesses.** If something is your inference rather than documented or observed, say so.

---

## 3. The question behind the packs

A **daily report job** runs today as a Windows scheduled task under a **group managed service
account (gMSA)**. It reads directory and service data once a day and mails a summary. The
research asked whether it could run somewhere better. Four options were compared:

| Option | Schedule | Identity for on-premises reads | Mail | Where the output lives |
|---|---|---|---|---|
| Windows task as the gMSA (today) | Task Scheduler on one server | gMSA | Graph `Mail.Send` or an on-premises relay | Mail and files on the server |
| Azure Automation (cloud sandbox or Hybrid Runbook Worker) | Azure schedule | Hybrid worker runs as the server's computer account or a stored username and password; **a gMSA can't be used** (inference) | Graph `Mail.Send` | Job history, kept 30 days at most |
| gMSA task plus Azure Arc managed identity | Task Scheduler | gMSA | Graph `Mail.Send` under the Arc identity | Mail and files on the server |
| **ServiceNow scheduled flow plus MID Server** | Instance scheduled trigger | **gMSA as the MID Server's service account** | The instance's own email | A ServiceNow record |

The ServiceNow option looks strongest when the report reads on-premises data or should end up
in the ticketing system, because:

- the gMSA stays, so no password is stored;
- the instance sends the mail, so no app needs Graph `Mail.Send` (whose mailbox scoping,
  RBAC for Applications, isn't confirmed for GCC);
- the report becomes a record with the instance's history and access controls.

The research also found open questions and community reports that only a sandbox can settle.
The five packs test them.

### Other findings you may be asked about

- **Microsoft 365 Copilot scheduled prompts are not available in GCC**, so Copilot can't run
  the report on a timer.
- **Copilot Studio triggers and autonomous agents are not available in GCC or GCC High.**
- **Copilot Studio** bills in Copilot Credits (1 classic answer, 2 generative answer, 5 agent
  action, 10 Graph grounding, 13 per 100 agent-flow actions). It's free for a Copilot-licensed
  user's own conversations; autonomous runs are always billed.

---

## 4. What a MID Server is

ServiceNow runs in the cloud and can't reach inside the network on its own. A **MID Server**
(Management, Instrumentation and Discovery Server) is a Java application installed on a server
inside the network, where it runs as a Windows service.

- It **connects out** to the instance over HTTPS and asks for work. No inbound firewall
  opening is needed.
- The instance gives it jobs: PowerShell, LDAP or JDBC reads, Discovery scans, JavaScript
  probes. It runs them locally and posts results back.
- Work passes through the **ECC queue** table (`ecc_queue`): an *output* record is a job sent
  to the MID Server; an *input* record is its result.
- Jobs run as **the account the service runs as**, unless the job uses a credential stored in
  the instance. For PowerShell, the MID Server tries stored Windows credentials first and falls
  back to the service account; when the target is the MID host itself, it uses the service
  account directly.
- The Windows service is normally named `snc_mid_<mid-server-name>`. Logs are in
  `<install-folder>\agent\logs\`, main file `agent0.log.0`.

---

## 5. The five packs

The full packs are web pages on the research site:

| Pack | Web page |
|---|---|
| Overview | <https://whalermike.github.io/fmw-research/sandbox/> |
| 1. MID Server running as a gMSA | <https://whalermike.github.io/fmw-research/sandbox/pack-1-mid-server-gmsa/> |
| 2. Service account for on-premises reads | <https://whalermike.github.io/fmw-research/sandbox/pack-2-service-account-credential/> |
| 3. Scheduled job on workdays | <https://whalermike.github.io/fmw-research/sandbox/pack-3-scheduled-workdays/> |
| 4. Graph from the instance with a certificate | <https://whalermike.github.io/fmw-research/sandbox/pack-4-graph-certificate/> |
| 5. Report as a record plus instance email | <https://whalermike.github.io/fmw-research/sandbox/pack-5-record-and-email/> |
| Results template | <https://whalermike.github.io/fmw-research/sandbox/results-template/> |

They also come as a zip (`fmw-sandbox-packs-2026-11-12.zip`) for anyone who can download from
GitHub. Run them in order. Packs 2 and 5 depend on pack 1.

**All steps are drafts.** They come from ServiceNow and Microsoft documentation and community
reports, not from a run in a real instance. Menu names and script APIs differ between
ServiceNow releases. When a step fails, the failure is a finding: record what happened and what
worked instead.

### Pack 1: MID Server running as a gMSA

- **Question:** can the MID Server service run as a gMSA, and does the gMSA need local admin?
- **Why:** ServiceNow's gMSA page says in its prerequisites to add the gMSA to the MID host's
  local Administrators group, but its benefits section says that isn't needed.
- **Outline:** create the gMSA (`New-ADServiceAccount`, allowed only for the MID host);
  `Install-ADServiceAccount` and `Test-ADServiceAccount` on the host; install the MID Server
  with defaults first; switch the service with
  `sc.exe config "snc_mid_<name>" obj= "<DOMAIN>\gmsa-midrpt$" password= ""`; check it's Up
  and validated **without** local admin; add local admin only if that fails.
- **Watch for:** error 1069 (logon failure). The fix reported by the community: set the account
  once in `services.msc` (Log On tab, blank passwords), which grants "Log on as a service". The
  gMSA may also need modify rights on the install folder.

### Pack 2: Using the service account for on-premises reads

- **Question:** do jobs on the MID Server read AD as the gMSA with no stored password? Does the
  AD v2 spoke work the same way?
- **Outline:** confirm the gMSA is in no privileged groups; send a `JavascriptProbe` from
  **Scripts - Background** that runs PowerShell `whoami` and an `[adsisearcher]` lookup of a test
  user; read the result in **ECC > Queue** (input record); create a Windows credential using the
  MID Server service account option ("Use MID Server Service Account") and test it; if licensed,
  try the AD v2 spoke.
- **Watch for:** the release may block `Packages` (Java) access from probes; record it and try
  the IntegrationHub PowerShell step. Community reports say the AD v2 spoke may not honour the
  service-account credential.

### Pack 3: Scheduled job on workdays

- **Question:** does a daily schedule skip weekends, and how late does it start?
- **Outline:** (A) a Scheduled Script Execution, Daily, **Conditional** with
  `new GlideDateTime().getDayOfWeekLocalTime() <= 5` (1 is Monday, 7 is Sunday), logging a line
  with `gs.info`; (B) a scheduled flow with an **If** that ends the flow on Saturday or Sunday.
  Run both for one week.
- **Watch for:** schedules use the instance time zone (`glide.sys.default.tz`). Flows are
  queued, so they may start late in business hours. Record the largest delay.

### Pack 4: Graph from the instance with a certificate

- **Question:** can the instance call Microsoft Graph with an app registration and a
  **certificate**, so no client secret is stored?
- **Outline:** create an app registration with only `Organization.Read.All` (application) using
  Microsoft Graph PowerShell; stage A proves `GET https://graph.microsoft.com/v1.0/organization`
  through an OAuth registry entry and REST message with a 7-day secret; stage B uploads a
  certificate (convert PFX to JKS with the MID Server's `keytool` if needed), creates a JWT key
  and JWT provider, and switches the token request to a client assertion; then the secret is
  deleted and the call is retested.
- **Watch for:** ServiceNow documents certificate client credentials for **SMTP**; whether it
  works for a REST message is the open question. Microsoft needs the certificate thumbprint as
  `x5t` in the JWT header. Known errors: **AADSTS700027** (certificate not registered on the app)
  and **AADSTS900144** (missing `requested_token_use`).

### Pack 5: Report as a record plus instance email

- **Question:** can the report be kept as a record with an attachment and mailed by the
  instance? What retention and access apply?
- **Outline:** check **Email Properties** (sending enabled, any test redirect such as
  `glide.email.test.user`) without changing a shared sandbox; create table `u_fmw_daily_report`;
  a background script inserts a record, attaches `daily-report.txt` with `GlideSysAttachment`,
  and inserts a `sys_email` record of type `send-ready`; check **Outbound > Sent**; check
  **Auto Flush** (`sys_auto_flush`) and archive rules; check the table's ACLs and impersonate a
  user with no roles.
- **Watch for:** if direct `sys_email` inserts are ignored, use a flow with the core **Send
  Email** action (no IntegrationHub licence needed).

---

## 6. How to help run a pack

1. **Read the pack** and list every placeholder (`<mid-server-name>`, `<mid-host>`,
   `<DOMAIN>`, `<domain-fqdn>`, `<test-user>`, `<install-folder>`, `<tenant-id>`,
   `<test-mailbox>`). Ask for each value. Keep the values inside.
2. **Check prerequisites** before the first step: roles, rights, licences, a test user or test
   mailbox, and that the target is a sandbox.
3. **Give one step at a time** with the placeholders filled in. Wait for the output before the
   next step.
4. **When a step fails,** explain the error, suggest one fix at a time, and note it for the
   results template's "Steps that differed" and "Errors" tables.
5. **At the end,** fill in the results template from the notes and output, check the pass
   criteria, and draft the generic finding.
6. **Before anything leaves,** check the generic finding against the ground rules in section 2.

---

## 7. Ready to paste: instructions for GitHub Copilot

If the packs are kept in a work repository, save this as `.github/copilot-instructions.md`
there so GitHub Copilot follows the same rules.

```markdown
# Copilot instructions: ServiceNow sandbox test packs

This repository holds copies of the FMW Research ServiceNow sandbox test packs and their
results. The packs are public; the results are internal.

- Run pack steps only against the ServiceNow sandbox and test domain or tenant, never production.
- Results stay in this repository. Never suggest pushing, syncing or copying them anywhere else.
- Fill results in a copy of results-template.md, one file per run: results/pack-N-YYYY-MM-DD.md.
- Keep placeholder values (hosts, accounts, domains, tenant and client IDs, mailboxes) in the
  results files only, never in the pack files.
- The "Generic finding" section is one to three sentences with no names, IDs, output or
  screenshots, and never names the organization.
- Steps are drafts. When a step fails, record what happened and what worked instead.
- Write "supports" or "addresses", not "satisfies" or "meets".
- Mark inference as inference.
```

---

## 8. Prompts

Use these in Microsoft 365 Copilot Chat or GitHub Copilot Chat. Paste the pack text or point to
the file when asked.

**Start a pack**

> Here is test pack N for a ServiceNow sandbox: [paste or attach]. List every placeholder I
> need to fill in, every prerequisite I should check first, and any step you think may differ
> on our ServiceNow release. Then give me step 1 only, with the placeholders filled in from
> these values: [values].

**Troubleshoot a step**

> Step N of pack N failed. Here is the command and the output: [paste]. Explain the error in
> plain words, give the most likely cause, and suggest one fix. Note this for the "Errors"
> table of the results template.

**Fill in the results**

> Here are my notes and output from running pack N: [paste]. Fill in the results template:
> pass criteria with results, steps that differed from the pack, errors and fixes, and notes.

**Draft the generic finding**

> From these results: [paste], write a generic finding of one to three sentences. Include the
> ServiceNow release and what worked or failed. Leave out every name of an instance, host,
> server, account, domain, tenant, mailbox, person or organization, every ID and all output.
> Then check your own sentence against those rules and list anything you removed.

**Check before it leaves**

> Check this text before it is shared outside: [paste]. Flag any name, ID, host, IP address,
> URL of an internal system, organization name, or output. Say "clear" only if there is none.

The pack-specific prompts are at the end of each pack.

---

## 9. Getting results back to the research side

Only this leaves, retyped by hand:

```text
Pack: N (short name)
Date run: YYYY-MM-DD
ServiceNow release: <release name>
Result: Pass / Partly / Fail
Generic finding: <one to three sentences>
```

The research side then updates the pack's status (Open → Findings) and the research log.

---

## 10. Glossary

| Term | Meaning |
|---|---|
| gMSA | Group managed service account. An AD account whose password Active Directory sets and rotates; only allowed hosts can use it. |
| KDS root key | The domain key that gMSA passwords are derived from. Needed once per forest. |
| MID Server | ServiceNow's on-premises agent; see section 4. |
| ECC queue | The `ecc_queue` table that carries jobs to the MID Server and results back. |
| JavascriptProbe | A ServiceNow API that sends a JavaScript job to a MID Server. |
| Windows credential | A credential record in the instance that MID Server jobs use for Windows targets. |
| Spoke | An IntegrationHub connector package (for example AD v2, Microsoft Entra ID). Some need a separate subscription. |
| Scheduled Script Execution | A scheduled job (`sysauto_script`) that runs a server script on a schedule. |
| Flow, Flow Designer, Workflow Studio | ServiceNow's low-code automation; Workflow Studio is the newer home of Flow Designer. |
| OAuth Application Registry | Where the instance stores how it gets tokens from another service. |
| JWT key, JWT provider | Instance records that sign a JSON Web Token with a certificate, used for a client assertion. |
| Client assertion | A signed token an app sends instead of a client secret to prove who it is. |
| `x5t` | The JWT header claim holding the certificate thumbprint; Microsoft Entra needs it. |
| Auto Flush | The `sys_auto_flush` table that deletes old records from a table after a set time. |
| ACL | Access control rule in ServiceNow. |
| RBAC for Applications | Exchange Online feature that limits which mailboxes an app can use. |
| GCC Moderate | Microsoft 365 Government Community Cloud, the baseline for this research. |

---

## 11. Open questions the packs should settle

| # | Question | Pack |
|---|---|---|
| 1 | Does the gMSA need local admin on the MID host? | 1 |
| 2 | Does the error 1069 workaround hold on the current release? | 1 |
| 3 | Do probes run as the gMSA and read AD without a stored password? | 2 |
| 4 | Are Java `Packages` calls allowed in JavascriptProbe on this release? | 2 |
| 5 | Does the AD v2 spoke accept the MID Server service-account credential? | 2 |
| 6 | Do workday-only schedules skip weekends, and how late do flows start? | 3 |
| 7 | Can a REST message use certificate client credentials to Microsoft Graph? | 4 |
| 8 | Are direct `sys_email` inserts sent, or is a flow needed? | 5 |
| 9 | What retention applies to the report records and the sent mail? | 5 |
| 10 | Which ServiceNow government offering is in use, and does it change any of the above? | All |

---

## 12. Future notes

Later notes will be `002-...md`, `003-...md` and so on in this InBox, each saying what it
replaces. If a pack changes, the note will say which steps changed so a run in progress can
continue.
