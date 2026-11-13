# Windows Server 2025 retirements: where Microsoft's sources disagree

!!! info "Research notes, not workbook guidance"
    **Status:** Open · **Last checked:** 2026-11-13 · **Baseline:** Microsoft 365 GCC Moderate

**Question:** when planning for the features Windows Server 2025 removes, deprecates or changes
by default, where do Microsoft's own pages disagree with each other, and how can each point be
settled?

This page lists only the disagreements. It does not decide anything. Each point gives what each
source says, why it matters for planning, a way to settle it (a lab check or a Learn update to
watch for), and the reading used until then. Microsoft Learn is the primary source. Pages on
support.microsoft.com are marked **[KB]**, Microsoft blogs **[Microsoft blog]**, and anything not
from Microsoft **[Non-Microsoft]**. Every page was read on 2026-11-13. Quotes are short and exact.

The lab checks are written for an isolated test domain with at least one Windows Server 2025
domain controller. Run them as a domain administrator in an elevated PowerShell session.
Names such as `contoso.test` are placeholders.

The finished guidance on these platform changes lives in the
[Federal Modernization Workbook](https://whalermike.github.io/modernization-workbook/). Nothing
here changes it.

## Summary

| # | Point | Sources in conflict | How to settle |
|---|---|---|---|
| 1 | TLS 1.0 and 1.1 default | Server removed-features page vs Schannel protocol table vs TLS deprecation page | Lab |
| 2 | SMB signing, inbound | SMB hardening page vs SMB signing page and What's new | Lab |
| 3 | KB5073381 RC4 enforcement dates and default value | KB5073381 with itself; KB5073381 vs AskDS blog | Lab |
| 4 | Kerberos trust encryption default | Learn troubleshooting article vs a non-Microsoft analysis; KB5073381 FAQ | Lab |
| 5 | Seamless SSO account and AES date | Seamless SSO page vs KB5073381 | Lab (check the account) |
| 6 | dMSA attribute name and switch-over timing | dMSA overview with itself; overview vs FAQ | Lab |
| 7 | IAKerb and Local KDC release status | NTLM roadmap blog vs Learn Q&A | Wait for Microsoft |
| 8 | Smaller points | See the table at the end | Mixed |

## 1. TLS 1.0 and 1.1 on Windows Server 2025

**Question:** are TLS 1.0 and 1.1 off by default on a shipping Windows Server 2025 build?

**What the sources say:**

- *Features removed or no longer developed in Windows Server*: "These versions are disabled by
  default in Windows Server 2025."
  ([Learn](https://learn.microsoft.com/windows-server/get-started/removed-deprecated-features-windows-server),
  read 2026-11-13)
- *Protocols in TLS/SSL (Schannel SSP)*: the protocol table (ms.date 2025-03-20) lists TLS 1.0 and
  1.1, client and server, as **Enabled** on Windows Server 2025.
  ([Learn](https://learn.microsoft.com/windows/win32/secauthn/protocols-in-tls-ssl--schannel-ssp-),
  read 2026-11-13)
- *TLS 1.0 and TLS 1.1 deprecation in Windows*: the change targets 2024 Insider Preview builds and
  "won't impact in-market Operating System versions."
  ([Learn](https://learn.microsoft.com/windows/win32/secauthn/tls-10-11-deprecation-in-windows),
  read 2026-11-13)

**Why it matters:** applications and appliances that only speak TLS 1.0 or 1.1 (for example
unpatched SQL Server 2012 to 2016) either keep working or fail after a move to Windows Server 2025.
That decides whether the move needs an inventory and remediation step first.

**How to settle it (lab):** on a freshly installed Windows Server 2025 member server, with no
hardening baseline applied:

```powershell
# 1. Look for explicit Schannel protocol keys (none on a clean install means the built-in default applies)
$p = 'HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols'
Get-ChildItem $p -Recurse -ErrorAction SilentlyContinue |
    ForEach-Object { Get-ItemProperty $_.PSPath } |
    Select-Object PSChildName, Enabled, DisabledByDefault

# 2. Test the real behaviour: install IIS, bind a self-signed HTTPS certificate, then try TLS 1.0
Install-WindowsFeature Web-Server -IncludeManagementTools
$cert = New-SelfSignedCertificate -DnsName $env:COMPUTERNAME -CertStoreLocation Cert:\LocalMachine\My
New-WebBinding -Name 'Default Web Site' -Protocol https -Port 443
(Get-WebBinding -Name 'Default Web Site' -Protocol https).AddSslCertificate($cert.Thumbprint, 'My')
```

Then, from a Windows PowerShell 5.1 session on any test machine:

```powershell
[Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls      # TLS 1.0 only
Invoke-WebRequest "https://<ws2025-server>/" -UseBasicParsing | Select-Object StatusCode
```

A failed handshake means TLS 1.0 is off on the server. Repeat with `Tls11`. Schannel event
**36871** in the System log also shows refused handshakes.

**Current working reading:** treat TLS 1.0 and 1.1 as possibly off on Windows Server 2025, and
inventory TLS 1.0 and 1.1 dependencies before the move. Don't state either default as fact until the
lab result is in.

## 2. SMB signing on Windows Server 2025: inbound and outbound, or outbound only

**Question:** does a Windows Server 2025 member server require signing on inbound SMB connections
by default, or only on outbound ones?

**What the sources say:**

- *SMB security hardening*: "all outbound and inbound SMB connections are now required to be
  signed by default."
  ([Learn](https://learn.microsoft.com/windows-server/storage/file-server/smb-security-hardening),
  read 2026-11-13)
- *Control SMB signing behavior*: "Windows Server 2025 requires outbound SMB signing only."
  ([Learn](https://learn.microsoft.com/windows-server/storage/file-server/smb-signing),
  read 2026-11-13)
- *What's new in Windows Server 2025*: signing is required by default for all outbound SMB
  connections; inbound isn't mentioned.
  ([Learn](https://learn.microsoft.com/windows-server/get-started/whats-new-windows-server-2025),
  read 2026-11-13)

Domain controllers have required inbound signing for years, so the disagreement only matters for
member servers. Windows 11 24H2 Enterprise, Pro and Education require both directions.

**Why it matters:** if inbound signing is required, scanners, NAS devices and older clients that
write to a Windows Server 2025 file server without signing will fail with `STATUS_INVALID_SIGNATURE`
(0xc000a000). If it's outbound only, the risk is limited to the server connecting out to
third-party SMB servers.

**How to settle it (lab):** on a clean Windows Server 2025 member server, and on a Windows Server
2025 domain controller for comparison, before any GPO applies:

```powershell
Get-SmbServerConfiguration | Select-Object RequireSecuritySignature, EnableSecuritySignature
Get-SmbClientConfiguration | Select-Object RequireSecuritySignature, EnableSecuritySignature
gpresult /r /scope computer
```

`RequireSecuritySignature : True` on the server side of the member server supports the hardening
page. `False` supports the other two pages. To see who would break before changing anything, turn
on the audit settings:

```powershell
Set-SmbServerConfiguration -AuditClientDoesNotSupportSigning $true -Force
Set-SmbClientConfiguration -AuditServerDoesNotSupportSigning $true -Force
```

Events **3021** (SMBServer\Audit) and **31998** (SMBClient\Audit) then list the peers that don't sign.

**Current working reading:** outbound only on member servers (two of three pages), inbound on
domain controllers as before. Run the audit settings anyway.

## 3. KB5073381: when RC4 enforcement starts, and what the default value is

**Question:** which monthly update turns on the Kerberos RC4 change for CVE-2026-20833, and what
value does a domain controller assume when `DefaultDomainSupportedEncTypes` isn't set?

**What the sources say:**

- **[KB]** KB5073381, Take Action section: enforcement is "automatically enabled by installing
  Windows Updates released on or after April 2026".
  ([support.microsoft.com](https://support.microsoft.com/kb/5073381), read 2026-11-13)
- **[KB]** KB5073381, a Note in the same article: updates "on or after July 2026" enable it
  programmatically. The timeline table gives April 14, 2026 as enforcement with manual rollback
  through `RC4DefaultDisablementPhase`, and July 2026 (month only) as the end of that rollback.
- **[KB]** KB5073381: from April 14, 2026 the default becomes AES-SHA1 only, **0x18**.
- **[Microsoft blog]** AskDS, *What is going on with RC4 in Kerberos?* (updated June 10, 2026):
  gives Windows Server 2025's default `DefaultDomainSupportedEncTypes` as **0x24**.
  ([Tech Community](https://techcommunity.microsoft.com/blog/askds/what-is-going-on-with-rc4-in-kerberos/4489365),
  read 2026-11-13)
- *Detect and remediate RC4 usage in Kerberos*: RC4 stops being the assumed default "by the end of
  the second quarter of 2026."
  ([Learn](https://learn.microsoft.com/windows-server/security/kerberos/detect-remediate-rc4-kerberos),
  read 2026-11-13)

**Why it matters:** service accounts with no AES keys, RC4-only clients and RC4-only keytabs fail
once enforcement is on. A plan needs to know whether a rollback is still available, and 0x18 and
0x24 behave differently: 0x24 still allows RC4 tickets.

Both dates have now passed. The question left is what a domain controller at the current update
level actually does.

**How to settle it (lab):** on a Windows Server 2025 domain controller at the current monthly
update:

```powershell
# Explicit settings (absent = built-in default)
Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Services\Kdc' -Name DefaultDomainSupportedEncTypes -ErrorAction SilentlyContinue
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Kerberos\Parameters' -Name RC4DefaultDisablementPhase -ErrorAction SilentlyContinue

# KDC audit and block events 201-209 from KB5073381
Get-WinEvent -FilterHashtable @{ LogName = 'System'; Id = 201..209 } -MaxEvents 50 -ErrorAction SilentlyContinue |
    Where-Object ProviderName -match 'Kdc|Kerberos-Key-Distribution' |
    Select-Object TimeCreated, Id, LevelDisplayName, Message
```

Not yet run against a domain: KB5073381 names the event source "Kdcsvc," and the
provider-name filter above matches either form. Confirm the provider name on the first
event you see and tighten the filter.

Then test the effective default with a service account that has an SPN and no
`msDS-SupportedEncryptionTypes`. Run it from a domain-joined Windows Server 2025 test machine:

```powershell
New-ADUser -Name svc-etype-test -AccountPassword (Read-Host -AsSecureString 'Test password') -Enabled $true
setspn -S HTTP/etypetest.contoso.test CONTOSO\svc-etype-test
klist purge
klist get HTTP/etypetest.contoso.test
```

In the `klist` output, `KerbTicket Encryption Type` and `Session Key Type` show AES256 under 0x18.
Then set the account to RC4 only (`Set-ADUser svc-etype-test -KerberosEncryptionType RC4`), purge,
and request again: a refusal with KDC event 203 or 204 is what enforcement looks like. Remove the
test account afterwards.

**Current working reading:** April 2026 turned enforcement on with a rollback, and July 2026
removed the rollback. On a current domain controller, 0x18 is the assumed default. The AskDS
0x24 figure probably describes the default before April, but Microsoft hasn't said so.

## 4. Kerberos trust encryption defaults

**Question:** does a trust with no encryption type set still default to RC4 for referral
tickets, and does the 2026 RC4 change touch trusts at all?

**What the sources say:**

- *Kerberos Unsupported etype error* (KB 4492348, ms.date 2026-02-12): "By default, the trust
  supports RC4 encryption but not AES128 or AES256".
  ([Learn](https://learn.microsoft.com/troubleshoot/windows-server/windows-security/unsupported-etype-error-accessing-trusted-domain),
  read 2026-11-13)
- **[Non-Microsoft]** An analysis on rickardnobel.se says that since the November 2022 update a
  blank trust value is read as AES, and the referral ticket comes back AES.
  ([rickardnobel.se](https://rickardnobel.se/ad-trust-the-other-domain-supports-kerberos-aes-explained/),
  read 2026-11-13)
- **[KB]** KB5073381 FAQ Q1: the 2026 change affects only Windows domain controllers, and referral
  flows with other Windows or third-party KDCs are unaffected.
  ([support.microsoft.com](https://support.microsoft.com/kb/5073381), read 2026-11-13)
- A Microsoft statement that trusts now default to AES: not found. Whether a Windows Server 2025
  KDC, which no longer issues RC4 TGTs, can build an RC4 referral over an RC4-only trust: not yet
  specified.

**Why it matters:** if referrals still fall back to RC4, AES-only clients fail across the trust
with KDC event 14 (`KDC_ERR_ETYPE_NOSUPP`), or quietly fall back to NTLM.

**How to settle it (lab):** in a test forest with a trust to a second test domain, from the
trusting side:

```powershell
# What the trust object says (empty = not set)
Get-ADObject -Filter 'objectClass -eq "trustedDomain"' -Properties 'msDS-SupportedEncryptionTypes' |
    Select-Object Name, 'msDS-SupportedEncryptionTypes'
ksetup /getenctypeattr other.contoso.test

# What a referral actually uses
klist purge
klist get krbtgt/OTHER.CONTOSO.TEST
```

Read the `KerbTicket Encryption Type` on the referral ticket. Run it once with the trust value
empty and once with AES set
(`ksetup /setenctypeattr other.contoso.test AES128-CTS-HMAC-SHA1-96 AES256-CTS-HMAC-SHA1-96`, on
both sides). Repeat with a Windows Server 2025 domain controller on one side.

**Current working reading:** set the trust encryption type explicitly to AES on both sides, and
don't rely on either default. Treat RC4-only trusts to or from Windows Server 2025 domain
controllers as a test item.

## 5. Seamless SSO computer account (AZUREADSSOACC): which date

**Question:** when does the default encryption type that affects the Seamless SSO computer
account move from RC4 to AES?

**What the sources say:**

- *Microsoft Entra Seamless single sign-on: how it works* (updated 2026-06-01): "Starting with the
  July 2026 Windows Server update", the AD DS default changes from RC4 to AES-256.
  ([Learn](https://learn.microsoft.com/entra/identity/hybrid/connect/how-to-connect-sso-how-it-works),
  read 2026-11-13)
- **[KB]** KB5073381: the default changed to AES-SHA1 **0x18** (AES128 and AES256) with the
  **April 14, 2026** updates, and the rollback ended in July 2026.
  ([support.microsoft.com](https://support.microsoft.com/kb/5073381), read 2026-11-13)

**Why it matters:** if the account still uses RC4 when the domain controllers enforce AES, Seamless
SSO stops working. The Learn page says to roll over the Kerberos decryption key first and then
change the encryption type, otherwise SSO breaks.

**How to settle it (lab):** both dates have passed, so the useful check is the account itself, in
each forest that uses Seamless SSO:

```powershell
Get-ADComputer AZUREADSSOACC -Properties 'msDS-SupportedEncryptionTypes', PasswordLastSet |
    Select-Object Name, 'msDS-SupportedEncryptionTypes', PasswordLastSet
```

A value of 24 (0x18) or 16 (0x10) means AES only. Empty or a value that includes 4 means RC4 may
still be in use. The key rollover is `Update-AzureADSSOForest -OnPremCredentials $creds` from the
Entra Connect server, as the Seamless SSO page describes. A Hybrid Identity Administrator runs it.

**Current working reading:** treat April 2026 as the date that mattered, as in KB5073381. The July
date on the Seamless SSO page matches the end of rollback, not the start of enforcement.

## 6. dMSA: attribute name, and when the service switches to the dMSA

**Question 6a:** which attribute on the old service account records the migration state?

- *Delegated Managed Service Accounts overview*: the Start step sets `msDS-SupersededAccountState`
  to 1. The Complete step on the same page sets `msDS-SupersededServiceAccountState` to 2.
  ([Learn](https://learn.microsoft.com/windows-server/identity/ad-ds/manage/delegated-managed-service-accounts/delegated-managed-service-accounts-overview),
  read 2026-11-13)

**Question 6b:** when does the service start using the dMSA?

- *dMSA FAQ*: the service uses the dMSA "only after the migration process is complete".
  ([Learn](https://learn.microsoft.com/windows-server/identity/ad-ds/manage/delegated-managed-service-accounts/delegated-managed-service-accounts-faq),
  read 2026-11-13)
- *dMSA overview*: during Start, each logon by the old account "refreshes the TGT" and adds the
  host to the dMSA's allowed list.

The two may describe different things: the FAQ the switch of the service's credential, and the
overview the dMSA learning which devices use it. Neither page says so.

**Why it matters:** scripts and monitoring that read the wrong attribute name return nothing. The
switch-over time decides when to watch for failures, and Learn recommends keeping a service in Start
for four ticket lifetimes (28 days).

**How to settle it (lab):** on a test domain with a Windows Server 2025 domain controller and KDS
root key:

```powershell
# Which names exist in the schema
Get-ADObject -SearchBase (Get-ADRootDSE).schemaNamingContext -LDAPFilter '(lDAPDisplayName=msDS-Superseded*)' -Properties lDAPDisplayName |
    Select-Object lDAPDisplayName

# After Start-ADServiceAccountMigration, and again after Complete-ADServiceAccountMigration
Get-ADUser svc-legacy-test -Properties * | Select-Object Name, Enabled, 'msDS-Superseded*'
Get-ADServiceAccount dmsa-test -Properties * | Select-Object Name, 'msDS-DelegatedMSAState', 'msDS-ManagedAccountPrecededByLink'
```

For the switch-over, enable the Security-Kerberos Operational log on the service host and watch for
events **307** (migration), **308** (permission add) and **309** (key fetch) during Start and after
Complete:

```powershell
wevtutil sl Microsoft-Windows-Security-Kerberos/Operational /e:true
Get-WinEvent -LogName Microsoft-Windows-Security-Kerberos/Operational -MaxEvents 50 |
    Where-Object Id -in 307, 308, 309 | Select-Object TimeCreated, Id, Message
```

Event 309 appears only once the host fetches dMSA keys.

**Current working reading:** read both attribute names until the schema check is done. Expect the
service credential to switch at Complete, with device learning during Start.

## 7. IAKerb and Local KDC: released or not

**Question:** are IAKerb and Local KDC, phase 2 of Microsoft's plan to turn NTLM off by default,
generally available for Windows Server 2025?

**What the sources say:**

- **[Microsoft blog]** *Advancing Windows security: disabling NTLM by default* (January 29, 2026,
  updated October 22, 2026): IAKerb and Local KDC are planned for the "second half of 2026", in
  pre-release.
  ([Tech Community](https://techcommunity.microsoft.com/blog/windows-itpro-blog/advancing-windows-security-disabling-ntlm-by-default/4489526),
  read 2026-11-13)
- A Microsoft Learn Q&A answer says the Local KDC service may appear on Windows Server 2025 but "is
  currently not in General Availability".
- **[Non-Microsoft]** Press reports describe both in Insider Canary preview from June 2026
  ([petri.com](https://petri.com/windows-11-iakerb-localkdc-reduce-ntlm/), read 2026-11-13).
- A general availability announcement: not found.

**Why it matters:** IAKerb and Local KDC are what remove NTLM from cases Kerberos can't reach today
(local accounts, no line of sight to a domain controller). An NTLM reduction plan can't count on
them until they're released.

**How to settle it:** wait for Microsoft. Watch the roadmap blog and the Windows Server 2025
What's new page for a release statement. A service on a test server isn't proof of support.

**Current working reading:** not released. Plan NTLM reduction with the tools available now:
enhanced NTLM auditing and Kerberos-first configuration.

## 8. Smaller points

| Point | What the sources say (all read 2026-11-13) | Current working reading |
|---|---|---|
| **WSUS driver sync end date** | The April 18, 2025 removal date appears widely. **[Microsoft blog]** April 7, 2025: "we are postponing the plan to remove WSUS driver synchronization" and promises a revised timeline ([Tech Community](https://techcommunity.microsoft.com/blog/windows-itpro-blog/continuing-wsus-support-for-driver-synchronization/4401042)). No new date found. | Driver sync continues. No end date. Watch the WSUS blog. |
| **KB5066470 NTLMv1 audit start** | **[KB]** KB5066470 says auditing on Windows 11 24H2 clients starts "late August 2025" in one place and September 2025 in its rollout section ([support.microsoft.com](https://support.microsoft.com/help/5066470)). | Cite as August to September 2025. The October 2026 enforcement date isn't affected. |
| **WMIC removal on Windows Server 2025** | *Features removed or no longer developed in Windows Server*: WMIC is a Feature on Demand that "will be removed from Windows in a future release" ([Learn](https://learn.microsoft.com/windows-server/get-started/removed-deprecated-features-windows-server)). *Features removed in Windows client*: removed from Windows 11 24H2 and later in August 2026 ([Learn](https://learn.microsoft.com/windows/whats-new/removed-features)). No Server date. | Server removal not yet specified. Lab check: `Get-WindowsCapability -Online | Where-Object Name -like '*WMIC*'` (the capability name isn't on Learn; this lists any match). Move scripts to `Get-CimInstance` anyway. |
| **When Windows Kerberos got AES keys** | *Detect and remediate RC4 usage in Kerberos* says AES-SHA1 support "was added in Windows Server 2003", and on the same page calls 2003 the last version without it ([Learn](https://learn.microsoft.com/windows-server/security/kerberos/detect-remediate-rc4-kerberos)). **[Microsoft blog]** *Beyond RC4 for Windows authentication* says 2008 ([Windows Server blog](https://www.microsoft.com/en-us/windows-server/blog/2025/12/03/beyond-rc4-for-windows-authentication)). | Windows Server 2008. Treat any password last set before the domain had 2008 domain controllers as lacking AES keys, and check with `List-AccountKeys.ps1` from [microsoft/Kerberos-Crypto](https://github.com/microsoft/Kerberos-Crypto) or KDC events 202 and 207. |
| **AES-SHA256 and AES-SHA384 Kerberos types** | *Detect and remediate RC4 usage in Kerberos* shows sample `List-AccountKeys.ps1` output with keys such as AES128-SHA256. No Microsoft page found says these types are used for tickets. **[Non-Microsoft]** strongwind1.github.io says they were "not yet active" as of April 2026. | Unconfirmed. Don't plan on them. Lab check: `klist` ticket encryption types on a Windows Server 2025 domain. |
| **Cloud Sync agent on Windows Server 2025** | *Microsoft Entra Cloud Sync prerequisites* (ms.date 2026-10-22) lists Windows Server 2016 to 2025 for the agent host, but its group provisioning section still lists 2016 to 2022 only ([Learn](https://learn.microsoft.com/entra/identity/hybrid/cloud-sync/how-to-prerequisites)). | Supported on 2025 for user sync. Group provisioning on 2025 is unconfirmed: test it, or watch for a page update. |
| **Stale AD advice on the Windows Server 2025 What's new page** | *What's new in Windows Server 2025* still recommends planning to upgrade AD and AD LDS servers to Windows Server 2022 ([Learn](https://learn.microsoft.com/windows-server/get-started/whats-new-windows-server-2025)). The rest of the page targets 2025. | Leftover text from an earlier release. Don't quote it. |

## Sources

All read 2026-11-13. The full list is on the [Sources](../sources.md#windows-server-2025-retirements)
page.
