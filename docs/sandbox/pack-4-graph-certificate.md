# Pack 4: Graph from the instance with a certificate

!!! info "Research notes, not workbook guidance"
    **Status:** Open · **Last checked:** 2026-11-12 · Steps are drafts until a sandbox run confirms them.

**Question:** can the instance call Microsoft Graph using an app registration with a
**certificate**, so no client secret is stored in ServiceNow?

**Background:**

- The usual pattern is an OAuth profile in the instance using the client-credentials grant
  and the scope `https://graph.microsoft.com/.default`, referenced by a REST message
  ([community thread](https://www.servicenow.com/community/architect-forum/ms-graph-oauth-2-0-integration-best-practice-questions-and/m-p/2196850)).
- ServiceNow documents certificate-based client credentials (with a JWT provider) for SMTP
  ([Configure client credential flow for SMTP OAuth2 using certificate-based authentication](https://www.servicenow.com/docs/r/UrSRFFKWBbfQBgoRlt~ltw/gHj53y2BUVud4hBHtVCp9g)).
  Whether the same works for a REST message is the open question.
- A ServiceNow community article describes the OAuth registry and profile pattern with Entra ID
  ([Using Microsoft Entra ID to secure ServiceNow integrations](https://www.servicenow.com/community/developer-blog/using-microsoft-entra-id-to-secure-servicenow-integrations/ba-p/3604333)).
- Community reports show errors when moving from a secret to a certificate, such as
  AADSTS900144, missing `requested_token_use`
  ([thread](https://www.servicenow.com/community/itom-forum/error-aadsts900144-missing-requested-token-use-during-servicenow/m-p/3553549)),
  and AADSTS700027, when the signing certificate isn't registered on the app.
- In a GCC Moderate tenant, the endpoints are the commercial ones: `login.microsoftonline.com`
  and `graph.microsoft.com`.

This pack first proves the Graph call with a short-lived secret (stage A, sandbox only), then
replaces the secret with a certificate (stage B).

## You need

- A test Entra tenant (or a test app in your GCC tenant) and rights to create an app
  registration and grant admin consent.
- The Microsoft Graph PowerShell SDK on an admin workstation.
- The `admin` role in the sandbox.

## Steps

### 1. Create the app registration with one read-only permission

The test call reads the tenant's organization record, so the app gets only
`Organization.Read.All` (application).

```powershell
Connect-MgGraph -Scopes "Application.ReadWrite.All","AppRoleAssignment.ReadWrite.All"
```

```powershell
$app = New-MgApplication -DisplayName "fmw-sandbox-sn-graph-read" -SignInAudience AzureADMyOrg
$sp = New-MgServicePrincipal -AppId $app.AppId
$graph = Get-MgServicePrincipal -Filter "appId eq '00000003-0000-0000-c000-000000000000'"
$role = $graph.AppRoles | Where-Object { $_.Value -eq "Organization.Read.All" -and $_.AllowedMemberTypes -contains "Application" }
New-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $sp.Id -PrincipalId $sp.Id -ResourceId $graph.Id -AppRoleId $role.Id
"Tenant: " + (Get-MgContext).TenantId
"Client ID: " + $app.AppId
```

Record the tenant ID and client ID on work storage.

### 2. Stage A: prove the call with a 7-day secret (sandbox only)

```powershell
$secret = Add-MgApplicationPassword -ApplicationId $app.Id -PasswordCredential @{ DisplayName = "sandbox-stage-a"; EndDateTime = (Get-Date).AddDays(7) }
$secret.SecretText
```

In the instance:

1. Go to **System OAuth > Application Registry**, select **New**, then **Connect to a third
   party OAuth Provider**.
2. Name `fmw-sandbox-graph`; Client ID and Client Secret from above; Default Grant type
   **Client Credentials**; Token URL
   `https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token`.
3. In the **OAuth Entity Scopes** list, add `https://graph.microsoft.com/.default`, and add it
   to the OAuth entity profile. Save.
4. Go to **System Web Services > Outbound > REST Message**, select **New**. Name
   `fmw-sandbox-graph-org`; Endpoint `https://graph.microsoft.com/v1.0/organization`;
   Authentication type **OAuth 2.0**; OAuth profile `fmw-sandbox-graph default_profile`. Save.
5. Open the **Default GET** method, select **Get OAuth Token**, then **Test**.

**Expected:** HTTP status 200 and a body that contains your test tenant's display name.

### 3. Stage B: replace the secret with a certificate

Create a 90-day certificate and register its public key on the app:

```powershell
$cert = New-SelfSignedCertificate -Subject "CN=fmw-sandbox-sn-graph-read" -CertStoreLocation Cert:\CurrentUser\My -KeyExportPolicy Exportable -KeySpec Signature -KeyLength 2048 -NotAfter (Get-Date).AddDays(90)
Update-MgApplication -ApplicationId $app.Id -KeyCredentials @(@{ Type = "AsymmetricX509Cert"; Usage = "Verify"; Key = $cert.RawData })
$pfxPassword = Read-Host -AsSecureString "Password for the PFX file"
Export-PfxCertificate -Cert $cert -FilePath .\fmw-sandbox-sn-graph-read.pfx -Password $pfxPassword
```

If the instance asks for a Java KeyStore, convert the PFX with the `keytool` that ships in the
MID Server's Java folder:

```powershell
& "<install-folder>\agent\jre\bin\keytool.exe" -importkeystore -srckeystore .\fmw-sandbox-sn-graph-read.pfx -srcstoretype pkcs12 -destkeystore .\fmw-sandbox-sn-graph-read.jks -deststoretype jks
```

In the instance, follow ServiceNow's certificate-based client-credentials procedure (linked
above), adapted from SMTP to the REST message:

1. Upload the keystore under **System Definition > Certificates**.
2. Create a **JWT Key** that uses it, and a **JWT Provider** that uses the key. Add claims:
   `aud` = `https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token`, `iss` and `sub`
   = the client ID. Microsoft also needs the certificate thumbprint in the JWT header as `x5t`
   (see [certificate credentials](https://learn.microsoft.com/entra/identity-platform/certificate-credentials)).
3. On `fmw-sandbox-graph`, remove the client secret and select the JWT provider, so the token
   request sends a `client_assertion`.
4. Run the REST message test again.

**Record:** whether it worked; if not, the exact AADSTS error code and what you changed.

### 4. Remove the stage A secret

```powershell
Remove-MgApplicationPassword -ApplicationId $app.Id -KeyId $secret.KeyId
```

Run the REST message test again to show it still works on the certificate alone.

### 5. Clean up when finished

```powershell
Remove-MgApplication -ApplicationId $app.Id
```

Delete the OAuth registry entry, REST message, JWT provider, JWT key and certificate from the
instance, and the local PFX and JKS files.

## Pass criteria

| Check | Pass |
|---|---|
| Stage A Graph call | HTTP 200 |
| Stage B Graph call with the certificate | HTTP 200 |
| After the secret is removed | Still HTTP 200 |
| Permissions on the app | Only `Organization.Read.All` |

## Copilot prompt (for use at work)

> I tested whether a ServiceNow instance can call Microsoft Graph using an Entra app
> registration with a certificate instead of a client secret. Here are my notes, the REST
> message test results and any AADSTS errors: [paste]. Fill in the results template: stage A
> result, stage B result, errors and the fix for each, and whether the call still worked after
> the secret was removed. Then write a one-paragraph generic finding with no tenant IDs,
> client IDs, app names or instance names.

## What to bring back here

One generic sentence, for example: "Release X called Graph with a certificate through a JWT
provider; the x5t header claim was required."
