import json
import re

# CWE_ID들 추가해야함
CWE_MAP = {
    "16":    "Configuration",
    "59":    "Improper Link Resolution Before File Access",
    "90":    "LDAP Injection",
    "119":   "Buffer Overflow",
    "125":   "Out-of-bounds Read",
    "189":   "Numeric Errors",
    "190":   "Integer Overflow or Wraparound",
    "200":   "Information Exposure",
    "264":   "Permissions, Privileges, and Access Control",
    "310":   "Cryptographic Issues",
    "399":   "Resource Management Errors",
    "400":   "Uncontrolled Resource Consumption",
    "415":   "Double Free",
    "416":   "Use After Free",
    "476":   "NULL Pointer Dereference",
    "787":   "Out-of-bounds Write",
    "CWE":   ""
}

# unified diff 의 hunk 헤더를 잡아내는 정규식
HUNK_HEADER_RE = re.compile(r'^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@')

def parse_diff(diff_text):
    """
    diff_text를 “파일별 섹션”으로 나눈 뒤,
    - 삭제(-) 행이 단 한 줄이라도 있는 파일만 골라
    - 그 부분의 “패치 전 코드” (삭제행과 컨텍스트 공백행) 를 모아서 processed_code 생성
    - 그 processed_code 내에서 삭제행에 해당했던 라인 번호(1-based) 리스트 removed_ranges 생성
    """
    lines = diff_text.splitlines()
    file_hunks = {}     # { filename: [ { 'lines':[], 'flags':[] }, … ] }
    cur_file = None

    for line in lines:
        # --- a/... / +++ b/... 에서 파일 이름 추출
        if line.startswith('diff --git '):
            parts = line.split()
            if len(parts) >= 4:
                # parts[2] == "a/path", parts[3] == "b/path"
                cur_file = parts[2][2:]
                file_hunks[cur_file] = []
            continue

        if cur_file is None:
            continue

        # hunk 시작
        if HUNK_HEADER_RE.match(line):
            file_hunks[cur_file].append({'lines': [], 'flags': []})
            continue

        # 아직 hunk를 만나지 못했으면 스킵
        if not file_hunks[cur_file]:
            continue

        seg = file_hunks[cur_file][-1]
        #   +추가 라인  => 패스
        if line.startswith('+') and not line.startswith('+++'):
            continue
        #   -삭제 라인  => 코드에 추가, flag=True
        elif line.startswith('-') and not line.startswith('---'):
            seg['lines'].append(line[1:])
            seg['flags'].append(True)
        #    공백 라인  => 컨텍스트, flag=False
        elif line.startswith(' '):
            seg['lines'].append(line[1:])
            seg['flags'].append(False)
        else:
            # ---+++ 기타 diff 메타라인
            continue

    # (1) “삭제행이 한 줄 이상 있는 파일”만 골라서 processed_code 빌드
    processed_lines = []
    removed_indices = []
    idx = 0

    for fname, hunks in file_hunks.items():
        # 이 파일에 삭제행이 하나라도 없다면 건너뛰기
        if not any(any(seg['flags']) for seg in hunks):
            continue

        # 삭제행이 있는 파일만, 그 코드 섹션 모두를 모아서
        for seg in hunks:
            for flag, txt in zip(seg['flags'], seg['lines']):
                idx += 1
                processed_lines.append(txt)
                if flag:
                    removed_indices.append(idx)

    processed_code = "\n".join(processed_lines)

    # (2) removed_indices를 “연속 구간”으로 묶어서 start-end 형식 문자열 리스트로 변환
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
    in_path, out_path = 'patch_db_secu_only_cves.json', 'patch_db_cves_preprocessed.jsonl'

    with open(in_path, 'r', encoding='utf-8') as fin:
        records = json.load(fin)

    with open(out_path, 'w', encoding='utf-8') as fout:
        for rec in records:
            cve = rec.get("CVE_ID", "")
            cwe = rec.get("CWE_ID", "")
            cwe_name = CWE_MAP.get(cwe, "")

            diff_code = rec.get("diff_code", "")
            proc_code, removed = parse_diff(diff_code)

            out_obj = {
                "CVE_ID":               cve,
                "CWE_ID":               cwe,
                "CWE_NAME":             cwe_name,
                "processed_code":       proc_code,
                "removed_line_numbers": removed
            }
            fout.write(json.dumps(out_obj, ensure_ascii=False) + "\n")


main()