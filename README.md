# Ksatria Muslim

Project Pendidikan anak


### Buy package and log usage

- /api/reward-history/buy_package/

body 
```json
{"child": "childId", "package": "packageTitle"}
```

response
```json
{
  "permissible": "true/false",
  "message": "nullable kadang ada kadang gak ada",
  "coin_remaining": "integer",
  "duration_remaining": "integer / float minutes"
}
```

- /api/package-usage/log/

body
```json
{
  "child": "childId",
  "package": "package title",
  "finished_at": "string format 202001011010, nullable",
  "started_at": "string format 202001011010, nullable"
}
```

response

```json
{"ok": "true"}
```
