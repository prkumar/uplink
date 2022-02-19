import sys

collect_ignore = []
if sys.version_info.major < 3:
    collect_ignore.extend(
        [
            "unit/test_aiohttp_client.py",
            "integration/test_handlers_aiohttp.py",
            "integration/test_retry_aiohttp.py",
        ]
    )
