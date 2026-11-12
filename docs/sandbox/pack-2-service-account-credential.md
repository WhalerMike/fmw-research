# Pack 2: Using the service account for on-premises reads

!!! info "Research notes, not workbook guidance"
    **Status:** Open · **Last checked:** 2026-11-12 · Steps are drafts until a sandbox run confirms them.

**Question:** when the MID Server runs as the gMSA (pack 1), do jobs it runs read Active
Directory as the gMSA, with no password stored in the instance? And does the AD v2 spoke work
the same way?

**Background:**

- ServiceNow documents a Windows credential option to use the MID Server service account
  ([gMSA configuration for Discovery](https://www.servicenow.com/docs/r/xIukoQY2A2qGfsWn8TUt1A/ryjUtR4~sbK0EiOUJWNgcA)).
- For PowerShell, the MID Server tries the Windows credentials in the instance first. If none
  work, it falls back to the service account. When the target is the MID Server's own host, it
  skips the stored credentials and uses the service account
  ([MID Server PowerShell files](https://www.servicenow.com/docs/r/hBTzZEiPu2xbUS8_SIbkhA/mwla_EMTolcbxxZYuB46yQ)).
- Community reports say the AD v2 spoke may not honour the service-account credential
  ([thread](https://www.servicenow.com/community/developer-forum/ad-v2-spoke-authentication-failed-when-using-mid-server-service/m-p/3604031)),
  and that a gMSA "Service Account" credential did not work with one other integration
  ([thread](https://www.servicenow.com/community/itom-forum/getting-adme-to-work-with-mid-server-service-account-credentials/td-p/3025047)).

## You need

- Pack 1 passed: `<mid-server-name>` is Up and running as the gMSA.
- A test AD user `<test-user>` to read.
- The `admin` role in the sandbox, for background scripts.

## Steps

### 1. Give the gMSA read-only rights

Authenticated users can read most AD attributes by default. Don't add the gMSA to any
privileged group. Confirm its memberships:

```powershell
Get-ADServiceAccount -Identity gmsa-midrpt -Properties MemberOf | Select-Object -ExpandProperty MemberOf
```

**Expected:** empty, or only groups you added on purpose (record them).

### 2. Run a script on the MID Server and see which account it runs as

In the instance, go to **System Definition > Scripts - Background**, paste this, replace the
two placeholders, and select **Run script**. It sends a JavaScript probe to the MID Server,
which starts PowerShell under the service's own account.

```javascript
var ps = "whoami; ([adsisearcher]'(sAMAccountName=<test-user>)').FindOne().Path";
var js = "var cmd = probe.getParameter('ps');" +
  "var pb = new Packages.java.lang.ProcessBuilder('powershell.exe','-NoProfile','-NonInteractive','-Command', cmd);" +
  "pb.redirectErrorStream(true); var p = pb.start();" +
  "var r = new Packages.java.io.BufferedReader(new Packages.java.io.InputStreamReader(p.getInputStream()));" +
  "var out = ''; var line; while ((line = r.readLine()) != null) { out += line + '\\n'; }" +
  "p.waitFor(); out;";
var probe = new JavascriptProbe('<mid-server-name>');
probe.setName('FMW sandbox pack 2: whoami');
probe.addParameter('ps', ps);
probe.setJavascript(js);
gs.info('Probe sent: ' + probe.create());
```

Wait one minute. Then open the result: go to **ECC > Queue**, filter **Queue** is `input` and
**Name** is `FMW sandbox pack 2: whoami`, and open the newest record. Read its **Payload**.

**Expected:** the first line is `<domain>\gmsa-midrpt$`; the second is the LDAP path of
`<test-user>`.

If the payload shows an error about `Packages` being blocked, your release restricts Java
access from probes. Record that, and try the IntegrationHub **PowerShell** step instead (it
may need an IntegrationHub subscription).

### 3. Create the Windows credential that uses the service account

1. Go to **Discovery > Credentials** (or **Connections & Credentials > Credentials**), select
   **New**, then **Windows Credentials**.
2. Name it `fmw-sandbox-mid-service-account`.
3. Select the option to use the MID Server service account. ServiceNow's page names it "Use MID
   Server Service Account". Leave user name and password empty.
4. Under **MID servers**, limit it to `<mid-server-name>`.
5. Save, then use the **Test credential** related link against `<mid-host>`.

**Expected:** the test succeeds and the record stores no password.

### 4. Only if the AD v2 spoke is licensed: test it

1. Create a connection and credential alias for the AD v2 spoke, using the credential from
   step 3 and `<mid-server-name>`.
2. In **Workflow Studio** (or **Flow Designer**), create a test action with the spoke's
   **Lookup User** (or similar read-only) step for `<test-user>`.
3. Run the test.

**Record:** whether it succeeds, and the exact error if not.

### 5. Clean up

Delete the background-script ECC records you no longer need, and keep the credential for
pack 5 only if it passed.

## Pass criteria

| Check | Pass |
|---|---|
| Probe `whoami` | The gMSA |
| AD read from the probe | Returns the test user's LDAP path |
| Windows credential | Tests successfully with no stored password |
| AD v2 spoke | Recorded as works, fails (with error) or not licensed |

## Copilot prompt (for use at work)

> I tested whether ServiceNow MID Server jobs run as the MID Server's gMSA service account.
> Here are the ECC queue payloads and credential test results: [paste]. Fill in the results
> template. Say whether the probe ran as the gMSA, whether the AD read worked, whether the
> service-account credential tested successfully, and what happened with the AD v2 spoke.
> Then write a one-paragraph generic finding with no names of servers, accounts, domains or
> instances.

## What to bring back here

One generic sentence, for example: "Probes ran as the gMSA and read AD on release X; the AD v2
spoke did not accept the service-account credential."
