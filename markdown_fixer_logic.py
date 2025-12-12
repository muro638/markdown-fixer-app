import re

def get_indent_level(line: str) -> int:
    """라인의 들여쓰기 레벨(공백 수)을 반환합니다."""
    return len(line) - len(line.lstrip(' '))

def markdown_fixer(text: str) -> str:
    """
    주어진 텍스트의 마크다운 오류를 수정합니다.
    (모든 규칙이 적용된 최종본)
    """
    # --- (공통 패턴) ---
    list_item_pattern = re.compile(r'^[ \t]*([\*-]|\d+\.)(?:( +)(.*)?|([ \t]*))$')
    title_pattern = re.compile(r'^\s*\*\*[^*].*\*\*\s*$')

    lines = text.splitlines()
    if not lines:
        return ""

    # --- 0단계: 하위 항목을 가진 부모 줄(parent) 미리 파악하기 ---
    parent_map = {}
    last_index = len(lines) - 1

    for i, current_line in enumerate(lines):
        if i < last_index:
            is_current_list = bool(list_item_pattern.match(current_line))
            if is_current_list:
                next_line = lines[i + 1]
                is_next_list = bool(list_item_pattern.match(next_line))

                if is_next_list:
                    current_indent = get_indent_level(current_line)
                    next_indent = get_indent_level(next_line)

                    if next_indent > current_indent:
                        parent_map[i] = True

    processed_lines = []

    # --- 1차 처리: 개별 라인 내용 수정 ---
    for i, line in enumerate(lines):
        current_line = line

        # --- 규칙 1.2 ---
        current_line = current_line.replace(':**', '**:')

        # --- 규칙 1.2.5 (종료 불일치) ---
        current_line = re.sub(r'^([ \t]*([\*-]|\d+\.) +)(?!\*\*)([^\s:][^:]*?)\*\*(?=:)', r'\1**\3**:', current_line)
        # current_line = re.sub(r'^([ \t]*([\*-]|\d+\.) +)(?!\*\*)([^:]+?)\*\*(?=:)', r'\1**\3**:', current_line)

        # --- 규칙 1.2.6 (시작 불일치) ---
        current_line = re.sub(r'^([ \t]*([\*-]|\d+\.) +)(\*\*[^*]+)(?<!\*\*):', r'\1\3**:', current_line)

        # --- (신규) 규칙 2: 불릿포인트 뒤에 공백 추가 (*item -> * item) ---
        current_line = re.sub(r'^( *([\*-]|\d+\.))([^\s\*\.\\])', r'\1 \3', current_line)

        # --- (수정) 규칙 1: 불릿 공백 갯수 수정 (관계형 들여쓰기) ---
        match = re.match(r'^( *)([\*-]|\d+\.)(?:( +)(.*)?|([ \t]*))$', current_line)

        if match:
            spaces_before = match.group(1)
            bullet = match.group(2)
            content = match.group(4) if match.group(3) else None
            space_len = len(spaces_before)
            # 1-2칸은 1레벨로 간주
            if 1 <= space_len <= 2:
                spaces_before = ""

            elif 3 <= space_len <= 5:
                # 3-5칸은 "정상 2레벨"로 간주하고 4칸으로 고정
                spaces_before = "    "

            elif 6 <= space_len <= 9:
                # (기존 로직 유지) 6-9칸은 3레벨(8칸)로 간주
                spaces_before = "        "

            if content is not None:
                current_line = f"{spaces_before}{bullet} {content}"
            else:
                current_line = f"{spaces_before}{bullet}"

        # --- 규칙 1.6: 항목별 답안 볼드체 (콜론 기준) ---
        current_line = re.sub(r'^([ \t]*([\*-]|\d+\.) +)(?!\*\*)([^:]+)(?<!\*\*):', r'\1**\3**:', current_line)

        # --- (신규) 규칙 1.6.5: 볼드체 뒤 공백 제거 (**항목** :) ---
        current_line = re.sub(r'(\*\*[^*]+\*\*)([ \t]+):', r'\1:', current_line)

        # --- 규칙 1.7: 띄어쓰기 두번 오류 ---
        leading_spaces_len = get_indent_level(current_line)
        indent = current_line[:leading_spaces_len]
        content = current_line[leading_spaces_len:]
        content = re.sub(r' {2,}', ' ', content)
        current_line = indent + content

        # --- (신규) 규칙 1.8: 제목 볼드체 시작 불일치 (**제목) ---
        if not match and current_line.strip().startswith('**') and not current_line.strip().endswith('**'):
            current_line = current_line.rstrip() + '**'

        # 규칙 1.9: 일반 글 볼드체 제거
        is_list_item = bool(match) # 1.5의 match 객체
        is_title = bool(title_pattern.match(current_line))

        if not is_list_item: # 불릿/목록이 아닌 라인만 검사
            if not is_title:  # 제목이 아닌 경우 (일반 줄글)

                # 1.9: 일반 줄글의 볼드체 제거 (예: **다우** -> 다우)
                current_line = re.sub(r'\*\*(.*?)\*\*', r'\1', current_line)

        # --- 나머지 규칙 (1.1, 1.3, 1.4) ---
        current_line = re.sub(r'(니다)([ \t]*)$', r'\1.\2', current_line)  # 1.1
        current_line = current_line.replace('% p', '%p')  # 1.3
        current_line = current_line.replace('~', '-')  # 1.4
        current_line = current_line.replace('..', '.') # 온점 두개 제거
        # --- (신규) 규칙 1.4.5: 쉼표 뒤 띄어쓰기 (숫자 제외) ---
        # 1. (?<!\d),(?=\S) : 앞에 숫자가 없는 쉼표 뒤에 공백이 아닌 문자가 올 때 (예: "가,나")
        # 2. (?<=\d),(?=[^\s\d]) : 앞에 숫자가 있는 쉼표 뒤에 '숫자도 공백도 아닌' 문자가 올 때 (예: "1,가")
        # -> 제외됨: "1,000" (뒤가 숫자), "가, 나" (뒤가 공백)
        current_line = re.sub(r'(?<!\d),(?=\S)|(?<=\d),(?=[^\s\d])', ', ', current_line)

        processed_lines.append(current_line)

    # --- 1.5단계: 하위 항목이 있는 부모 항목에 볼드체 적용 ---
    bolded_lines = []
    pass_1_last_index = len(processed_lines) - 1

    for i, current_line in enumerate(processed_lines):
        is_current_list = bool(list_item_pattern.match(current_line))
        is_already_bold = bool(re.match(r'^[ \t]*([\*-]|\d+\.) +(\*\*.*\*\*)', current_line))

        if is_current_list and not is_already_bold and i < pass_1_last_index:
            # (신규) 부모가 문장(.)으로 끝나면 볼드체 적용 안 함
            is_sentence = current_line.rstrip().endswith('.')

            if not is_sentence:
                next_line = processed_lines[i + 1]
                is_next_list = bool(list_item_pattern.match(next_line))

                if is_next_list:
                    current_indent = get_indent_level(current_line)
                    next_indent = get_indent_level(next_line)

                    if next_indent > current_indent:
                        current_line = re.sub(
                            r'^([ \t]*([\*-]|\d+\.) +)(.*)$',
                            r'\1**\3**',
                            current_line
                        )

        bolded_lines.append(current_line)

    # --- 2차 처리: 개행 추가 및 제거 ---
    final_lines = []
    last_index = len(bolded_lines) - 1

    for i, corrected_line in enumerate(bolded_lines):
        is_current_list = bool(list_item_pattern.match(corrected_line))
        is_current_empty = not corrected_line.strip()

        if is_current_empty:
            is_previous_list = (i > 0) and bool(list_item_pattern.match(bolded_lines[i - 1]))
            is_next_list = (i < last_index) and bool(list_item_pattern.match(bolded_lines[i + 1]))

            if is_previous_list and is_next_list:
                continue
            else:
                final_lines.append(corrected_line)

        elif is_current_list:
            if i > 0:
                previous_line = bolded_lines[i - 1]
                is_previous_list = bool(list_item_pattern.match(previous_line))
                is_previous_empty = not previous_line.strip()
                is_previous_title = bool(title_pattern.match(previous_line))

                # 개행 추가 조건: (1) 이전 줄이 목록 X, (2) 빈 줄 X, (3) 제목 X
                if not is_previous_list and not is_previous_empty and not is_previous_title:

                    # (신규 예외) [제목 -> 줄글 -> 목록] 패턴이면 개행 안 함
                    is_two_lines_before_title = False
                    if i > 1:
                        two_lines_before = bolded_lines[i - 2]
                        # 전전 줄이 제목인지 확인
                        is_two_lines_before_title = bool(title_pattern.match(two_lines_before))

                    # 전전 줄이 제목이 아닐 때만 개행 추가
                    if not is_two_lines_before_title:
                        final_lines.append("")

            final_lines.append(corrected_line)

        else:
            final_lines.append(corrected_line)

    # --- 규칙 4: 마지막 줄이 빈 줄이면 모두 제거 ---
    while final_lines and not final_lines[-1].strip():
        final_lines.pop()

    return '\n'.join(final_lines)