# CommsPliant Python SDK

Official Python client for the [CommsPliant Customer Integration API](https://developer.commspliant.com/).

Requires Python 3.9 or later.

## Installation

```bash
pip install commspliant
```

To work on the SDK itself, clone this repository and run `pip install -e ".[dev]"`.

## Quickstart

```python
from commspliant import Client

client = Client("ck_YOUR_API_KEY")

result = client.render_html(
    template_id="550e8400-e29b-41d4-a716-446655440000",
    variables={
        "title": "Monthly Report",
        "user": {"name": "Jane Doe"},
    },
)

with open("document.html", "wb") as output_file:
    output_file.write(result.body)
```

## Authentication

By default the SDK sends `X-Api-Key: ck_...`.

```python
client = Client("ck_YOUR_API_KEY", use_bearer_auth=True)
```

## Configuration

```python
client = Client("ck_YOUR_API_KEY", base_url="http://localhost:8085")
```

## Errors

Non-success API responses raise `APIError` with `status_code`, `message`, and `request_id`.

## Documentation

Endpoint guides and SDK usage examples: [doc/README.md](doc/README.md)

## Links

- [PyPI package](https://pypi.org/project/commspliant/)
- [Developer Portal](https://developer.commspliant.com/)
- [About CommsPliant](https://commspliant.com/)
