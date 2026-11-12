# Microsoft 365 Copilot compared with AI agents

!!! info "Research notes, not workbook guidance"
    **Status:** Findings · **Last checked:** 2026-11-12 · **Baseline:** Microsoft 365 GCC Moderate

**Question:** in a GCC Moderate tenant that already has Microsoft 365 Copilot, what does Copilot
cover, and when would a separate AI agent be needed?

**Short answer:** Microsoft 365 Copilot with a declarative agent covers most assistance a person
needs around a ticket, under the person's own identity and with no metered charges. What it
can't do is act on each ticket as it arrives with no person involved, or write to ServiceNow.
Writing needs a Copilot Studio agent that a person starts. Acting with no person involved isn't
available in Copilot Studio in GCC.

## Side by side

| | Microsoft 365 Copilot with a declarative agent | Separate agent (Copilot Studio, Foundry, Bot Service) |
|---|---|---|
| Available in GCC | Yes. Declarative agents have full support in GCC ([Declarative agents: national cloud support](https://learn.microsoft.com/microsoft-365/copilot/extensibility/overview-declarative-agent#national-cloud-support)). | Copilot Studio in GCC: yes ([Copilot Studio for US Government](https://learn.microsoft.com/microsoft-copilot-studio/requirements-licensing-gcc)). Foundry: only in Azure Government, where its FedRAMP High, IL4 and IL5 authorizations are listed as "Forecasted". |
| Whose identity it acts as | **The user's own.** Agent Builder agents don't use app registrations or Agent IDs ([Agent identities in Copilot Studio](https://learn.microsoft.com/microsoft-copilot-studio/govern-agents-identities-overview)). | **Its own agent identity.** Copilot Studio creates an Entra Agent ID for each new agent ([Use Entra agent identities](https://learn.microsoft.com/microsoft-copilot-studio/admin-use-entra-agent-identities)). It needs a sponsor, owners, credential rules and monitoring (see the workbook's [Book 17, owners and sponsors](https://whalermike.github.io/modernization-workbook/docs/books/b17-ai-identity/05-owners-sponsors-and-lifecycle.html)). |
| ServiceNow access | **Read and search** through the synced ServiceNow Tickets connector, which lists GCC IP ranges ([ServiceNow Tickets connector troubleshooting](https://learn.microsoft.com/microsoft-365/copilot/connectors/servicenow-tickets-troubleshooting)). An admin must turn it on. | **Read and write** through the ServiceNow Power Platform connector, which is listed for GCC ([Power Automate connectors by region](https://learn.microsoft.com/connectors/connector-reference/connector-reference-powerautomate-connectors)). |
| Runs with no person | **No.** Scheduled prompts aren't available in GCC. | Copilot Studio triggers and autonomous agents are **not available in GCC or GCC High** ([Copilot Studio for US Government](https://learn.microsoft.com/microsoft-copilot-studio/requirements-licensing-gcc)). |
| Cost | Included in the Copilot licence. | Included only when a Copilot-licensed user starts the agent. Otherwise billed in Copilot Credits; see [AI bot costs](ai-bot-costs.md). Power Platform connector licensing is separate. |
| Typical use around a ticket | Drafting a request, summarizing a ticket, searching knowledge and ticket history, drafting a plan for an approver. | Opening or updating tickets. |
| Risk | Low. It can't do anything the user couldn't already do. | Higher. A new non-person identity with write access. |

## Three levels

| Level | What it is | In GCC Moderate |
|---|---|---|
| 1. Microsoft 365 Copilot plus a declarative agent | The person's own identity; reads tickets and knowledge through the ServiceNow Tickets connector. | Available |
| 2. Copilot Studio agent that a person starts | Opens or updates tickets through the ServiceNow connector, under its own agent identity. | Available |
| 3. Agent that acts on each ticket with no person | Copilot Studio triggers and autonomous agents. | **Not available in GCC** |

## Related findings

- **Approval has to be enforced by the runtime.** Microsoft's Foundry guidance says "A
  system-prompt instruction alone doesn't enforce approval"
  ([Enforce tool approval](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/use-toolbox-hosted-agent#enforce-tool-approval)).
- **AI approvals.** Multistage approvals in Copilot Studio agent flows (preview) can let an AI
  stage approve or reject on its own. Learn advises keeping human stages for sensitive
  decisions ([Advanced approvals](https://learn.microsoft.com/microsoft-copilot-studio/flows-advanced-approvals)).
- **Change execution stays deterministic.** Logic Apps and Azure Automation can make changes
  under their own managed identities
  ([Logic Apps managed identity](https://learn.microsoft.com/azure/logic-apps/authenticate-with-managed-identity)).
- In the workbook's [Ticket to Machine](https://whalermike.github.io/modernization-workbook/docs/books/b13-governance/10-ticket-to-machine.html)
  model, the identity that decides and the identity that acts are separate. None of the three
  levels above changes that.

## Naming note

Microsoft describes Microsoft 365 GCC as FedRAMP Moderate, while the Copilot Studio GCC page
lists FedRAMP High. This project says "GCC Moderate" for the tenant and cites each service's own
page for its authorization level.

## Side notes: GCC High and DoD

- Copilot Studio in GCC High: available, without triggers or autonomous agents. DoD is not yet
  specified.
- New Power Platform connectors are off by default in GCC High and DoD
  ([Connectors off by default](https://learn.microsoft.com/power-platform/admin/connector-off-by-default)).
