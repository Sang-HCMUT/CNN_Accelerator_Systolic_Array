# -*- coding: utf-8 -*-
"""
Script: generate_charts.py
Generates 5 publication-quality engineering benchmark charts for thesis report and slides:
  1. chart1_speedup_benchmark.png: E2E and Core Latency & Speedup vs CPU Baseline
  2. chart2_latency_breakdown.png: System Latency Decomposition & Bus Profiler (Clean Legend, No Overlap)
  3. chart3_fpga_resources.png: Physical Resource Utilization on DE2 & DE10 (Dual-Axis STA, Clean Layout)
  4. chart4_latency_scaling_k.png: Core Compute Latency Scaling vs K-Dimension
  5. chart5_verification_coverage.png: 3-Tier Verification & UVM Coverage Closure Dashboard
"""

import os
import sys
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Reconfigure stdout to utf-8 if needed
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Styling configuration for modern publication-grade figures
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#e0e0e0'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

OUTPUT_DIR = 'figures'
os.makedirs(OUTPUT_DIR, exist_ok=True)
ARTIFACT_DIR = r'C:\Users\hoang\.gemini\antigravity\brain\9f77ab99-8f96-4134-8b24-d1c001f13ee8'

# -----------------------------------------------------------------------------
# CHART 1: SPEEDUP BENCHMARK & EXECUTION CYCLES
# -----------------------------------------------------------------------------
def plot_chart1():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.8), dpi=300)
    fig.patch.set_facecolor('#ffffff')

    # Subplot 1: Total Latency & Core Latency (Log Scale)
    categories = ['PicoRV32 Software\n(Baseline RV32I)', 'Systolic Gen-1\n(Single-Byte MMIO)', 'Systolic Gen-2\n(Packed + 8 Quant)']
    e2e_cycles = [333485, 8484, 1920]
    core_cycles = [0, 93, 37]

    x = np.arange(len(categories))
    width = 0.36

    bars1 = ax1.bar(x - width/2, e2e_cycles, width, label='Tổng chu kỳ toàn hệ thống (End-to-End)', color='#1976d2', edgecolor='#0d47a1', linewidth=1.2)
    bars2 = ax1.bar(x + width/2, core_cycles, width, label='Chu kỳ tính toán lõi PE (Pure Compute)', color='#f57c00', edgecolor='#e65100', linewidth=1.2)

    ax1.set_yscale('log')
    ax1.set_ylabel('Chu kỳ xung nhịp (Clock Cycles - Log Scale)', fontsize=11, fontweight='bold', color='#1a237e')
    ax1.set_title('So Sánh Chu Kỳ Thực Thi (GEMM 8x8, K=8)', fontsize=12, fontweight='bold', pad=12, color='#0d47a1')
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, fontsize=10, fontweight='bold')
    ax1.legend(loc='upper right', frameon=True, framealpha=0.95, fontsize=9.5)
    ax1.set_ylim(5, 1500000)

    # Data value annotations
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval * 1.35, f'{int(yval):,} cyc', ha='center', va='bottom', fontsize=9, fontweight='bold', color='#0d47a1')
    
    for bar in bars2:
        yval = bar.get_height()
        if yval > 0:
            ax1.text(bar.get_x() + bar.get_width()/2.0, yval * 1.45, f'{int(yval)} cyc', ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#e65100')

    # Subplot 2: System Speedup Factor vs Software Baseline
    speedups = [1.0, 39.3, 173.7]
    colors = ['#9e9e9e', '#43a047', '#00c853']
    bars3 = ax2.bar(categories, speedups, color=colors, width=0.45, edgecolor='#1b5e20', linewidth=1.2)

    ax2.set_ylabel('Hệ Số Tăng Tốc (Speedup vs Software Baseline)', fontsize=11, fontweight='bold', color='#1b5e20')
    ax2.set_title('Mức Tăng Tốc Toàn Hệ Thống SoC (@ 50 MHz)', fontsize=12, fontweight='bold', pad=12, color='#1b5e20')
    ax2.set_ylim(0, 220)

    for bar in bars3:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 5, f'{yval:.1f}x' if yval > 1 else '1.0x (Gốc)', ha='center', va='bottom', fontsize=11, fontweight='bold', color='#1b5e20')

    # Add callout for Gen-2 highlight
    ax2.annotate('TĂNG TỐC 4.4x\nso với Gen-1!', xy=(2, 173.7), xytext=(1.25, 150),
                 arrowprops=dict(facecolor='#d50000', shrink=0.08, width=2, headwidth=8),
                 fontsize=10, fontweight='bold', color='#d50000', bbox=dict(boxstyle='round,pad=0.4', facecolor='#ffebee', edgecolor='#d50000'))

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, 'chart1_speedup_benchmark.png')
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Saved {out_path}")


# -----------------------------------------------------------------------------
# CHART 2: SYSTEM LATENCY BREAKDOWN (DONUT CHARTS WITH LEGENDS - ZERO OVERLAP)
# -----------------------------------------------------------------------------
def plot_chart2():
    # Wider figure with room at bottom for legend boxes
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.5), dpi=300)
    fig.patch.set_facecolor('#ffffff')

    # Gen-1 Profile: 8,484 cycles
    sizes_gen1 = [4919, 3037, 435, 93]
    colors_gen1 = ['#3949ab', '#1e88e5', '#fb8c00', '#43a047']
    explode_gen1 = (0.02, 0.02, 0.06, 0.12)
    legend_gen1 = [
        'CPU Fetch Lệnh/Stack BRAM: 4,919 cyc (58.0%)',
        'CPU Loop & Store Overhead: 3,037 cyc (35.8%)',
        'Giao Dịch AXI MMIO & Polling: 435 cyc (5.1%)',
        'Mảng PE Tính Toán Thuần: 93 cyc (1.1%)'
    ]

    wedges1, _, autotexts1 = ax1.pie(
        sizes_gen1, explode=explode_gen1, labels=None,
        autopct=lambda p: f'{p:.1f}%' if p > 8.0 else '',
        startangle=140, colors=colors_gen1, pctdistance=0.75,
        wedgeprops=dict(width=0.42, edgecolor='#ffffff', linewidth=2)
    )
    for autotext in autotexts1:
        autotext.set_color('white')
        autotext.set_weight('bold')
        autotext.set_fontsize(10)

    # Donut center text
    ax1.text(0, 0.08, '8,484', ha='center', va='center', fontsize=18, fontweight='bold', color='#1a237e')
    ax1.text(0, -0.12, 'Chu kỳ', ha='center', va='center', fontsize=11, color='#5c6bc0')

    ax1.set_title('Gen-1 (Single-Byte): Tổng 8,484 Chu Kỳ\nNghẽn Cổ Chai CPU Loop & MMIO Tuần Tự (98.9%)',
                  fontsize=11.5, fontweight='bold', color='#1a237e', pad=14)
    ax1.legend(wedges1, legend_gen1, loc='upper center', bbox_to_anchor=(0.5, -0.06),
               fontsize=9, frameon=True, facecolor='#f8f9fa', edgecolor='#cfd8dc')

    # Gen-2 Profile: 1,920 cycles (77.4% reduction!)
    sizes_gen2 = [1520, 363, 37]
    colors_gen2 = ['#3949ab', '#fb8c00', '#00c853']
    explode_gen2 = (0.02, 0.05, 0.12)
    legend_gen2 = [
        'CPU Fetch & Unrolled Loop: 1,520 cyc (79.2%)',
        'Giao Dịch AXI Packed MMIO: 363 cyc (18.9%)',
        'Mảng PE Tính Toán Thuần: 37 cyc (1.9%)'
    ]

    wedges2, _, autotexts2 = ax2.pie(
        sizes_gen2, explode=explode_gen2, labels=None,
        autopct=lambda p: f'{p:.1f}%' if p > 8.0 else '',
        startangle=140, colors=colors_gen2, pctdistance=0.72,
        wedgeprops=dict(width=0.42, edgecolor='#ffffff', linewidth=2)
    )
    for autotext in autotexts2:
        autotext.set_color('white')
        autotext.set_weight('bold')
        autotext.set_fontsize(10)

    # Donut center text
    ax2.text(0, 0.12, '1,920', ha='center', va='center', fontsize=18, fontweight='bold', color='#00695c')
    ax2.text(0, -0.08, 'Chu kỳ\n(-77.4%)', ha='center', va='center', fontsize=10.5, fontweight='bold', color='#00897b')

    ax2.set_title('Gen-2 (Packed Word + 8 Quantizers): Tổng 1,920 Chu Kỳ\nTiết Kiệm 77.4% Chu Kỳ Toàn Hệ Thống (Nhanh Gấp 4.4x)',
                  fontsize=11.5, fontweight='bold', color='#00695c', pad=14)
    ax2.legend(wedges2, legend_gen2, loc='upper center', bbox_to_anchor=(0.5, -0.06),
               fontsize=9, frameon=True, facecolor='#f8f9fa', edgecolor='#cfd8dc')

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, 'chart2_latency_breakdown.png')
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Saved {out_path}")


# -----------------------------------------------------------------------------
# CHART 3: FPGA PHYSICAL RESOURCE UTILIZATION (DUAL-AXIS STA & CLEAN MARGINS)
# -----------------------------------------------------------------------------
def plot_chart3():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.8), dpi=300)
    fig.patch.set_facecolor('#ffffff')

    # Subplot 1: Hardware Resource Percentage on DE2 and DE10
    metrics = ['Logic Elements / ALMs', 'Dedicated Registers', 'DSP Multipliers', 'Block RAM (BRAM)']
    de2_usage = [57.5, 28.4, 91.4, 54.6]   # 19107/33216, 9423, 64/70, 264192/483840
    de10_usage = [19.8, 23.8, 57.1, 4.7]   # 8290/41910, 9982, 64/112, 264192/5662720

    y = np.arange(len(metrics))
    height = 0.35

    rects1 = ax1.barh(y - height/2, de2_usage, height, label='Terasic DE2 (Cyclone II 90nm)', color='#1976d2', edgecolor='#0d47a1', linewidth=1.2)
    rects2 = ax1.barh(y + height/2, de10_usage, height, label='Terasic DE10-Standard (Cyclone V 28nm)', color='#00897b', edgecolor='#004d40', linewidth=1.2)

    ax1.set_xlabel('Tỉ Lệ Chiếm Dụng Tài Nguyên (%)', fontsize=11, fontweight='bold', color='#263238')
    ax1.set_title('Tỉ Lệ Sử Dụng Tài Nguyên Phần Cứng Trên 2 Nền Tảng', fontsize=11.5, fontweight='bold', pad=12, color='#263238')
    ax1.set_yticks(y)
    ax1.set_yticklabels(metrics, fontsize=10, fontweight='bold')
    ax1.set_xlim(0, 115)
    ax1.set_ylim(-0.6, len(metrics) - 0.2)

    # Value annotations: for wide bars, put inside with white text; for narrow bars, put outside
    for rect, color in [(rects1, '#0d47a1'), (rects2, '#004d40')]:
        for bar in rect:
            w = bar.get_width()
            y_pos = bar.get_y() + bar.get_height() / 2.0
            if w > 45:
                # Inside the bar: clean white text
                ax1.text(w - 2.5, y_pos, f'{w:.1f}%', va='center', ha='right', fontsize=9.5, fontweight='bold', color='#ffffff')
            else:
                # Outside the bar
                ax1.text(w + 1.8, y_pos, f'{w:.1f}%', va='center', ha='left', fontsize=9.5, fontweight='bold', color=color)

    # Legend placement at row y=1 (Dedicated Registers) where bars are only ~25-28%, so x in [50..100] is completely empty!
    ax1.legend(loc='center right', bbox_to_anchor=(0.98, 0.42), frameon=True, framealpha=0.95, facecolor='#f8f9fa', edgecolor='#cfd8dc', fontsize=9)

    # Subplot 2: Timing Slack & Fmax Comparison with DUAL Y-AXIS (No overlap, proper units!)
    platforms = ['Terasic DE2\n(Cyclone II)', 'Terasic DE10\n(Cyclone V)']
    setup_slack = [4.626, 5.609]
    fmax = [65.04, 69.49]

    x2 = np.arange(len(platforms))
    w2 = 0.35

    # Left axis: Setup Slack
    bars_slack = ax2.bar(x2 - w2/2, setup_slack, w2, label='Worst Setup Slack (+ns @ 50MHz)', color='#43a047', edgecolor='#1b5e20', linewidth=1.2)
    ax2.set_ylabel('Worst Setup Slack (ns)', fontsize=11, fontweight='bold', color='#2e7d32')
    ax2.set_ylim(0, 8.5)
    ax2.tick_params(axis='y', labelcolor='#2e7d32')

    for bar in bars_slack:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.2, f'+{yval:.3f} ns', ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#1b5e20')

    # Right axis: Fmax
    ax2_twin = ax2.twinx()
    bars_fmax = ax2_twin.bar(x2 + w2/2, fmax, w2, label='Tần Số Cực Đại Fmax (MHz)', color='#ab47bc', edgecolor='#4a148c', linewidth=1.2)
    ax2_twin.set_ylabel('Tần Số Cực Đại Fmax (MHz)', fontsize=11, fontweight='bold', color='#6a1b9a')
    ax2_twin.set_ylim(0, 95)
    ax2_twin.tick_params(axis='y', labelcolor='#6a1b9a')
    ax2_twin.grid(False) # avoid overlapping gridlines

    # Target 50MHz line
    ax2_twin.axhline(50.0, color='#d32f2f', linestyle=':', linewidth=1.5, label='Xung nhịp danh định (50 MHz)')

    for bar, fm in zip(bars_fmax, fmax):
        yval = bar.get_height()
        ax2_twin.text(bar.get_x() + bar.get_width()/2.0, yval + 1.5, f'{fm:.2f} MHz', ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#4a148c')

    ax2.set_xticks(x2)
    ax2.set_xticklabels(platforms, fontsize=10, fontweight='bold')
    
    # Clean Title including TNS status (Eliminating colliding badge!)
    ax2.set_title('Phân Tích Đóng Thời Gian Tĩnh (STA @ 50 MHz)\n[ TNS = 0.000 ns — Đóng Timing An Toàn 100% ]',
                  fontsize=11.5, fontweight='bold', pad=12, color='#1b5e20')

    # Combined Legend at top-left
    handles1, labels1 = ax2.get_legend_handles_labels()
    handles2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(handles1 + handles2, labels1 + labels2, loc='upper left', frameon=True, framealpha=0.92, fontsize=8.5)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, 'chart3_fpga_resources.png')
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Saved {out_path}")


# -----------------------------------------------------------------------------
# CHART 4: COMPUTE LATENCY SCALING VS K-DIMENSION
# -----------------------------------------------------------------------------
def plot_chart4():
    plt.figure(figsize=(9.5, 5.8), dpi=300)
    plt.gcf().patch.set_facecolor('#ffffff')

    k_values = np.array([1, 2, 4, 8, 12, 16])
    theory_lat = 22 + k_values
    gen1_lat = 85 + k_values
    gen2_lat = 29 + k_values

    plt.plot(k_values, gen1_lat, 'o--', color='#d32f2f', linewidth=2.2, markersize=8, label='Gen-1 (Đọc tuần tự 64 chu kỳ: T = 85 + K)')
    plt.plot(k_values, gen2_lat, 's-', color='#2e7d32', linewidth=2.5, markersize=8, label='Gen-2 (Đọc song song 8 Quantizers: T = 29 + K)')
    plt.plot(k_values, theory_lat, '^:', color='#1565c0', linewidth=2.0, markersize=7, label='Giới hạn lý thuyết tối thiểu (3N + K - 2: T = 22 + K)')

    # Annotate K=8
    plt.annotate(f'K=8: 93 chu kỳ\n(Gen-1)', xy=(8, 93), xytext=(9.2, 102),
                 arrowprops=dict(facecolor='#d32f2f', shrink=0.08, width=1.5, headwidth=6),
                 fontsize=9.5, fontweight='bold', color='#d32f2f')

    plt.annotate(f'K=8: 37 chu kỳ\n(Gen-2: Giảm 60.2% trễ!)', xy=(8, 37), xytext=(9.2, 48),
                 arrowprops=dict(facecolor='#2e7d32', shrink=0.08, width=1.5, headwidth=6),
                 fontsize=9.5, fontweight='bold', color='#2e7d32', bbox=dict(boxstyle='round,pad=0.3', facecolor='#e8f5e9', edgecolor='#2e7d32'))

    plt.xlabel('Chiều Sâu Nhân Ma Trận K (K-Dimension)', fontsize=11, fontweight='bold')
    plt.ylabel('Chu Kỳ Tính Toán Lõi PE (Clock Cycles)', fontsize=11, fontweight='bold')
    plt.title('Độ Trễ Tính Toán Lõi Phần Cứng Theo Chiều Sâu K (Mảng 8x8)', fontsize=12, fontweight='bold', pad=12, color='#0d47a1')
    plt.xticks(k_values, [f'K={k}' for k in k_values], fontsize=10, fontweight='bold')
    plt.ylim(15, 125)
    plt.legend(loc='upper left', frameon=True, framealpha=0.95, fontsize=9.5)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, 'chart4_latency_scaling_k.png')
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Saved {out_path}")


# -----------------------------------------------------------------------------
# CHART 5: VERIFICATION & UVM COVERAGE CLOSURE DASHBOARD
# -----------------------------------------------------------------------------
def plot_chart5():
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12.5, 9.2), dpi=300)
    fig.patch.set_facecolor('#ffffff')

    # Card 1: Unit Test Checks (61/61)
    ax1.pie([61], labels=None, colors=['#2e7d32'],
            startangle=90, wedgeprops=dict(width=0.35, edgecolor='#ffffff', linewidth=2))
    ax1.text(0, 0.08, '61 / 61', ha='center', va='center', fontsize=18, fontweight='bold', color='#2e7d32')
    ax1.text(0, -0.15, 'PASS (100%)', ha='center', va='center', fontsize=11, fontweight='bold', color='#388e3c')
    ax1.set_title('TẦNG 1: Kiểm Thử Đơn Vị\n(7 Nhóm Module RTL — 61/61 Checks PASS)', fontsize=11, fontweight='bold', color='#1b5e20')

    # Card 2: UVM 1.1c Functional Coverage (88/88 Bins)
    ax2.pie([88], labels=None, colors=['#6a1b9a'],
            startangle=90, wedgeprops=dict(width=0.35, edgecolor='#ffffff', linewidth=2))
    ax2.text(0, 0.08, '88 / 88', ha='center', va='center', fontsize=18, fontweight='bold', color='#6a1b9a')
    ax2.text(0, -0.15, 'BINS (100%)', ha='center', va='center', fontsize=11, fontweight='bold', color='#8e24aa')
    ax2.set_title('TẦNG 2: Độ Bao Phủ UVM 1.1c\n(39 Point + 49 Cross Bins Covered)', fontsize=11, fontweight='bold', color='#4a148c')

    # Card 3: PyTorch Conv1 Bit-True Activations (256/256)
    ax3.pie([256], labels=None, colors=['#0277bd'],
            startangle=90, wedgeprops=dict(width=0.35, edgecolor='#ffffff', linewidth=2))
    ax3.text(0, 0.08, '256 / 256', ha='center', va='center', fontsize=18, fontweight='bold', color='#0277bd')
    ax3.text(0, -0.15, 'BIT-TRUE (0 Err)', ha='center', va='center', fontsize=11, fontweight='bold', color='#039be5')
    ax3.set_title('TẦNG 3: Đối Soát Tầng Conv1 Thật\n(Khớp 100% Tuyệt Đối Với PyTorch Model)', fontsize=11, fontweight='bold', color='#01579b')

    # Card 4: Full MNIST Forward Classification Telemetry
    classes = [f'{i}' for i in range(10)]
    confidences = [2, 1, 3, 5, 2, 4, 3, 69, 7, 4]
    bar_colors = ['#b0bec5' if i != 7 else '#e53935' for i in range(10)]
    bars = ax4.bar(classes, confidences, color=bar_colors, edgecolor='#37474f', linewidth=1)
    ax4.set_xlabel('Lớp Chữ Số MNIST (Classes 0–9)', fontsize=9.5, fontweight='bold')
    ax4.set_ylabel('Điểm Tin Cậy Logits (%)', fontsize=9.5, fontweight='bold')
    ax4.set_title('TẦNG 3: Nhận Dạng Chữ Số Viết Tay MNIST\nDự Đoán Đúng Số 7 (Confidence 69.4%)', fontsize=11, fontweight='bold', color='#b71c1c')
    ax4.set_ylim(0, 85)
    for bar in bars:
        h = bar.get_height()
        if h >= 10:
            ax4.text(bar.get_x() + bar.get_width()/2.0, h + 2, f'{h}%', ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#b71c1c')

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, 'chart5_verification_coverage.png')
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Saved {out_path}")


def copy_to_artifacts():
    print(f"Copying generated charts to artifact directory: {ARTIFACT_DIR}")
    for name in os.listdir(OUTPUT_DIR):
        if name.endswith('.png'):
            src = os.path.join(OUTPUT_DIR, name)
            dst = os.path.join(ARTIFACT_DIR, name)
            shutil.copy(src, dst)
            print(f"  -> Copied {name} to artifact directory")


if __name__ == '__main__':
    print("Generating 5 polished, overlap-free engineering charts...")
    plot_chart1()
    plot_chart2()
    plot_chart3()
    plot_chart4()
    plot_chart5()
    copy_to_artifacts()
    print("[SUCCESS] All 5 charts regenerated, tested, and copied!")
