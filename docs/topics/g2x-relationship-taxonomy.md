# B2B, B2C and G2x: the relationship names, and whether they separate levels of government

!!! info "Research notes, not workbook guidance"
    **Status:** Integrated · **Last checked:** 2026-11-25 · **Baseline:** Microsoft 365 GCC Moderate

**Question:** do the e-business names B2B and B2C have a government counterpart, and do any of
those names separate federal, state and local government (F2S, F2L and so on)? If so, what is
each relationship, and what identity model goes with it?

**Short answer:** yes to "G". G2C, G2B and G2G are established e-government terms, and G2E is a
secondary one. US sources separate levels of government in plain words ("federal, state, and
local", "intergovernmental", SLTT), not in acronyms. **F2S, F2L and S2L were not found** in
authoritative use. A workbook page that used them would be coining them.

**What moved to the workbook (approved 2026-11-25):** a counterparty crosswalk and the terms,
added to the workbook's *External Partner Identity* chapter
([Book 03, Chapter 15](https://whalermike.github.io/modernization-workbook/docs/books/b03-hr-identity/15-external-partner-identity.html)), in workbook pull request [#769](https://github.com/WhalerMike/modernization-workbook/pull/769).
G2C stays outside the workbook's scope (its decision WD-050). The rest of this page is kept for
reference and doesn't change the workbook.

## 1. Verdict for each term

| Term | Meaning | Verdict | Source |
|---|---|---|---|
| B2B | Business to business | Established | Census Bureau E-Stats uses manufacturing and wholesale e-commerce as its B2B measure ([census.gov FAQ](https://census.gov/programs-surveys/e-stats/about/faqs.html)). No reliable coiner or date was found |
| B2C | Business to consumer | Established | Same |
| C2C, C2B | Consumer to consumer; consumer to business | Established in trade use, secondary | [Types of e-commerce](https://Www.Wikipedia.org/wiki/Types_of_e-commerce) **[Non-government]** |
| B2G | Business to government, mostly procurement | Occasional; some writers treat it as a kind of B2B | Same |
| B2E, C2G | Business to employee; citizen to government | Occasional, mostly textbook use | Same |
| G2G, G2B, G2C | Government to government, to business, to citizen | **Established** | CRS RL31057 names "three distinct sectors" ([everycrsreport.com](https://www.everycrsreport.com/reports/RL31057.html), updated 2003-01-28) |
| G2E | Government to employee | Established, secondary | RL31057: "Some observers also identify a fourth sector"; a subset of G2G |
| F2S, F2L, S2L | Federal to state, federal to local, state to local | **Not found** | A search of OMB, CRS, UN and OECD sources, and of federal data-exchange pages, found none |

The OECD's [2025 definition of e-commerce](https://www.oecd.org/en/publications/the-2025-oecd-definition-of-e-commerce-and-guidelines-for-interpretation_2254f1de-en)
turns on the ordering method, not on who the parties are, and says the parties can include
governments.

**Open point:** the 2002 President's Management Agenda E-Government Strategy is usually described
as having four portfolios (Government to Citizen, Government to Business, Government to
Government, and Internal Efficiency and Effectiveness). The archived strategy PDF
([UNT web archive](https://webarchive.library.unt.edu/web/20081101060115/http:/www.whitehouse.gov/omb/inforeg/egovstrategy.pdf))
returned no text, so the exact portfolio names are **not verified**. OMB's archived G2G portfolio
page is readable: its aim was to "forge new partnerships among levels of government", and it lists
Geospatial One-Stop, Disaster Management, SAFECOM, E-Vital and Grants.gov
([webharvest.gov, 2004](https://webharvest.gov/peth04/20041023084637/http:/www.whitehouse.gov/omb/egov/gtog.htm)).
Related: [OMB press release 2002-11](https://georgewbush-whitehouse.archives.gov/omb/pubpress/2002-11.html),
[GAO-03-229](https://www.gao.gov/products/gao-03-229).

## 2. Relationship matrix

| Relationship | Definition | US examples | Identity and trust model |
|---|---|---|---|
| G2C | An agency serving the public | IRS e-file; Login.gov sign-in for public services | Login.gov as the identity provider; [OMB M-26-18](https://www.whitehouse.gov/wp-content/uploads/2026/08/M-26-18-Scaling-Use-of-Login.gov-to-Deliver-a-Universal-Sign-on-for-Public-Services_3e1851.pdf) makes it the universal sign-on. In Entra terms, customer identity: an External ID external tenant ([Learn](https://learn.microsoft.com/entra/external-id/external-identities-overview)) |
| G2B / B2G | Grants, procurement, regulation | SAM.gov, Grants.gov | Both sign in through Login.gov ([GrantSolutions guide](https://home.grantsolutions.gov/home/wp-content/uploads/2025/02/Grantor-Process-Login.gov_.pdf)). A business partner's people working in agency systems are B2B collaboration guests |
| G2G, federal to federal | Agency to agency | Shared services; accepting another agency's PIV | Federation (FIPS 201-3 section 7). In Entra: B2B collaboration, cross-tenant access settings, and [B2B direct connect](https://learn.microsoft.com/entra/external-id/b2b-direct-connect-overview), which supports Teams Connect shared channels |
| G2G, federal to state and local | Vertical, intergovernmental | [IRS FedState](https://www.irs.gov/irm/part11/irm_11-003-032); E-Vital and Grants.gov in OMB's 2002 G2G portfolio | Signed agreements; mostly file-to-file or system-to-system exchange (non-person identity). [Login.gov serves state and local programs](https://www.gsa.gov/blog/2021/02/18/logingov-to-provide-authentication-and-identity-proofing-services-to-a-limited-number-of-federally-funded-state-and-local-government-programs) under Title III of the Intergovernmental Cooperation Act and OMB Circular A-97 (GSA, 2021, archived) |
| G2G, justice and public safety, all levels | CJIS information sharing | FBI CJIS systems; [NIEF, formerly GFIPM](https://bja.ojp.gov/program/it/national-initiatives/gfipm) | A trust federation: each agency's identity provider sends attributes to service providers. The [CJIS Security Policy](https://le.fbi.gov/cjis-division/cjis-security-policy-resource-center/policy-and-implementation) requires MFA; [NIST IR 8523](https://nvlpubs.nist.gov/nistpubs/ir/2025/NIST.IR.8523.pdf) gives state and local MFA guidance |
| G2G, state to local and tribal | Within a state; government to government | State-run benefit and law-enforcement systems | Outside federal scope; the same federation patterns |
| G2E | An agency and its own workforce | Personnel and HR systems | The workforce tenant, PIV, Entra ID: the workbook's core |
| C2G | The public reporting to government | Tips, petitions, comments | Usually anonymous, or through Login.gov |

**Entra naming:** in Microsoft's products B2B and B2C are tenant models, not counterparties. A
state employee using a federal app is G2G in policy terms and a B2B collaboration guest in Entra.
Azure AD B2C has been closed to new customers since May 1, 2025; External ID replaces it
([Learn](https://learn.microsoft.com/entra/external-id/external-identities-overview)).
Cross-tenant access settings govern B2B collaboration and B2B direct connect
([Learn](https://learn.microsoft.com/entra/external-id/cross-tenant-access-overview)).

## 3. Levels of government

- **In words, not acronyms.** RL31057 says G2G covers exchanges "between the federal, state, and
  local levels." OMB's 2002 G2G page names "Federal, State and Local" governments, not tribal ones.
- **The US terms in use:** "intergovernmental" (the
  [DHS Office of Intergovernmental Affairs](https://www.dhs.gov/office-intergovernmental-affairs);
  the Intergovernmental Cooperation Act) and **SLTT**, defined in statute as a state, local,
  Tribal or territorial government or a subdivision of one
  ([Pub. L. 117-150, section 2](https://www.govinfo.gov/content/pkg/PLAW-117publ150/html/PLAW-117publ150.htm),
  2022) and used throughout [CISA](https://cisa.gov/topics/state-local-tribal-and-territorial).
  Legal writing calls the wider subject
  "[data federalism](https://harvardlawreview.org/print/vol-135/data-federalism/)."
- **Internationally:** the UN E-Government Survey scores national portals and, separately, city
  portals in its [Local Online Service Index](https://publicadministration.un.org/egovkb/en-us/About/E-Government-at-Local-Level/Local-Online-Service-Index-LOSI).
  That is a split by level, with no F2x terms.
- **Reading used:** write "federal-to-state (G2G)" or "intergovernmental (SLTT)", never F2S or F2L.

## 4. What the workbook already had (checked on origin/main, 2026-11-25)

- **B2B:** about 40 files. The *External Partner Identity* chapter already counted states, tribal
  governments and other agencies as partners, with a fictional state agency as its worked example.
  The Partner Access Profile appendix, the cross-tenant sections of the identity book, and the
  decision that B2B guests are the default (cross-tenant synchronization the exception) all exist.
- **B2C and External ID external tenants:** tagged as customer identity and out of scope in the
  Learn coverage map.
- **Public services and Login.gov:** out of scope under decision WD-050.
- **G2G, G2B, G2C, B2G, G2E, F2S, F2L, "intergovernmental":** no text hits. New.

## 5. Options considered

1. Terms only. 2. **A counterparty crosswalk inside the External Partner Identity chapter, with the
terms defined there (chosen).** 3. A separate taxonomy page (would repeat that chapter).
4. Reopen WD-050 to cover G2C and G2B public sign-on (a scope change).

## Sources

All read 2026-11-25. The full list is on the [Sources](../sources.md#b2b-b2c-and-g2x-relationship-names)
page.
