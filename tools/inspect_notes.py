import sys, re
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

with open('BaoCao_TienDo_50_CNN_Systolic_SoC.md', 'r', encoding='utf-8') as f:
    text = f.read()

notes = re.findall(r'> 🎙️ \*\*Speaker Notes\*\*:\s*>\s*([^\n]+(?:\n>\s*[^\n]+)*)', text)
print(f'Found {len(notes)} speaker notes:')
for i, n in enumerate(notes, 1):
    clean_n = ' '.join(line.strip().lstrip('>').strip().strip('\"*') for line in n.splitlines())
    print(f'Slide {i}: {clean_n}')
