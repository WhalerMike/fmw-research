# Pack 3: Scheduled job on workdays

!!! info "Research notes, not workbook guidance"
    **Status:** Open · **Last checked:** 2026-11-12 · Steps are drafts until a sandbox run confirms them.

**Question:** can the instance run the daily report on workdays only, and how close to the set
time does it start?

**Background:** flow scheduled triggers run daily, weekly, monthly, once or repeated, and "use
the instance timezone". Flows are processed asynchronously, so a scheduled flow "may not run at
the exact scheduled time"
([Flow triggers](https://www.servicenow.com/docs/r/washingtondc/build-workflows/flow-triggers.html)).
Skipping weekends needs a check inside the job
([community thread](https://www.servicenow.com/community/developer-forum/scheduled-flow-on-workdays/m-p/2161492)).

This pack tests both ways: a scheduled script (A) and a scheduled flow (B).

## You need

- The `admin` role in the sandbox.
- The instance time zone: **System Properties > System**, property
  `glide.sys.default.tz`. Record it.

## A. Scheduled Script Execution

1. Go to **System Definition > Scheduled Jobs**, select **New**, then
   **Automatically run a script of your choosing**.
2. Name: `FMW sandbox pack 3: workday job`.
3. Run: **Daily**. Time: a time 10 minutes from now.
4. Select **Conditional**, and paste this into **Condition** (1 is Monday, 7 is Sunday):

    ```javascript
    var now = new GlideDateTime();
    now.getDayOfWeekLocalTime() <= 5;
    ```

5. Paste this into **Run this script**:

    ```javascript
    var now = new GlideDateTime();
    gs.info('FMW pack 3 ran at ' + now.getDisplayValue() + ' (day ' + now.getDayOfWeekLocalTime() + ')');
    ```

6. Save.

After it runs, look for the log line: go to **System Logs > System Log > All** and filter
**Message** contains `FMW pack 3 ran at`. Record the set time and the logged time.

To test the weekend skip without waiting, change the condition's `<= 5` to `<= 0`, use
**Execute Now**, and confirm no new log line appears. Then set it back.

## B. Scheduled flow

1. Open **Workflow Studio** (or **Flow Designer**) and create a flow
   `FMW sandbox pack 3: workday flow`.
2. Trigger: **Daily**, at a time 10 minutes from now.
3. Add **Flow Logic > If**. Condition: the trigger's run-start day is Saturday or Sunday. If
   your release has no day-of-week pill, add a **Run Script** step that returns
   `new GlideDateTime().getDayOfWeekLocalTime()` and test that output for 6 or 7.
4. Inside the **If**, add **End Flow**.
5. After the **If**, add **Log** with the message `FMW pack 3 flow ran`.
6. Save and **Activate**.

After it runs, open **Executions** for the flow and record the scheduled time and the actual
start time.

## Run for one week

Leave both enabled for seven days. Then record, for each day, whether each one ran and the
start delay.

## Clean up

Deactivate the scheduled job and the flow.

## Pass criteria

| Check | Pass |
|---|---|
| Runs Monday to Friday | Yes, for A and for B |
| Skips Saturday and Sunday | Yes, for A and for B |
| Start delay | Recorded (largest delay in the week) |
| Time zone | Instance time zone recorded; matches the time you expect the report |

## Copilot prompt (for use at work)

> I ran a week-long test of two ServiceNow schedules, a scheduled script and a scheduled flow,
> both meant to run on workdays only. Here are the log lines and flow execution times: [paste].
> Fill in the results template: which days each ran, whether weekends were skipped, and the
> start delay for each run. Then write a one-paragraph generic finding with no instance names.

## What to bring back here

One generic sentence, for example: "Both schedules skipped weekends; scheduled flows started up
to N minutes late during business hours."
