# Scheduling a daily report job

!!! info "Research notes, not workbook guidance"
    **Status:** Findings · **Last checked:** 2026-11-12 · **Baseline:** Microsoft 365 GCC Moderate

**Question:** a daily report runs today as a Windows scheduled task under a group managed
service account (gMSA). Could it run as a scheduled cloud task instead, or as an automated task
in ServiceNow?

The example is generic: a job that reads directory and service data once a day and mails a
summary.

**Short answer:** it depends on what the report reads. The gMSA gives the task a Kerberos
identity on the domain. A job that runs in the cloud has no Kerberos identity and can't reach
inside the network. ServiceNow can take over the schedule and the mail, and its MID Server can
keep the gMSA for the on-premises reads.

## Option 1: everything the report reads is in the cloud

Data in Entra, Microsoft 365 or Azure.

- **Azure Automation runbook in the cloud sandbox, on a daily schedule.** Schedules can be one
  time, hourly, daily, weekly or monthly
  ([Manage schedules](https://learn.microsoft.com/azure/automation/shared-resources/schedules)).
- **Identity:** the Automation account's managed identity, with read-only Graph application
  permissions. No server, no gMSA and no stored secret.
- **Mail:** Graph `sendMail`, limited to one shared mailbox through RBAC for Applications. This
  is the pattern in the workbook's
  [service account migration guide, M3](https://whalermike.github.io/modernization-workbook/docs/books/guides/service-account-migration.html#sam-m3),
  which records RBAC for Applications in GCC as not yet specified.
- **Tenant pairing:** a GCC Moderate tenant uses Entra ID in commercial Azure, so the Automation
  account sits in a commercial Azure subscription tied to that tenant
  ([Cloud feature availability](https://learn.microsoft.com/azure/security/fundamentals/feature-availability#microsoft-365-integration)).
- **Watch:** Automation keeps job logs for 30 days at most, so export run evidence if it's
  needed longer.
- **Alternative:** a Logic Apps Recurrence trigger, with HTTP actions under the managed
  identity rather than the Outlook connector, which sends as whoever created the connection.

## Option 2: the report reads on-premises data through Kerberos

Data in on-premises AD, file shares or SQL.

- **The cloud sandbox can't reach the network.** Learn: "The job can only access resources in
  your datacenter if those resources are accessible from the public cloud"
  ([Runbook execution](https://learn.microsoft.com/azure/automation/automation-runbook-execution)).
- **Hybrid Runbook Worker:** the schedule lives in Azure and the job runs on a domain server
  ([Hybrid Runbook Worker overview](https://learn.microsoft.com/azure/automation/automation-hybrid-runbook-worker)).
- **The identity catch:** hybrid jobs run as Local System by default, which on the network is
  the server's computer account. The alternative, Hybrid Worker credentials, needs a credential
  asset with a username and password
  ([Run runbooks on a Hybrid Runbook Worker](https://learn.microsoft.com/azure/automation/automation-hrw-run-runbooks#configure-runbook-permissions)).
  A gMSA can't fill that, because it has no password to store (my inference).
- **Gain:** one central schedule, job history in Azure, and alerting.
- **Loss:** the gMSA, unless the server's computer account gets the read rights instead.

## Option 3: both kinds of data

Keep the Windows scheduled task as the gMSA for the Kerberos reads, and use the Azure Arc
managed identity for Graph and mail. This is the drift-reporter pattern in the workbook's
[Book 10 Appendix B, D.3](https://whalermike.github.io/modernization-workbook/docs/books/b10-cloud-boundary/appendix-b-platform-host-interfaces.html),
and [C2 with M3](https://whalermike.github.io/modernization-workbook/docs/books/guides/service-account-migration.html#sam-c2)
in the migration guide.

## Option 4: a ServiceNow scheduled flow

### Schedule

- A **scheduled trigger** in Flow Designer or Workflow Studio: daily, weekly, monthly, once or
  repeated ([Flow triggers](https://www.servicenow.com/docs/r/washingtondc/build-workflows/flow-triggers.html);
  [Create a saved scheduled trigger](https://www.servicenow.com/docs/r/HGWDpzjgkfvaJWTdMzNy2w/34CBgmHHiwUiPRMFzX0Rlg)).
- It runs in the instance's time zone and may not start at the exact minute, because triggers
  are queued.
- To run on workdays only, a daily trigger whose first step checks the date is the usual
  approach ([community thread](https://www.servicenow.com/community/developer-forum/scheduled-flow-on-workdays/m-p/2161492)).
  A Scheduled Script Execution is the other option.

### Where the work runs

| Report reads | Runs on | Identity |
|---|---|---|
| Entra, Microsoft 365 or Azure (Graph) | The instance, through an outbound REST message or the Microsoft Entra ID spoke | An app registration whose credential is stored in ServiceNow. ServiceNow can't use an Azure managed identity, so a certificate is better than a secret ([migration guide, C3](https://whalermike.github.io/modernization-workbook/docs/books/guides/service-account-migration.html#sam-c3)). In GCC the endpoint is `graph.microsoft.com`. |
| On-premises AD, file shares or SQL | A MID Server script. The MID Server is a Windows service inside the network. | **The gMSA can run the MID Server.** ServiceNow documents gMSA setup, and a Windows credential set to "Use MID Server Service Account" stores no password ([gMSA configuration for Discovery](https://www.servicenow.com/docs/r/xIukoQY2A2qGfsWn8TUt1A/ryjUtR4~sbK0EiOUJWNgcA)). |

### What it gains over a Windows scheduled task

- **Mail without Graph `Mail.Send`.** The instance's own outbound email sends the report, which
  avoids RBAC for Applications.
- **The report becomes a record** with the instance's retention, history and access controls.
- No Azure subscription, Automation account or Arc dependency.
- For on-premises data the gMSA stays, so no password is stored.

### Cautions

- **The gMSA's reach gets wider.** Every job on that MID Server runs as its service account,
  including Discovery and other integrations. A dedicated MID Server, or read-only rights for the
  gMSA, limits that.
- **Community reports, not official guidance:**
    - Error 1069 when starting the service; the reported fix was installing with a normal
      account first, then switching to the gMSA
      ([thread](https://www.servicenow.com/community/itom-forum/starting-midserver-with-gmsa-account-gives-error-1069/m-p/2534577)).
    - The AD v2 spoke may not honour the MID service-account credential
      ([thread](https://www.servicenow.com/community/developer-forum/ad-v2-spoke-authentication-failed-when-using-mid-server-service/m-p/3604031)).
    - ServiceNow's pages disagree on whether the gMSA must be a local administrator
      ([Install a MID Server on Windows](https://www.servicenow.com/docs/r/GCPjp~ldPTNRN99oH1DYFg/1QSEzO0T4JFObpamBnxtzw)).
- **Licensing:** IntegrationHub spokes can need a separate subscription. REST messages, Flow
  Designer and MID Server scripts come with the instance (the workbook's
  [Book 15 Ch13](https://whalermike.github.io/modernization-workbook/docs/books/b15-day2-operations/13-building-day-two-automation-in-house.html)
  makes the same point).
- **Credential in the instance:** Graph reads need an app registration credential stored in
  ServiceNow, held in a connection alias with read-only Graph permissions.
- **Not yet researched:** what ServiceNow's government offerings include.

## Not an option: Microsoft 365 Copilot

Scheduled prompts aren't available in GCC, so a Copilot agent can't run on a timer there.

## Comparison

| Option | Schedule | Identity for on-premises data | Mail | Output |
|---|---|---|---|---|
| Windows task as the gMSA | Task Scheduler on one server | gMSA | Graph `Mail.Send` or an on-premises relay | A mail and files on the server |
| Azure Automation (cloud or hybrid) | Azure schedule | Hybrid worker as the computer account or a stored credential; not a gMSA | Graph `Mail.Send` | Job history for 30 days |
| gMSA task plus Arc managed identity | Task Scheduler | gMSA | Graph `Mail.Send` under the Arc identity | A mail and files on the server |
| ServiceNow scheduled flow plus MID Server | Instance scheduled trigger | gMSA as the MID Server service account | Instance email | A ServiceNow record |

| Report reads | Fits best |
|---|---|
| Only Entra, Microsoft 365 or Azure data | Azure Automation with a managed identity (no stored credential), or ServiceNow (no mail scoping) |
| On-premises data | The gMSA task, or ServiceNow with the gMSA on the MID Server |
| Both | The gMSA task plus Arc managed identity, or ServiceNow with the MID Server and an app registration certificate |

**Cost:** Azure Automation bills per minute of job run time, so a daily report costs little.
ServiceNow costs depend on the instance subscription and any IntegrationHub licensing.
