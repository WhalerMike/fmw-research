# AI bot costs

!!! info "Research notes, not workbook guidance"
    **Status:** Findings · **Last checked:** 2026-11-12 · **Baseline:** Microsoft 365 GCC Moderate

**Question:** what does an AI bot or agent cost?

**Short answer:** there is no single price. Each service in the stack bills separately, so the
cost depends on which pieces a bot uses. Microsoft Learn describes each billing model but does
not print dollar rates. Those are on Microsoft's pricing pages and in the Copilot Studio
Licensing Guide, and government-cloud prices can differ.

## Copilot Studio agents

Copilot Studio agents bill in **Copilot Credits**, per action
([Billing rates and management](https://learn.microsoft.com/microsoft-copilot-studio/requirements-messages-management)).

| What the agent does | Credits |
|---|---|
| Scripted (classic) answer | 1 |
| AI-generated answer | 2 |
| Agent action (a trigger, a tool call, a reasoning step) | 5 |
| Grounding on the organization's Microsoft Graph data | 10 |
| Agent flow actions | 13 per 100 actions |
| Reasoning model | 10 per 1,000 billed tokens, on top of the rates above |

- **Copilot licence exemption.** A user with a Microsoft 365 Copilot licence pays nothing for
  their own conversations with the agent.
- **Agents that start on their own are always billed.** An agent that wakes up because a ticket
  arrived counts as autonomous, and Copilot licences don't cover it.
- **Capacity is bought monthly and doesn't carry over.** If an environment runs out, its agent
  flows are blocked until capacity is added or pay-as-you-go billing to an Azure subscription is
  switched on.
- **Worked example on the Learn page:** an order-processing agent that makes 4 tool calls per
  order costs 20 credits per order. An agent that classifies a ticket and calls 2 to 4 tools
  would cost about the same, plus model tokens if it uses a reasoning model (my estimate).

## Azure AI Foundry Agent Service

There is no separate agent fee ([Foundry Agent Service FAQ](https://learn.microsoft.com/azure/foundry/agents/faq)).
You pay for:

- the model's input and output tokens on each call;
- Code Interpreter, per session (a session lasts one hour);
- File Search, by the amount of vector storage used.

**Azure OpenAI** charges for tokens, either per use or as reserved throughput. Azure Government
has its own quota and reserved-throughput pages.

## The automation that makes the change

- **Logic Apps** bills per action (Consumption plan) or per hosting plan (Standard plan).
- **Azure Automation** bills per minute of job run time.

These charges are the same with or without a bot in front of them.

## Identity and governance

- **Microsoft Entra Agent ID** "is available for all Microsoft Entra customers"
  ([What is the Microsoft Entra Agent ID platform](https://learn.microsoft.com/entra/agent-id/what-is-agent-id-platform)).
- Governance of agents (sponsors, lifecycle workflows, access packages, Conditional Access for
  agents) needs **Microsoft 365 E7**, or **Microsoft Agent 365** plus Entra P1 or E3. Agent 365
  is licensed per user.
- The Agent 365 service description says it passed its FedRAMP High assessment on October 1,
  2026, with final authorization still pending
  ([Microsoft Agent 365 service description](https://learn.microsoft.com/office365/servicedescriptions/microsoft-agent-365/microsoft-agent-365#feature-availability)).

## Azure Bot Service

Learn doesn't state its pricing tiers. Check the Azure pricing page directly.

## What the findings suggest

- A bot is metered on every request it handles; the change it leads to costs no more than it
  does today.
- The main cost driver is an agent that runs on its own for every new ticket, especially with a
  reasoning model. (In GCC, Copilot Studio can't run that way yet; see
  [Microsoft 365 Copilot compared with AI agents](copilot-vs-agents-gcc-moderate.md).)
- An agent that uses fixed rules or scripted answers for common requests, and the model only for
  unclear ones, stays at a few credits per request.
