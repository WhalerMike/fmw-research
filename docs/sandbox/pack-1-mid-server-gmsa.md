# Pack 1: MID Server running as a gMSA

!!! info "Research notes, not workbook guidance"
    **Status:** Open · **Last checked:** 2026-11-12 · Steps are drafts until a sandbox run confirms them.

**Question:** can the MID Server's Windows service run as a group managed service account
(gMSA), and does the gMSA need to be a local administrator?

**Why it matters:** ServiceNow's own page contradicts itself. Its prerequisites say to add the
gMSA to the MID Server host's local Administrators group; its benefits section says the gMSA
does not need to be in that group
([gMSA configuration for Discovery](https://www.servicenow.com/docs/r/xIukoQY2A2qGfsWn8TUt1A/ryjUtR4~sbK0EiOUJWNgcA)).
A community thread reports error 1069 when starting the service as a gMSA
([thread](https://www.servicenow.com/community/itom-forum/starting-midserver-with-gmsa-account-gives-error-1069/m-p/2534577)).

## You need

- A sandbox instance and a user with the `admin` or `mid_server` role.
- A domain-joined Windows Server for the MID Server, `<mid-host>`, with the Active Directory
  PowerShell module (RSAT) installed.
- Rights to create a gMSA in the domain.

## Steps

### 1. Create the gMSA (domain controller or admin workstation)

Check for a KDS root key. If the command returns nothing, create one and wait for replication
before step 2 (see
[Getting started with gMSAs](https://learn.microsoft.com/windows-server/identity/ad-ds/manage/group-managed-service-accounts/group-managed-service-accounts/getting-started-with-group-managed-service-accounts)).

```powershell
Get-KdsRootKey
```

```powershell
Add-KdsRootKey -EffectiveImmediately
```

Create the gMSA and allow only the MID host to retrieve its password:

```powershell
New-ADServiceAccount -Name gmsa-midrpt -DNSHostName gmsa-midrpt.<domain-fqdn> -PrincipalsAllowedToRetrieveManagedPassword "<mid-host>$"
```

### 2. Install and test the gMSA on the MID host

```powershell
Install-ADServiceAccount -Identity gmsa-midrpt
```

```powershell
Test-ADServiceAccount -Identity gmsa-midrpt
```

**Expected:** `True`.

### 3. Install the MID Server with a normal account first

The community fix for error 1069 was to install with an ordinary account, then switch the
service to the gMSA.

1. In the instance, go to **MID Server > Downloads** and download the Windows installer that
   matches `<mid-host>`.
2. Install it with the installer's defaults, naming the MID Server `<mid-server-name>` and
   letting the service run as Local System for now
   ([Install a MID Server on Windows](https://www.servicenow.com/docs/r/GCPjp~ldPTNRN99oH1DYFg/1QSEzO0T4JFObpamBnxtzw)).
3. In the instance, go to **MID Server > Servers**, open `<mid-server-name>`, and select
   **Validate**. Wait for status **Up** and validated **Yes**.

Find the service name (normally `snc_mid_<mid-server-name>`):

```powershell
Get-Service snc_mid_* | Select-Object Name, DisplayName, Status
```

### 4. Switch the service to the gMSA, without local admin

```powershell
sc.exe config "snc_mid_<mid-server-name>" obj= "<DOMAIN>\gmsa-midrpt$" password= ""
```

```powershell
Restart-Service "snc_mid_<mid-server-name>"
```

```powershell
Get-CimInstance Win32_Service -Filter "Name='snc_mid_<mid-server-name>'" | Select-Object Name, StartName, State
```

**Expected:** `StartName` is `<DOMAIN>\gmsa-midrpt$` and `State` is `Running`.

**If the service fails with error 1069** (logon failure), the gMSA probably lacks the "Log on as
a service" right. Open `services.msc`, open the MID Server service, select the **Log On** tab,
choose **This account**, enter `<DOMAIN>\gmsa-midrpt$` with both password boxes empty, and
select **OK**. The console grants the right. Then restart the service with the command above.

### 5. Check the MID Server is healthy without local admin

```powershell
Get-Content "<install-folder>\agent\logs\agent0.log.0" -Tail 50
```

In the instance, check **MID Server > Servers** shows `<mid-server-name>` as **Up**. Run
**Validate** again.

Check folder rights: the gMSA needs to write to the install folder (logs, work files).

```powershell
icacls "<install-folder>"
```

If it can't write, grant modify rights to the install folder only:

```powershell
icacls "<install-folder>" /grant "<DOMAIN>\gmsa-midrpt$:(OI)(CI)M"
```

### 6. Only if step 5 fails: add local admin and retest

```powershell
Add-LocalGroupMember -Group Administrators -Member "<DOMAIN>\gmsa-midrpt$"
```

```powershell
Restart-Service "snc_mid_<mid-server-name>"
```

Repeat step 5, then record which one worked.

## Pass criteria

| Check | Pass |
|---|---|
| `Test-ADServiceAccount` | `True` |
| Service `StartName` | The gMSA |
| MID Server status in the instance | Up and validated |
| Local admin needed | Recorded as yes or no, with the release name |

## Copilot prompt (for use at work)

> I ran a test to run a ServiceNow MID Server service as a group managed service account. Here
> are my notes and the command output: [paste]. Fill in the results template: what passed,
> what failed, any error codes, whether local administrator rights were needed, and the
> ServiceNow release. Then write a one-paragraph generic finding with no server names,
> account names, domain names or instance names.

## What to bring back here

One generic sentence for the log, for example: "MID Server ran as a gMSA on release X without
local admin; install folder needed modify rights." No names or output.
