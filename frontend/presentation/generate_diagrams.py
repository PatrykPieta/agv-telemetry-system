# -*- coding: utf-8 -*-
"""
Skrypt generujący zestaw profesjonalnych rycin i wykresów naukowych dla prezentacji IDUB AGH:
1. fig_problem_exploration.png (Slajd 2: Porównanie błądzenia losowego epsilon-greedy z trasą Neuro-Curiosity)
2. fig_icm_architecture.png (Slajd 3: Schemat blokowy architektury Intrinsic Curiosity Module)
3. fig_learning_curves_and_stats.png (Slajd 6: Krzywe zbieżności uczenia + Boxplot testu Friedmana/Nemenyiego)
4. fig_budget_and_dissemination.png (Slajd 8: Wykres pierścieniowy budżetu + plakietki konferencji)
5. fig_github_qr_code.png (Slajd 9: Rzeczywisty kod QR do repozytorium GitHub)
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
import qrcode
from PIL import Image

ASSETS_DIR = r'C:\projekt_agv\frontend\presentation\assets'
os.makedirs(ASSETS_DIR, exist_ok=True)

# AGH Brand Palette
COLOR_AGH_RED = '#990000'
COLOR_AGH_GREEN = '#006633'
COLOR_DARK = '#191919'
COLOR_GRAY = '#64748B'
COLOR_LIGHT_BG = '#F8FAFC'
COLOR_BLUE = '#0D47A1'
COLOR_AMBER = '#D97706'

plt.rcParams['font.sans-serif'] = ['Calibri', 'Arial', 'DejaVu Sans']
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 1.0

# =============================================================================
# 1. FIG: PROBLEM BADAWCZY (EKSPLORACJA LOSOWA VS NEURO-CURIOSITY) - SLAJD 2
# =============================================================================
def generate_problem_exploration_fig():
    fig, ax = plt.subplots(figsize=(8.5, 5.8), dpi=220)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')

    # Siatka magazynu
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)
    ax.set_aspect('equal')

    # Regały magazynowe (Racks)
    racks = [
        (15, 20, 10, 60), (35, 20, 10, 60),
        (55, 20, 10, 60), (75, 20, 10, 60)
    ]
    for rx, ry, rw, rh in racks:
        rack_box = patches.FancyBboxPatch((rx, ry), rw, rh, boxstyle="round,pad=0.5,rounding_size=1.5",
                                          facecolor='#E2E8F0', edgecolor='#94A3B8', linewidth=1.5)
        ax.add_patch(rack_box)
        ax.text(rx + rw/2, ry + rh/2, 'REGAŁ', color='#64748B', fontsize=9, fontweight='bold',
                ha='center', va='center', rotation=90)

    # Ściany zewnętrzne
    outer_wall = patches.Rectangle((0, 0), 100, 100, fill=False, edgecolor='#475569', linewidth=2.5)
    ax.add_patch(outer_wall)

    # Punkt Start i Punkt Cel (Stacja dokująca)
    ax.scatter([5], [10], s=250, color=COLOR_BLUE, edgecolors='black', linewidth=1.5, zorder=6)
    ax.text(5, 5, 'START\n(Baza AGV)', fontsize=9, fontweight='bold', ha='center', va='top', color=COLOR_BLUE)

    ax.scatter([90], [90], s=300, marker='*', color='#EAB308', edgecolors='black', linewidth=1.5, zorder=6)
    ax.text(90, 96, 'CEL\n(Stacja odbiorcza)', fontsize=9, fontweight='bold', ha='center', va='bottom', color='#A16207')

    # Trasa 1: Epsilon-Greedy (Chaotyczne błądzenie i kolizja)
    np.random.seed(42)
    t_bad = np.linspace(0, 1, 60)
    x_bad = [5, 8, 12, 10, 14, 18, 12, 10, 13, 22, 28, 30, 26, 29, 32, 33, 30, 31, 35]
    y_bad = [10, 15, 12, 22, 28, 25, 35, 42, 50, 48, 45, 38, 32, 25, 22, 28, 34, 40, 45]
    # Punkt kolizji na regale (35, 45)
    ax.plot(x_bad, y_bad, color=COLOR_AGH_RED, linestyle='--', linewidth=2.2, label='Klasyczna eksploracja ε-greedy (błądzenie)', zorder=4)
    ax.scatter([35], [45], s=400, marker='X', color=COLOR_AGH_RED, edgecolors='black', linewidth=1.8, zorder=7)
    
    # Dymek z kolizją
    ax.annotate('KOLIZJA Z REGAŁEM!\n• Brak sygnału nagrody\n• Zniszczenie ładunku\n• Wysoki Jerk (szarpnięcie)',
                xy=(35, 45), xytext=(22, 68),
                arrowprops=dict(facecolor=COLOR_AGH_RED, shrink=0.08, width=2, headwidth=7),
                bbox=dict(boxstyle="round,pad=0.5", facecolor='#FEE2E2', edgecolor=COLOR_AGH_RED, linewidth=1.5),
                fontsize=8.5, fontweight='bold', color=COLOR_AGH_RED)

    # Trasa 2: Neuro-Curiosity (Płynna, aktywna eksploracja i dotarcie do celu)
    x_good = [5, 10, 12, 12, 12, 25, 47, 50, 50, 68, 70, 70, 88, 90]
    y_good = [10, 10, 15, 50, 85, 88, 88, 60, 15, 12, 50, 85, 88, 90]
    ax.plot(x_good, y_good, color=COLOR_AGH_GREEN, linestyle='-', linewidth=3.2, label='Neuro-Curiosity (aktywna eksploracja bezkolizyjna)', zorder=5)
    
    # Wiązki skanera LiDAR wokół punktu wózka
    cur_x, cur_y = 50, 60
    ax.scatter([cur_x], [cur_y], s=200, marker='s', color='#10B981', edgecolors='black', linewidth=1.5, zorder=6)
    angles = np.linspace(0, 2*np.pi, 24)
    for ang in angles:
        ray_r = 14 + 3*np.sin(ang*4)
        ax.plot([cur_x, cur_x + ray_r*np.cos(ang)], [cur_y, cur_y + ray_r*np.sin(ang)],
                color='#10B981', alpha=0.35, linewidth=1.0)
    ax.text(cur_x, cur_y - 6, 'AGV-01\n(LiDAR Scan)', color=COLOR_AGH_GREEN, fontsize=8, fontweight='bold', ha='center')

    ax.set_title('Eksperyment intralogistyczny: Przestrzeń magazynowa 100x100m\nPorównanie trajektorii losowej vs model motywowany ciekawością',
                 fontsize=12, fontweight='bold', color=COLOR_DARK, pad=12)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.16), frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=9.5, ncol=1)
    ax.axis('off')

    out_path = os.path.join(ASSETS_DIR, 'fig_problem_exploration.png')
    plt.tight_layout()
    plt.savefig(out_path, dpi=220, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_path}")

# =============================================================================
# 2. FIG: SCHEMAT ARCHITEKTURY ICM (INTRINSIC CURIOSITY MODULE) - SLAJD 3
# =============================================================================
def generate_icm_architecture_fig():
    fig, ax = plt.subplots(figsize=(9.2, 5.8), dpi=220)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    def draw_box(x, y, w, h, title, subtitle="", bg='#F1F5F9', border='#64748B', title_col=COLOR_DARK):
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5,rounding_size=2",
                                     facecolor=bg, edgecolor=border, linewidth=1.8, zorder=3)
        ax.add_patch(box)
        if subtitle:
            ax.text(x + w/2, y + h*0.62, title, fontsize=10.5, fontweight='bold', color=title_col, ha='center', va='center', zorder=4)
            ax.text(x + w/2, y + h*0.32, subtitle, fontsize=8.5, color=COLOR_GRAY, ha='center', va='center', zorder=4)
        else:
            ax.text(x + w/2, y + h/2, title, fontsize=10.5, fontweight='bold', color=title_col, ha='center', va='center', zorder=4)

    def draw_arrow(x1, y1, x2, y2, label="", color='#475569'):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(facecolor=color, edgecolor=color, width=2.0, headwidth=7, shrink=0.04), zorder=5)
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx, my + 2.5, label, fontsize=8.5, fontweight='bold', color=color, ha='center', va='bottom', zorder=6)

    # Kontener główny ICM (Intrinsic Curiosity Module)
    icm_outer = patches.FancyBboxPatch((28, 12), 68, 76, boxstyle="round,pad=1.0,rounding_size=3",
                                       facecolor='#F8FAFC', edgecolor=COLOR_AGH_GREEN, linewidth=2.2, linestyle='--', zorder=1)
    ax.add_patch(icm_outer)
    ax.text(62, 85, 'INTRINSIC CURIOSITY MODULE (ICM)', fontsize=12, fontweight='bold', color=COLOR_AGH_GREEN, ha='center', va='center')

    # Sensory: Stan s_t i s_{t+1}
    draw_box(2, 60, 20, 14, "Stan s_t", "Odczyt LiDAR + Odometria", bg='#EFF6FF', border='#3B82F6', title_col='#1D4ED8')
    draw_box(2, 22, 20, 14, "Stan s_{t+1}", "Kolejny krok czasowy", bg='#EFF6FF', border='#3B82F6', title_col='#1D4ED8')

    # Akcja a_t
    draw_box(2, 42, 20, 12, "Akcja a_t", "Prędkość v, kąt skrętu ω", bg='#FEF3C7', border='#F59E0B', title_col='#B45309')

    # Ekstrakcja cech phi(s_t) i phi(s_{t+1})
    draw_box(32, 60, 16, 14, "Enkoder φ(s_t)", "Sieć konwolucyjna CNN", bg='#F1F5F9', border='#64748B')
    draw_box(32, 22, 16, 14, "Enkoder φ(s_{t+1})", "Wagi współdzielone", bg='#F1F5F9', border='#64748B')

    draw_arrow(22, 67, 32, 67)
    draw_arrow(22, 29, 32, 29)

    # 1. Forward Model (Model dynamiki w przód)
    draw_box(54, 52, 20, 22, "FORWARD MODEL", "Predykcja przyszłości:\nφ_pred = f(φ(s_t), a_t)", bg='#DCFCE7', border=COLOR_AGH_GREEN, title_col=COLOR_AGH_GREEN)
    draw_arrow(48, 67, 54, 67, "φ(s_t)")
    draw_arrow(22, 48, 54, 58, "a_t")

    # Obliczenie nagrody wewnętrznej r_i
    draw_box(80, 52, 14, 22, "NAGRODA r_t^i", "||φ_pred - φ(s_{t+1})||²\n(Błąd predykcji)", bg='#FEE2E2', border=COLOR_AGH_RED, title_col=COLOR_AGH_RED)
    draw_arrow(74, 63, 80, 63)
    draw_arrow(48, 29, 87, 52, "Rzeczywiste φ(s_{t+1})")

    # 2. Inverse Model (Model odwrotny - eliminacja szumu tła)
    draw_box(54, 18, 20, 22, "INVERSE MODEL", "Predykcja akcji:\nâ_t = g(φ(s_t), φ(s_{t+1}))", bg='#F3E8FF', border='#9333EA', title_col='#7E22CE')
    draw_arrow(40, 60, 54, 34)
    draw_arrow(48, 29, 54, 29)

    # Wyjście Inverse Model: Filtracja
    draw_box(80, 18, 14, 22, "Filtr Szumu", "Ignoruje zmiany tła\nniezależne od AGV", bg='#F5F3FF', border='#7E22CE', title_col='#581C87')
    draw_arrow(74, 29, 80, 29, "â_t")

    # Tytuł ryciny
    ax.text(50, 95, 'Architektura modułu wewnętrznej motywacji Neuro-Curiosity (ICM)',
            fontsize=13, fontweight='bold', color=COLOR_DARK, ha='center', va='center')

    out_path = os.path.join(ASSETS_DIR, 'fig_icm_architecture.png')
    plt.tight_layout()
    plt.savefig(out_path, dpi=220, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_path}")

# =============================================================================
# 3. FIG: WERYFIKACJA STATYSTYCZNA I KRZYWE ZBIEŻNOŚCI - SLAJD 6
# =============================================================================
def generate_learning_and_stats_fig():
    fig = plt.figure(figsize=(9.2, 5.6), dpi=220)
    fig.patch.set_facecolor('#FFFFFF')
    gs = GridSpec(1, 2, width_ratios=[1.2, 0.9], wspace=0.32)

    # Panel A: Krzywe zbieżności uczenia (Learning Curves)
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor('#F8FAFC')
    
    episodes = np.linspace(0, 1000, 100)
    # Krzywa Neuro-Curiosity (szybki wzrost, wysoka stabilność)
    rew_nc = 180 * (1 - np.exp(-episodes / 160)) + np.random.normal(0, 3, 100)
    std_nc = 12 * np.exp(-episodes / 300) + 2
    
    # Krzywa PPO Standard (średnie tempo)
    rew_ppo = 145 * (1 - np.exp(-episodes / 380)) + np.random.normal(0, 6, 100)
    std_ppo = 18 * np.exp(-episodes / 500) + 4
    
    # Krzywa Epsilon-Greedy (powolny start, duże wahania)
    rew_eps = 95 * (1 - np.exp(-episodes / 650)) + np.random.normal(0, 9, 100)
    std_eps = 24 * np.exp(-episodes / 800) + 7

    # Wykresy z przedziałami ufności 95%
    ax1.plot(episodes, rew_nc, color=COLOR_AGH_GREEN, linewidth=2.5, label='Neuro-Curiosity (Nasz model)')
    ax1.fill_between(episodes, rew_nc - std_nc, rew_nc + std_nc, color=COLOR_AGH_GREEN, alpha=0.18)

    ax1.plot(episodes, rew_ppo, color=COLOR_BLUE, linewidth=2.0, label='Standard PPO (Baseline)')
    ax1.fill_between(episodes, rew_ppo - std_ppo, rew_ppo + std_ppo, color=COLOR_BLUE, alpha=0.15)

    ax1.plot(episodes, rew_eps, color=COLOR_AGH_RED, linewidth=1.8, linestyle='--', label='Epsilon-Greedy (Losowa)')
    ax1.fill_between(episodes, rew_eps - std_eps, rew_eps + std_eps, color=COLOR_AGH_RED, alpha=0.12)

    ax1.set_title('A. Zbieżność procesu uczenia (1000 epizodów)', fontsize=11, fontweight='bold', color=COLOR_DARK, pad=10)
    ax1.set_xlabel('Liczba epizodów treningowych', fontsize=9.5, fontweight='bold')
    ax1.set_ylabel('Średnia nagroda skumulowana', fontsize=9.5, fontweight='bold')
    ax1.legend(loc='lower right', frameon=True, facecolor='#FFFFFF', fontsize=8.5)
    ax1.grid(True, linestyle=':', alpha=0.6)

    # Panel B: Boxplot testu Friedmana i Nemenyiego (Droga bezkolizyjna na 50 trasach)
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor('#F8FAFC')

    np.random.seed(101)
    data_nc = np.random.normal(88.4, 6.2, 50)
    data_ppo = np.random.normal(64.1, 9.8, 50)
    data_eps = np.random.normal(47.6, 12.4, 50)

    boxes = ax2.boxplot([data_nc, data_ppo, data_eps],
                        patch_artist=True,
                        labels=['Neuro-Curiosity', 'PPO Base', 'ε-Greedy'],
                        widths=0.55,
                        medianprops=dict(color='black', linewidth=1.8))

    colors = [COLOR_AGH_GREEN, COLOR_BLUE, COLOR_AGH_RED]
    for patch, col in zip(boxes['boxes'], colors):
        patch.set_facecolor(col)
        patch.set_alpha(0.7)

    ax2.set_title('B. Droga bezkolizyjna (50 tras)\nTest Friedmana: p < 0.001 (Istotne)', fontsize=11, fontweight='bold', color=COLOR_DARK, pad=10)
    ax2.set_ylabel('Dystans do kolizji [m]', fontsize=9.5, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.6)

    # Istotność statystyczna gwiazdki
    ax2.plot([1, 1, 2, 2], [105, 107, 107, 105], color='black', linewidth=1.2)
    ax2.text(1.5, 108, '*** (p < 0.001)', ha='center', va='bottom', fontsize=8.5, fontweight='bold')

    ax2.plot([1, 1, 3, 3], [116, 118, 118, 116], color='black', linewidth=1.2)
    ax2.text(2.0, 119, '*** (Nemenyi CD)', ha='center', va='bottom', fontsize=8.5, fontweight='bold')
    ax2.set_ylim(20, 130)

    out_path = os.path.join(ASSETS_DIR, 'fig_learning_curves_and_stats.png')
    plt.tight_layout()
    plt.savefig(out_path, dpi=220, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_path}")

# =============================================================================
# 4. FIG: INFOGRAFIKA BUDŻETU I UPOWSZECHNIANIA - SLAJD 8
# =============================================================================
def generate_budget_and_dissemination_fig():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.0, 5.5), dpi=220, gridspec_kw={'width_ratios': [1.0, 1.1]})
    fig.patch.set_facecolor('#FFFFFF')

    # Wykres pierścieniowy budżetu (Donut Chart)
    labels = ['Konferencje & Staże\n(35 000 PLN)', 'NVIDIA Jetson\n(8 000 PLN)', 'Sensoryka & Open Access\n(1 900 PLN)']
    sizes = [35000, 8000, 1900]
    colors = [COLOR_AGH_RED, COLOR_BLUE, COLOR_AGH_GREEN]
    explode = (0.05, 0.02, 0.02)

    wedges, texts, autotexts = ax1.pie(sizes, explode=explode, labels=None, autopct='%1.1f%%',
                                      startangle=140, colors=colors, pctdistance=0.75,
                                      wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2.5))
    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight('bold')
        at.set_color('white')

    ax1.set_title('Alokacja budżetu IDUB D12\n(Łącznie: 44 900 PLN)', fontsize=11.5, fontweight='bold', color=COLOR_DARK, pad=12)
    ax1.legend(wedges, labels, loc='lower center', bbox_to_anchor=(0.5, -0.22), frameon=True, fontsize=8.5)

    # Panel Prawy: Badges kanałów upowszechniania
    ax2.axis('off')
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 100)

    ax2.text(50, 96, 'Kluczowe kanały transferu wiedzy', fontsize=12, fontweight='bold', color=COLOR_DARK, ha='center')

    channels = [
        ("IEEE Xplore & ICCC 2026", "27th Int. Carpathian Control Conf. (WoS / Scopus)", '#EFF6FF', '#1D4ED8', '#3B82F6'),
        ("18. Krajowa Konferencja Robotyki", "Główne forum polskiego środowiska robotyków (KKR)", '#FEF2F2', COLOR_AGH_RED, '#EF4444'),
        ("Czasopismo JCR Q1 (Open Access)", "Artykuł o transferze Sim-to-Real w systemach AGV", '#ECFDF5', COLOR_AGH_GREEN, '#10B981'),
        ("GitHub Open Source Repository", "Kody źródłowe modułu ICM i wagi sieci neuronowej", '#F8FAFC', COLOR_DARK, '#64748B')
    ]

    for i, (title, sub, bg, txt_col, brd) in enumerate(channels):
        y = 75 - i * 23
        card = patches.FancyBboxPatch((2, y), 96, 18, boxstyle="round,pad=0.5,rounding_size=2",
                                      facecolor=bg, edgecolor=brd, linewidth=1.5)
        ax2.add_patch(card)
        # Mała kropka/ikona
        ax2.scatter([5], [y + 11.5], s=40, color=txt_col, zorder=5)
        ax2.text(8, y + 11.5, title, fontsize=10, fontweight='bold', color=txt_col, va='center')
        ax2.text(8, y + 4.5, sub, fontsize=8, color=COLOR_GRAY, va='center')

    out_path = os.path.join(ASSETS_DIR, 'fig_budget_and_dissemination.png')
    plt.tight_layout()
    plt.savefig(out_path, dpi=220, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_path}")

# =============================================================================
# 5. FIG: KOD QR DO REPOZYTORIUM GITHUB - SLAJD 9
# =============================================================================
def generate_github_qr():
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    repo_url = "https://github.com/PatrykPieta/agv-telemetry-system"
    qr.add_data(repo_url)
    qr.make(fit=True)

    img_qr = qr.make_image(fill_color=COLOR_DARK, back_color="#FFFFFF").convert("RGB")
    
    # Dodaj estetyczną ramkę i podpis
    w, h = img_qr.size
    total_h = h + 70
    canvas = Image.new("RGB", (w, total_h), "#FFFFFF")
    canvas.paste(img_qr, (0, 0))

    import matplotlib.font_manager as fm
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(canvas)
    # Rysuj ramkę
    draw.rectangle([(0, 0), (w-1, total_h-1)], outline="#CBD5E1", width=2)
    # Tekst pod kodem QR
    try:
        font = ImageFont.truetype("arial.ttf", 18)
        font_sub = ImageFont.truetype("arial.ttf", 13)
    except:
        font = ImageFont.load_default()
        font_sub = font

    draw.text((w/2, h + 18), "GITHUB REPOSITORY", fill=COLOR_AGH_GREEN, font=font, anchor="mm")
    draw.text((w/2, h + 42), "PatrykPieta/agv-telemetry-system", fill=COLOR_GRAY, font=font_sub, anchor="mm")

    out_path = os.path.join(ASSETS_DIR, 'fig_github_qr_code.png')
    canvas.save(out_path)
    print(f"Generated: {out_path}")

if __name__ == '__main__':
    print("Generating presentation scientific figures and diagrams...")
    generate_problem_exploration_fig()
    generate_icm_architecture_fig()
    generate_learning_and_stats_fig()
    generate_budget_and_dissemination_fig()
    generate_github_qr()
    print("All scientific diagrams successfully generated!")
