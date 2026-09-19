# Render PDF

## HTTP

- **Method:** `POST`
- **Path:** `/api/v1/render/pdf`
- **Permission:** `render.execute`

## Description

Resolves an **approved** template version, renders HTML with `variables`, converts to PDF, and returns the PDF as a streamed response.

Same auth rules as `POST /api/v1/render/html`.

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `templateId` | UUID string | Yes | Template to render (latest approved version is used) |
| `variables` | object | Yes | Values for template placeholders |

## Response

- **Status:** `200 OK`
- **Content-Type:** `application/pdf`
- **Body:** Rendered PDF stream
- **Headers:** `X-Request-ID` (request correlation ID), `Content-Disposition`

## Errors

| Status | Meaning |
|--------|---------|
| 400 | Invalid request body or parameters |
| 401 | Missing or invalid API key |
| 403 | Valid API key but missing `render.execute` permission |
| 404 | Template not found or not visible in the key's organization |
| 422 | Template version not approved for rendering |
| 429 | Render quota exceeded |
| 500 | Unexpected server error |

## SDK example

```python
from commspliant import Client

client = Client("ck_YOUR_API_KEY")

result = client.render_pdf(
    template_id="550e8400-e29b-41d4-a716-446655440000",
    variables={
        "title": "Invoice",
        "amount": "99.00",
    },
)

with open("document.pdf", "wb") as output_file:
    output_file.write(result.body)
```
