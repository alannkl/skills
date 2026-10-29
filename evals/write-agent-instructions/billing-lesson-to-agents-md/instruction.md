add this to AGENTS.md:

when you touch anything under src/billing make sure you run make stripe-fixtures first before running the tests, otherwise the tests run against stale stripe fixtures and pass when they shouldn't. we literally shipped a double charge bug because of this last month so pls actually do it
