import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('BaoCao_TienDo_50_CNN_Systolic_SoC.md', 'r', encoding='utf-8') as f:
    text = f.read()

patterns = [
    'tuyệt đối không bao giờ được phép',
    'thước đo chuẩn tuyệt đối',
    'đáp ứng xuất sắc',
    'khẳng định sự nghiêm túc',
    'bẻ gãy nút thắt',
    'Trái Tim',
    'Gợi ý thuyết minh',
    'Kính thưa',
    'FULL INDUSTRIAL CLOSURE',
    'đột phá'
]

for pat in patterns:
    matches = list(re.finditer(re.escape(pat), text, re.IGNORECASE))
    print(f"'{pat}': found {len(matches)}")
    for m in matches:
        start = max(0, m.start() - 30)
        end = min(len(text), m.end() + 40)
        print('   -->', repr(text[start:end]))
