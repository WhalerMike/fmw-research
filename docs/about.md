# How this project works

## Why it is separate

The workbook publishes guidance that has passed its review gates. Research is earlier than that:
it asks what a service can do, what it costs and where it is available, without deciding
anything. Keeping it in its own repository means a research note can never be mistaken for
workbook guidance, and the workbook never changes because research was done.

## Isolation rules

1. **One way only.** Research pages may link to workbook pages, Microsoft Learn and other public
   sources. The workbook does not link to, import, embed or build anything from this project.
2. **No automated connection.** No submodule, shared build, shared workflow, or automation that
   opens changes in the workbook repository.
3. **Every page is labelled.** Each topic page states that it is research, the date it was last
   checked, and its status.
4. **The workbook's public rules apply here too:**
    - No agency names, and no description of any agency's status or systems.
    - Microsoft 365 GCC Moderate, or an equivalent tenant, is the baseline. GCC High and DoD
      appear only as side notes.
    - A control or tool *supports* or *addresses* a requirement. Research never claims that
      a tool by itself fulfils one.
    - Every claim names its source. Where something is my inference, the page says so.
    - Examples are generic. No work data comes here.

## Status values

| Status | Meaning |
|---|---|
| Open | The question is being researched. |
| Findings | The answer is written up with sources. Nothing is decided. |
| Candidate for integration | The finding has been put forward for the workbook. |
| Integrated | A workbook change was made. The page links to it. |

## How a finding can join the workbook

1. A topic is marked **Candidate for integration**.
2. The workbook owner names that topic and approves moving it.
3. The finding is rewritten to workbook standards in a normal workbook pull request and goes
   through the workbook's usual gates. It is not copied across.
4. The topic page here is updated to **Integrated**, with a link to the workbook page.

Nothing moves without step 2.

## License

The same terms as the workbook: the writing is under
[CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/), and any code is under the
MIT License. See [LICENSE.md](https://github.com/WhalerMike/fmw-research/blob/main/LICENSE.md).
