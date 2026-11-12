# What is a MID Server?

!!! info "Research notes, not workbook guidance"
    **Status:** Findings · **Last checked:** 2026-11-12 · Explainer for the
    [ServiceNow sandbox test packs](index.md).

ServiceNow runs in the cloud, outside your network. On its own it can't reach anything inside:
Active Directory, file shares, SQL databases or Windows servers. A **MID Server**
(Management, Instrumentation and Discovery Server) is ServiceNow's helper program that you
install on a server **inside** your network to close that gap.

Think of it as ServiceNow's agent on the inside.

## How it works

1. **It phones home.** The MID Server connects **out** to your ServiceNow instance over HTTPS
   and asks whether there is work for it. The instance never connects in, so no inbound
   firewall opening is needed.
2. **It takes jobs.** The instance hands it tasks: run a PowerShell command, read Active
   Directory over LDAP, query a database over JDBC, scan servers (Discovery), or run a script
   (a JavaScript probe).
3. **It does the work locally and reports back.** It runs the job inside your network and posts
   the result to the instance.
4. **It works as a Windows account.** It runs as a Windows service. Jobs run under the
   service's own account unless a job uses a credential stored in the instance.

```text
   Your network                                    ServiceNow (cloud)
  +-------------------------------+               +---------------------------+
  |  AD, file shares, SQL, servers|               |  Instance                 |
  |            ^                  |   HTTPS out   |   - schedules, flows      |
  |            | reads            |  ---------->  |   - ECC queue (jobs and   |
  |  MID Server (Windows service, |  <----------  |     results)              |
  |  running as the gMSA)         |  jobs/results |   - records, email        |
  +-------------------------------+               +---------------------------+
```

## The parts you will meet in the packs

| Part | What it is |
|---|---|
| Windows service | Normally named `snc_mid_<mid-server-name>`. Its **Log On** account is the identity jobs run as. |
| Install folder | Holds the program and its logs. The main log is `<install-folder>\agent\logs\agent0.log.0`. |
| **MID Server > Servers** | The list in the instance. A healthy MID Server shows status **Up** and validated **Yes**. |
| ECC queue (`ecc_queue`) | The table jobs and results pass through. An **output** record is a job sent to the MID Server; an **input** record is its result. |
| Windows credentials | Credential records in the instance. For PowerShell, the MID Server tries these first and falls back to the service account; when the target is its own host, it uses the service account directly. |
| "Use MID Server Service Account" | A Windows credential option that tells jobs to use the service's own account, so no password is stored in the instance. |

## Why it can run as a gMSA

A group managed service account (gMSA) is an Active Directory account whose password AD sets
and rotates; only the hosts you allow can use it. Because the MID Server is an ordinary Windows
service, its Log On account can be a gMSA. Then:

- AD manages the password, and ServiceNow stores none;
- every job the MID Server runs with the service account reads as the gMSA;
- the gMSA's rights decide what those jobs can reach, so keep them read-only, or give the
  report its own MID Server.

ServiceNow documents gMSA setup for the MID Server
([gMSA configuration for Discovery](https://www.servicenow.com/docs/r/xIukoQY2A2qGfsWn8TUt1A/ryjUtR4~sbK0EiOUJWNgcA)),
but its own page disagrees on whether the gMSA must be a local administrator. That is what
[pack 1](pack-1-mid-server-gmsa.md) tests.

## Where it fits in the daily report

Today a Windows scheduled task runs the report as the gMSA. In the ServiceNow design:

| Job | Done by |
|---|---|
| Reading on-premises data (AD, shares, SQL) as the gMSA | The MID Server |
| The daily schedule | The instance (scheduled flow or scheduled job) |
| Keeping the report | The instance, as a record |
| Sending the email | The instance's own outbound email |

See [Scheduling a daily report job](../topics/daily-report-scheduling.md) for the full
comparison with the other options.

## Sources

- [Install a MID Server on Windows](https://www.servicenow.com/docs/r/GCPjp~ldPTNRN99oH1DYFg/1QSEzO0T4JFObpamBnxtzw)
- [gMSA configuration for Discovery](https://www.servicenow.com/docs/r/xIukoQY2A2qGfsWn8TUt1A/ryjUtR4~sbK0EiOUJWNgcA)
- [MID Server PowerShell files](https://www.servicenow.com/docs/r/hBTzZEiPu2xbUS8_SIbkhA/mwla_EMTolcbxxZYuB46yQ)
