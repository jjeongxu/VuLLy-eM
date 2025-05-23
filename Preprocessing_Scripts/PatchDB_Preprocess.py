import json
import re
import random
import tiktoken # GPT 3.5 turbo tokenizer

CWE_MAP = {
    "120": "Buffer Copy without Checking Size of Input",
    "121": "Stack-based Buffer Overflow",
    "122": "Heap-based Buffer Overflow",
    "123": "Write-what-where Condition",
    "125": "Out-of-bounds Read",
    "129": "Improper Validation of Array Index",
    "134": "Use of Externally-Controlled Format String",
    "190": "Integer Overflow or Wraparound",
    "191": "Integer Underflow (Wrap or Wraparound)",
    "415": "Double Free",
    "416": "Use After Free",
    "787": "Out-of-bounds Write",
    "805": "Buffer Access with Incorrect Length Value",
    "824": "Access of Uninitialized Pointer"
}

# for diff parsing
HUNK_HEADER_RE = re.compile(r'^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@')

try:
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
except KeyError:
    enc = tiktoken.get_encoding("cl100k_base")

def parse_diff(diff_text: str):
    """
    diff_text를 src code 파일별로 분리 -> 삭제(-) line 존재하는 src code 파일의
    '패치 전 코드' && 삭제된(diff된) Line 번호 range 구하기.
    """
    lines = diff_text.splitlines()
    file_hunks = {}
    cur_file = None

    for line in lines:
        # 파일 이름 잡기
        if line.startswith('diff --git '):
            parts = line.split()
            if len(parts) >= 4:
                cur_file = parts[2][2:]     # "a/..." → "..."
                file_hunks[cur_file] = []
            continue

        if cur_file is None:
            continue

        # hunk 헤더
        if HUNK_HEADER_RE.match(line):
            file_hunks[cur_file].append({'lines': [], 'flags': []})
            continue

        if not file_hunks[cur_file]:
            continue

        seg = file_hunks[cur_file][-1]

        if line.startswith('+') and not line.startswith('+++'):
            continue # 추가 행 무시
        elif line.startswith('-') and not line.startswith('---'):
            seg['lines'].append(line[1:])
            seg['flags'].append(True)
        elif line.startswith(' '):
            seg['lines'].append(line[1:])
            seg['flags'].append(False)

    processed_lines, removed_indices, idx = [], [], 0

    for fname, hunks in file_hunks.items():
        if not any(any(seg['flags']) for seg in hunks):
            continue  # 삭제 행 없는 파일 skip

        for seg in hunks:
            for flag, txt in zip(seg['flags'], seg['lines']):
                idx += 1
                processed_lines.append(txt)
                if flag:
                    removed_indices.append(idx)

    processed_code = "\n".join(processed_lines)

    # 삭제 행 range 계산
    removed_ranges = []
    for n in sorted(removed_indices):
        if not removed_ranges or n > removed_ranges[-1][1] + 1:
            removed_ranges.append([n, n])
        else:
            removed_ranges[-1][1] = n
    removed_ranges = [
        f"{a}-{b}" if a != b else f"{a}"
        for a, b in removed_ranges
    ]

    return processed_code, removed_ranges

def main():
    in_path  = 'patch_db_secu_only_cves.json'
    out_path = 'PatchDB_Processed_Dataset.jsonl'

    i = 0
    rand_list = random.sample(range(1000, 3601), 800)

    with open(in_path, 'r', encoding='utf-8') as fin:
        records = json.load(fin)

    with open(out_path, 'w', encoding='utf-8') as fout:
        for rec in records:
            cve = rec.get("CVE_ID", "")
            cwe = rec.get("CWE_ID", "")

            ## CWE_MAP에 있는 취약점만 전처리 데이터셋에 저장
            if cwe not in CWE_MAP:
                continue

            cwe_name  = CWE_MAP[cwe]
            diff_code = rec.get("diff_code", "")
            proc_code, removed = parse_diff(diff_code)

            token_len = len(enc.encode(proc_code))
            if token_len < 128 or token_len > 2048:
                continue

            out_obj = {
                "instruction": "Check if the following code has vulnerabilities. If there is, tell me the line number and what the vulnerability is.",
                "input": proc_code,
                "output": "Line number: {}: {}".format(removed, cwe_name),
                "idx": rand_list.pop()
            }
            fout.write(json.dumps(out_obj, ensure_ascii=False) + "\n")


main()
