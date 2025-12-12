import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
# 1번 파일에서 '엔진'을 가져옵니다.
from markdown_fixer_logic import markdown_fixer


def run_correction():
    """'오류 수정' 버튼을 눌렀을 때 실행될 함수"""
    # 1. 입력창(왼쪽)에서 텍스트 전체를 가져옵니다.
    input_text = input_textbox.get("1.0", tk.END)

    if not input_text.strip():
        messagebox.showwarning("경고", "수정할 텍스트가 없습니다.")
        return

    try:
        # 2. '엔진' 함수를 실행합니다.
        corrected_text = markdown_fixer(input_text)

        # 3. 출력창(오른쪽)의 기존 내용을 지웁니다.
        output_textbox.configure(state='normal')  # 수정 가능 상태로
        output_textbox.delete("1.0", tk.END)

        # 4. 수정된 텍스트를 출력창에 삽입합니다.
        output_textbox.insert("1.0", corrected_text)
        output_textbox.configure(state='disabled')  # 다시 읽기 전용으로

    except Exception as e:
        messagebox.showerror("오류 발생", f"처리 중 오류가 발생했습니다:\n{e}")


# --- (신규) 리셋 버튼 함수 ---
def reset_text():
    """'모두 지우기' 버튼을 눌렀을 때 실행될 함수"""
    # 1. 입력창(왼쪽) 비우기
    input_textbox.delete("1.0", tk.END)

    # 2. 출력창(오른쪽) 비우기
    output_textbox.configure(state='normal')  # 수정 가능 상태로
    output_textbox.delete("1.0", tk.END)
    output_textbox.configure(state='disabled')  # 다시 읽기 전용으로


# --- 기본 창 설정 ---
root = tk.Tk()
root.title("마크다운 오류 검사기")
root.geometry("1200x800")  # 창 크기 (너비x높이)

# --- 메인 프레임 (모든 것을 담음) ---
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# --- UI를 2개의 열로 나누기 위한 프레임 ---
frame_left = tk.Frame(main_frame)
frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

frame_right = tk.Frame(main_frame)
frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

# --- 왼쪽 영역 (입력) ---
tk.Label(frame_left, text="[수정 전 텍스트]", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
input_textbox = scrolledtext.ScrolledText(frame_left, wrap=tk.WORD, height=10, width=50, undo=True)
input_textbox.pack(fill=tk.BOTH, expand=True)

# --- 오른쪽 영역 (출력) ---
tk.Label(frame_right, text="[수정 후 텍스트]", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
output_textbox = scrolledtext.ScrolledText(frame_right, wrap=tk.WORD, height=10, width=50,
                                           state='disabled')  # 처음엔 읽기 전용
output_textbox.pack(fill=tk.BOTH, expand=True)

# --- (수정) 버튼 프레임 ---
button_frame = tk.Frame(root)
button_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

# --- '오류 수정' 버튼 ---
correct_button = tk.Button(button_frame, text="▶ 마크다운 오류 수정 실행 ( ▶ )", font=("Arial", 12, "bold"),
                           command=run_correction)
correct_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

# --- '리셋' 버튼 (신규) ---
reset_button = tk.Button(button_frame, text="모두 지우기 (리셋)", font=("Arial", 12, "bold"), command=reset_text)
reset_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

# --- 앱 실행 ---
root.mainloop()