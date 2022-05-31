# Telegram Stock Bot
### Regex search
This bot will detect any __stock__ symbol like `$NVDA` and reply with the current market price.

The response:
- Works with multiple values on the same message
- Includes pre/after-market prices too
- Links every company to a Google search

![](https://github.com/izquiratops/telegram-stock-bot/blob/main/docs/screen2.png)

### Alerts
Checks if the price of X stock reached Y value every 5 minutes. If it's the case, then notify about it.

Alerts can be added with the command `/create` or removed with `/delete`.
Look for the setted alerts with `/list`.

### Credentials
There must be a `info.json` with the following properties:
- `token`: Token from botfather
- `alerts_whitelist`: List of chats that can use the alert jobs

```
{
    "token": "123456789",
    "alerts_whitelist": ["123456789"]
}
```
