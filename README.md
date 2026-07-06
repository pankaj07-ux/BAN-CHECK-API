# Free Fire Ban Check API
**Developer:** pankaj-ux

## Run karo
```
pip install -r requirements.txt
python app.py
```

## Endpoint
```
GET /bancheck?uid=UID
```

## Example Response
```json
{
  "uid": "123456789",
  "nickname": "PlayerName",
  "region": "IND",
  "ban_status": "banned",
  "ban_period": "permanent",
  "ban_reason": "This account was confirmed for using cheats."
}
```
