"""
Inngest durable background functions for FlyRank.
Defines:
- say_hello: Simple test function with sleep step.
- make_report: Asynchronous report generation with simulated slow work, failure injection, and automatic retries.
- heartbeat: Scheduled cron job running on the clock logging report metrics.
"""

from datetime import timedelta
from typing import Any, Dict
import inngest

from src.jobs.client import inngest_client
from src.jobs.state import update_report, get_report_counts, get_report


# --- Stage 1: say-hello Function ---
@inngest_client.create_function(
    fn_id="say-hello",
    name="Say Hello in Background",
    trigger=inngest.TriggerEvent(event="test/hello"),
)
async def say_hello(ctx: inngest.Context, step: inngest.Step) -> str:
    """Test background function sleeping for 5 seconds before returning a greeting."""
    await step.sleep("sleep-5s", timedelta(seconds=5))
    return "Hello from the background!"


# --- Stage 2 & 3: make-report Function ---
async def on_report_failed(ctx: inngest.Context, step: inngest.Step) -> None:
    """Invoked when make-report exhausts all retries."""
    event_data = (
        ctx.event.data.get("event", {}).get("data", {})
        if "event" in ctx.event.data
        else ctx.event.data
    )
    report_id = event_data.get("id")
    error_msg = ctx.event.data.get("error", {}).get("message", "The report oven is broken!")
    if report_id:
        update_report(
            report_id=report_id,
            status="failed",
            error=error_msg,
            attempts=ctx.attempt if hasattr(ctx, "attempt") else 3,
        )


@inngest_client.create_function(
    fn_id="make-report",
    name="Make Asynchronous Report",
    trigger=inngest.TriggerEvent(event="report/requested"),
    retries=2,
    on_failure=on_report_failed,
)
async def make_report(ctx: inngest.Context, step: inngest.Step) -> Dict[str, Any]:
    """
    Generate an asynchronous report.
    1. Sleeps 8 seconds to simulate heavy background computation / external AI call.
    2. Builds report and updates in-memory registry.
    If topic is 'fail', raises an error to trigger automatic retries with backoff.
    """
    data = ctx.event.data
    report_id = data.get("id")
    topic = data.get("topic", "")

    # Step 1: Simulate slow compute (8 seconds)
    await step.sleep("do-the-slow-work", timedelta(seconds=8))

    # Step 2: Build the report
    def build_report_step() -> Dict[str, Any]:
        # Failure injection for testing retries with backoff (Stage 3)
        if topic == "fail":
            raise RuntimeError("The report oven is broken!")

        result_text = f"Report on '{topic}' generated successfully."
        update_report(
            report_id=report_id,
            status="done",
            result=result_text,
            attempts=getattr(ctx, "attempt", 1),
        )
        return {
            "id": report_id,
            "topic": topic,
            "status": "done",
            "result": result_text,
        }

    report_result = await step.run("build-report", build_report_step)
    return report_result


# --- Stage 4: Scheduled Heartbeat Cron ---
@inngest_client.create_function(
    fn_id="heartbeat",
    name="Heartbeat Status Monitor",
    trigger=inngest.TriggerCron(cron="* * * * *"),
)
async def heartbeat(ctx: inngest.Context, step: inngest.Step) -> Dict[str, int]:
    """
    Scheduled cron job running every minute on the clock.
    Performs non-blocking count of reports and prints summary to stdout.
    """
    counts = get_report_counts()
    print(
        f"[HEARTBEAT CRON] pending={counts['pending']} done={counts['done']} failed={counts['failed']} total={counts['total']}",
        flush=True,
    )
    return counts
