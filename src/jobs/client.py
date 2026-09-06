"""
Inngest client initialization for FlyRank.
"""

from datetime import timedelta
import os
import inngest

# Initialize Inngest client with unique app id
inngest_client = inngest.Inngest(
    app_id="report-api",
    is_production=os.getenv("INNGEST_IS_PRODUCTION", "false").lower() == "true",
    request_timeout=timedelta(seconds=2),
)
