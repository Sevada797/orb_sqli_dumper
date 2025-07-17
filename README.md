# ORB SQLi Dumper

**ORB** (Order-based SQLi Blind Dumper) is a multithreaded Python tool for exploiting blind SQL injection vulnerabilities via `ORDER BY` clause injection. It supports dumping:

- Database names
- Table names in a database
- Custom SQL SELECT query results (multi-column + multi-row)

⚠️ **FOR EDUCATIONAL & AUTHORIZED TESTING ONLY**  
Don't be stupid. Use this on targets you are authorized to test (e.g., bug bounty, labs, CTFs).

---

## 🔥 Features

- Boolean-based blind SQLi via `ORDER BY`
- Supports injection with a custom truth-string
- Binary search ASCII-based extraction
- Multi-threaded query dumping
- Supports raw HTTP headers
- Dumps multiple rows/columns using `GROUP_CONCAT + CONCAT_WS`
- Handles messy parsing via `~` separator workaround
- Thread batching & smart flushing to file or stdout

---

## ⚙️ Usage

```bash
python3 orb_dumper.py --url "https://target.com/products?sort=INJ" \
                      --collname id \
                      --true-string 'Success message' \
                      --headers "Cookie: sessid=abc123; User-Agent: chrome" \
                      --sql-query "SELECT col1,col2,col3 FROM users LIMIT 5000" \
                      -t 4 \
                      -o results.txt
```
Or just check help:

```bash
python3 orb_dumper.py -h
```


## 🎮 Modes

| `--wish` | Mode                | Description                            |
|----------|---------------------|----------------------------------------|
| `1`      | Dump DB names       | Extracts all schema (database) names   |
| `2`      | Dump table names    | Prompts for DB name, then lists tables |
| `3`      | Custom query mode   | Dump results of any SELECT query       |

Alternatively, you can pass a custom query using `--sql-query "SELECT ..."` directly.  
If `--sql-query` is used, `--wish` is ignored.

---

## ⚠️ Notes & Warnings

- Uses the placeholder string `INJ` in your URL for injection point.
- The tool wraps your query inside:

```sql
SELECT GROUP_CONCAT(CONCAT_WS(',', col1,col2,...) SEPARATOR '~') FROM (...)
```

- Then replaces `~` with `\n` as a workaround since actual newline had parsing issues during char-by-char extraction.

- Make sure to **limit your custom queries** like:

```sql
SELECT col1, col2 FROM users LIMIT 10000
```

- I set <1 million characters for binary_search function, cause it would've crash your system set it I higher, so use e.g. LIMIT 10000 for your queries, cause if they return max dumping will fail.
- The default ASCII char range is [32–126]; anything outside returns as `?`.

---

## 💡 Tips

- Increase `-t` (threads) for faster dumps — e.g. `-t 8`
- Test the injection point with a small query before running big ones. e.g. use ```--sql-query "SELECT 'test'"```
- Set `--true-string` to a response the server gives when condition is true.
- This tool works great against apps filtering via `ORDER BY` clauses.

---

## ✍️ Author Notes

> “I cheated a bit while coding this 😅 — used `GROUP_CONCAT` + `SEPARATOR ~` to stack results into one value, and dumped it char-by-char using multithreading.  
> Also had to cap binary search max range to avoid crashing my PC. But hey — it works beautifully.”  
>
> – **Dark-Sentinel / sevada797**

---

## 🔐 Legal Disclaimer

This tool is intended for **educational purposes only**.  
Use it **only on targets you own or are authorized to test**.  
Misuse may lead to **legal consequences** — you've been warned ⚠️

---

## ☕ Useful?

If this tool saved your time or helped in a bug bounty — consider dropping a small donation 🙏

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-donate-orange?style=flat&logo=buy-me-a-coffee)](https://buymeacoffee.com/zatikyansed)
