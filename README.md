Example:

```python
# python transfer.py
* Serving Flask app "transfer-servers" (lazy loading)
* Environment: production
  WARNING: This is a development server. Do not use it in a production deployment.
  Use a production WSGI server instead.
* Debug mode: on
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger PIN: 158-492-775
```

Payload:

```json
# POST: http://127.0.0.1:5000/transfer
{
    "server_id": "57467c1d-a471-4804-a4e6-fe00bbd6a5e5",
    "from": {
        "project": {
            "id": "4a92824aa74445f28d7cf814a54ee283",
            "name": "botv@vccloud.vn"
        },
        "user": {
            "id": "3502ac4dda5247829c20b6561c5d188a",
            "name": "botv@vccloud.vn"
        }
    },
    "to": {
        "project": {
            "id": "90e35e1736684fe69fc06b0a15b6f1c1",
            "name": "daemon"
        },
        "user": {
            "id": "c881e5539e774a0bbd699a56da2d78cc",
            "name": "daemon"
        }
    }
}
```

If success, it will being returned:

```json
{
    "successes": True
}
```

else:

```json
{
    "successes": False
}
```
