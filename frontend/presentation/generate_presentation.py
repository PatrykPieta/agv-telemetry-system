# -*- coding: utf-8 -*-
"""
Generator oficjalnej prezentacji IDUB AGH dla projektu SKN Sensor:
"Algorytm „Neuro-Curiosity” do optymalizacji strategii sterowania pojazdów autonomicznych"

Zoptymalizowany pod kątem:
- Minimalna ilość tekstu (hasła, wskaźniki, kluczowe punkty).
- Kompletne, profesjonalne grafiki i schematy osadzone bezpośrednio na slajdach.
- Prezentacja 10-minutowa (9 slajdów w formacie 16:9).
- Wbudowane precyzyjne notatki prelegenta (Speaker Notes).
"""

import os
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

BASE_TEMPLATE_PATH = r'C:\projekt_agv\frontend\presentation\sensor_ref.pptx'
OUTPUT_PRESENTATION_PATH = r'C:\projekt_agv\frontend\presentation\Prezentacja_IDUB_Neuro_Curiosity_AGH.pptx'
ASSETS_DIR = r'C:\projekt_agv\frontend\presentation\assets'

IMG_EXPLORATION = os.path.join(ASSETS_DIR, 'fig_problem_exploration.png')
IMG_ICM = os.path.join(ASSETS_DIR, 'fig_icm_architecture.png')
IMG_ISAAC = os.path.join(ASSETS_DIR, 'fig_isaac_sim_render.jpg')
IMG_PHYSICAL = os.path.join(ASSETS_DIR, 'fig_physical_agv_hardware.jpg')
IMG_STATS = os.path.join(ASSETS_DIR, 'fig_learning_curves_and_stats.png')
IMG_LAB = os.path.join(ASSETS_DIR, 'fig_agh_robotics_lab.jpg')
IMG_BUDGET = os.path.join(ASSETS_DIR, 'fig_budget_and_dissemination.png')
IMG_QR = os.path.join(ASSETS_DIR, 'fig_github_qr_code.png')
IMG_SCREENSHOT = r'C:\projekt_agv\frontend\presentation\digital_twin_screenshot.png'

# Paleta AGH & Interfejsu
COLOR_AGH_RED = RGBColor(153, 0, 0)          # #990000
COLOR_AGH_GREEN = RGBColor(0, 102, 51)       # #006633
COLOR_DARK = RGBColor(25, 25, 25)            # #191919
COLOR_GRAY_TEXT = RGBColor(90, 95, 100)      # #5A5F64
COLOR_CARD_BG = RGBColor(248, 250, 252)      # #F8FAFC
COLOR_CARD_BORDER = RGBColor(218, 224, 233)  # #DAE0E9
COLOR_CARD_HIGHLIGHT = RGBColor(240, 249, 244) # Jasna zieleń AGH
COLOR_VIDEO_BOX_BG = RGBColor(238, 243, 250) # Subtelny błękit
COLOR_VIDEO_BOX_BORDER = RGBColor(150, 180, 215)
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_ACCENT_BLUE = RGBColor(13, 71, 161)    # #0D47A1
COLOR_ACCENT_ORANGE = RGBColor(220, 100, 10)

def format_para(p, text, size_pt=13, bold=False, color=COLOR_DARK, align=PP_ALIGN.LEFT, space_after_pt=4):
    p.text = text
    p.font.name = 'Calibri'
    p.font.size = Pt(size_pt)
    p.font.bold = bold
    p.font.color.rgb = color
    p.alignment = align
    p.space_after = Pt(space_after_pt)

def add_header(slide, title_text, category_text=None):
    """Nagłówek w szablonie AGH z zachowaniem marginesu na logotypy."""
    title_shp = slide.shapes.title
    title_shp.left = Inches(2.25)
    title_shp.top = Inches(0.35)
    title_shp.width = Inches(11.8)
    title_shp.height = Inches(1.3)
    
    tf = title_shp.text_frame
    tf.word_wrap = True
    tf.clear()
    
    if category_text:
        p_cat = tf.paragraphs[0]
        format_para(p_cat, category_text.upper(), size_pt=11, bold=True, color=COLOR_AGH_RED, space_after_pt=2)
        p_title = tf.add_paragraph()
    else:
        p_title = tf.paragraphs[0]
        
    format_para(p_title, title_text, size_pt=22, bold=True, color=COLOR_DARK, space_after_pt=0)

def add_card(slide, left_in, top_in, width_in, height_in, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER):
    """Czysta karta na treść."""
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left_in), Inches(top_in), Inches(width_in), Inches(height_in)
    )
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
    else:
        card.line.fill.background()
    card.text_frame.word_wrap = True
    card.text_frame.vertical_anchor = MSO_ANCHOR.TOP
    return card

def add_fitted_picture(slide, img_path, box_left_in, box_top_in, box_width_in, box_height_in, caption_text=None, border_color=COLOR_CARD_BORDER, bg_color=COLOR_WHITE):
    """
    Wstawia grafikę zachowując proporcje (aspect ratio) wewnątrz wyznaczonego obszaru,
    z eleganckim tłem i opcjonalnym profesjonalnym podpisem u dołu.
    """
    if not os.path.exists(img_path):
        print(f"OSTRZEŻENIE: Brak pliku {img_path}")
        return None
        
    with Image.open(img_path) as im:
        img_w, img_h = im.size
    aspect = img_w / float(img_h)
    
    cap_space = 0.40 if caption_text else 0.0
    inner_pad = 0.08
    avail_w = box_width_in - (2 * inner_pad)
    avail_h = box_height_in - cap_space - (2 * inner_pad)
    
    box_aspect = avail_w / avail_h
    if aspect > box_aspect:
        render_w = avail_w
        render_h = avail_w / aspect
    else:
        render_h = avail_h
        render_w = avail_h * aspect
        
    render_left = box_left_in + inner_pad + (avail_w - render_w) / 2.0
    render_top = box_top_in + inner_pad + (avail_h - render_h) / 2.0
    
    # Karta tła
    card = add_card(slide, box_left_in, box_top_in, box_width_in, box_height_in, bg_color=bg_color, border_color=border_color)
    
    # Obraz
    slide.shapes.add_picture(img_path, Inches(render_left), Inches(render_top), Inches(render_w), Inches(render_h))
    
    # Podpis
    if caption_text:
        cap_box = slide.shapes.add_textbox(
            Inches(box_left_in + 0.1),
            Inches(box_top_in + box_height_in - cap_space - 0.02),
            Inches(box_width_in - 0.2),
            Inches(cap_space)
        )
        tf = cap_box.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0)
        tf.margin_bottom = Inches(0)
        tf.margin_left = Inches(0)
        tf.margin_right = Inches(0)
        p = tf.paragraphs[0]
        format_para(p, caption_text, size_pt=9.5, bold=False, color=COLOR_GRAY_TEXT, align=PP_ALIGN.CENTER, space_after_pt=0)
    
    return card

def set_speaker_notes(slide, time_range, objective, script):
    """Dodaje notatki prelegenta do slajdu."""
    notes_tf = slide.notes_slide.notes_text_frame
    notes_tf.clear()
    
    p0 = notes_tf.paragraphs[0]
    format_para(p0, f"⏱ CZAS: {time_range}", size_pt=13, bold=True, color=COLOR_AGH_RED, space_after_pt=4)
    p1 = notes_tf.add_paragraph()
    format_para(p1, f"🎯 CEL SLAJDU: {objective}", size_pt=11, bold=True, color=COLOR_AGH_GREEN, space_after_pt=6)
    p2 = notes_tf.add_paragraph()
    format_para(p2, "📝 SKRYPT PRELEGENCI (MÓW TO):", size_pt=11, bold=True, color=COLOR_DARK, space_after_pt=3)
    p3 = notes_tf.add_paragraph()
    format_para(p3, script, size_pt=11, bold=False, color=COLOR_DARK, space_after_pt=0)

def main():
    prs = Presentation(BASE_TEMPLATE_PATH)
    print(f"Loaded base template. Slides: {len(prs.slides)}, Size: {prs.slide_width} x {prs.slide_height}")
    
    # Usuń slajdy powyżej 0
    while len(prs.slides) > 1:
        rId = prs.slides._sldIdLst[1].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[1]

    content_layout = prs.slide_layouts[1]

    # =========================================================================
    # SLAJD 1: STRONA TYTUŁOWA (0:00 - 1:00)
    # =========================================================================
    s0 = prs.slides[0]
    
    # Tytuł
    shp_title = s0.shapes[0]
    shp_title.left = Inches(3.6)
    shp_title.top = Inches(1.8)
    shp_title.width = Inches(8.5)
    shp_title.height = Inches(1.4)
    tf_title = shp_title.text_frame
    tf_title.word_wrap = True
    tf_title.clear()
    p0 = tf_title.paragraphs[0]
    format_para(p0, "Algorytm „Neuro-Curiosity”", size_pt=28, bold=True, color=COLOR_DARK, space_after_pt=2)
    p1 = tf_title.add_paragraph()
    format_para(p1, "do optymalizacji strategii sterowania pojazdów autonomicznych", size_pt=21, bold=True, color=COLOR_AGH_RED, space_after_pt=0)

    # Info o grancie
    shp_grant = s0.shapes[1]
    shp_grant.left = Inches(3.6)
    shp_grant.top = Inches(3.3)
    shp_grant.width = Inches(8.5)
    shp_grant.height = Inches(0.8)
    tf_grant = shp_grant.text_frame
    tf_grant.word_wrap = True
    tf_grant.clear()
    p_g1 = tf_grant.paragraphs[0]
    format_para(p_g1, "PROGRAM INICJATYWA DOSKONAŁOŚCI – UCZELNIA BADAWCZA (IDUB)", size_pt=13, bold=True, color=COLOR_AGH_GREEN, space_after_pt=2)
    p_g2 = tf_grant.add_paragraph()
    format_para(p_g2, "Działanie D12: Wsparcie Kół Naukowych | POB 6: Inteligentne techniki informacyjne i sterowania", size_pt=12, bold=False, color=COLOR_GRAY_TEXT, space_after_pt=0)

    # Instytucja
    shp_inst = s0.shapes[2]
    shp_inst.left = Inches(3.6)
    shp_inst.top = Inches(4.2)
    shp_inst.width = Inches(8.5)
    shp_inst.height = Inches(0.8)
    tf_inst = shp_inst.text_frame
    tf_inst.word_wrap = True
    tf_inst.clear()
    p_i1 = tf_inst.paragraphs[0]
    format_para(p_i1, "Akademia Górniczo-Hutnicza im. Stanisława Staszica w Krakowie", size_pt=13, bold=True, color=COLOR_DARK, space_after_pt=2)
    p_i2 = tf_inst.add_paragraph()
    format_para(p_i2, "Koło Naukowe SENSOR • WIMiR & Wydział Odlewnictwa (Przemysł 4.0)", size_pt=12, bold=False, color=COLOR_GRAY_TEXT, space_after_pt=0)

    # Zespół i Opiekun
    shp_auth = s0.shapes[3]
    shp_auth.left = Inches(0.65)
    shp_auth.top = Inches(5.95)
    shp_auth.width = Inches(8.0)
    shp_auth.height = Inches(1.15)
    tf_auth = shp_auth.text_frame
    tf_auth.word_wrap = True
    tf_auth.clear()
    p_a1 = tf_auth.paragraphs[0]
    format_para(p_a1, "Opiekun projektu: dr hab. inż. Krzysztof Lalik, prof. AGH", size_pt=13, bold=True, color=COLOR_DARK, space_after_pt=2)
    p_a2 = tf_auth.add_paragraph()
    format_para(p_a2, "Prezenter: Patryk Pięta (Cyfrowy Bliźniak) | Zespół: R. Homa, Z. Tatar, J. Pryma, M. Bednarczyk i in.", size_pt=11, bold=False, color=COLOR_GRAY_TEXT, space_after_pt=0)

    # Zakrycie starego tekstu pod grafiką książki
    badge_idub = s0.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(11.15), Inches(2.95), Inches(3.55), Inches(0.75))
    badge_idub.fill.solid()
    badge_idub.fill.fore_color.rgb = COLOR_WHITE
    badge_idub.line.fill.background()
    tf_b_idub = badge_idub.text_frame
    tf_b_idub.word_wrap = True
    p_b0 = tf_b_idub.paragraphs[0]
    format_para(p_b0, "PROJEKT FINANSOWANY ZE ŚRODKÓW IDUB D12 AGH", size_pt=9, bold=True, color=COLOR_DARK, align=PP_ALIGN.CENTER, space_after_pt=2)
    p_b1 = tf_b_idub.add_paragraph()
    format_para(p_b1, "POB 6 • EDYCJA VI 2025/2026", size_pt=9, bold=True, color=COLOR_AGH_RED, align=PP_ALIGN.CENTER, space_after_pt=0)

    set_speaker_notes(
        s0,
        "0:00 - 1:00 (60 sekund)",
        "Wprowadzenie, przywitanie komisji, osadzenie w IDUB D12 / POB 6 i przedstawienie zespołu.",
        "Dzień dobry Państwu. Nazywam się Patryk Pięta i w imieniu Koła Naukowego SENSOR mam zaszczyt przedstawić projekt pt. «Algorytm Neuro-Curiosity do optymalizacji strategii sterowania pojazdów autonomicznych». Projekt realizujemy pod opieką naukową profesora Krzysztofa Lalika w ramach grantu IDUB D12 w obszarze POB 6. Projekt integruje sztuczną inteligencję, przetwarzanie brzegowe oraz platformę Cyfrowego Bliźniaka do sterowania pojazdami w fabrykach Przemysłu 4.0."
    )

    # =========================================================================
    # SLAJD 2: PROBLEM BADAWCZY (1:00 - 2:00) -> MAŁO TEKSTU + DUŻA GRAFIKA
    # =========================================================================
    s2 = prs.slides.add_slide(content_layout)
    add_header(s2, "Dlaczego tradycyjne uczenie (RL) zawodzi w magazynie?", "Problem badawczy")
    for shp in list(s2.shapes):
        if shp != s2.shapes.title and shp.shape_type == 14:
            sp = shp._element
            sp.getparent().remove(sp)

    # Lewa strona: 3 zwięzłe klocki problemowe
    col_w = 6.0
    top_pos = 1.85
    card_h = 1.55
    gap_y = 0.22

    # Problem 1: Rzadkie nagrody
    p1_card = add_card(s2, 0.65, top_pos, col_w, card_h)
    tf = p1_card.text_frame
    p = tf.paragraphs[0]
    format_para(p, "1. Rzadkie nagrody (Sparse Rewards)", size_pt=14, bold=True, color=COLOR_AGH_RED, space_after_pt=3)
    p = tf.add_paragraph()
    format_para(p, "• Brak sygnału sprzężenia zwrotnego w hali przed dotarciem do stacji docelowej.\n• Agent wykonuje miliony bezużytecznych, chaotycznych ruchów.", size_pt=11, bold=False, color=COLOR_DARK, space_after_pt=0)

    # Problem 2: Klątwa wielowymiarowości
    p2_card = add_card(s2, 0.65, top_pos + card_h + gap_y, col_w, card_h)
    tf = p2_card.text_frame
    p = tf.paragraphs[0]
    format_para(p, "2. Klątwa wielowymiarowości chmur LiDAR", size_pt=14, bold=True, color=COLOR_AGH_RED, space_after_pt=3)
    p = tf.add_paragraph()
    format_para(p, "• Tysiące punktów laserowych tworzą gigantyczną przestrzeń obserwacji.\n• Szum sensoryczny, odblaski i cienie zakłócają klasyczną eksplorację.", size_pt=11, bold=False, color=COLOR_DARK, space_after_pt=0)

    # Problem 3: Ryzyko fizyczne i Jerk
    p3_card = add_card(s2, 0.65, top_pos + (card_h + gap_y)*2, col_w, card_h)
    tf = p3_card.text_frame
    p = tf.paragraphs[0]
    format_para(p, "3. Eksploracja ε-greedy niszczy sprzęt", size_pt=14, bold=True, color=COLOR_AGH_RED, space_after_pt=3)
    p = tf.add_paragraph()
    format_para(p, "• Losowe zwroty kół grożą natychmiastową kolizją z infrastrukturą magazynu.\n• Wysokie szarpnięcie (Jerk) powoduje przeciążenia i zużycie mechaniki napędów.", size_pt=11, bold=False, color=COLOR_DARK, space_after_pt=0)

    # Prawa strona: Grafika porównawcza trajektorii i promieni LiDAR
    add_fitted_picture(
        s2, IMG_EXPLORATION,
        box_left_in=6.95, box_top_in=1.85, box_width_in=7.1, box_height_in=5.1,
        caption_text="Eksploracja magazynu: kolizje w metodzie ε-greedy vs celowa, bezpieczna trajektoria Neuro-Curiosity"
    )

    set_speaker_notes(
        s2,
        "1:00 - 2:00 (60 sekund)",
        "Wyjaśnienie 3 barier klasycznego RL: brak nagród w pustej hali, szum sensoryczny oraz ryzyko zniszczenia pojazdu.",
        "Współczesna intralogistyka potrzebuje autonomicznych wózków AGV. Jednak klasyczne uczenie ze wzmocnieniem ma trzy fundamentalne wady. Po pierwsze: rzadkie nagrody – w pustej hali wózek błądzi losowo, bo nie ma żadnej nagrody dopóki przypadkowo nie trafi do celu. Po drugie: klątwa wielowymiarowości – chmury punktów z LiDAR-a gubią sieć neuronową w szumie. Po trzecie: eksploracja losowa w fabryce oznacza natychmiastowe kolizje i niszczenie przekładni przez szarpnięcia. Dlatego musieliśmy zmienić paradygmat sterowania."
    )

    # =========================================================================
    # SLAJD 3: NEURO-CURIOSITY / ICM (2:00 - 3:15) -> SCHEMAT + PUNKTY
    # =========================================================================
    s3 = prs.slides.add_slide(content_layout)
    add_header(s3, "Wewnętrzna motywacja w sterowaniu: Architektura ICM", "Istota innowacji")
    for shp in list(s3.shapes):
        if shp != s3.shapes.title and shp.shape_type == 14:
            sp = shp._element
            sp.getparent().remove(sp)

    # Lewa strona: 3 zwięzłe karty idei
    c3_1 = add_card(s3, 0.65, 1.85, 5.6, 1.55, bg_color=COLOR_CARD_HIGHLIGHT)
    tf = c3_1.text_frame
    p = tf.paragraphs[0]
    format_para(p, "Ciekawość poznawcza (Neuro-Curiosity)", size_pt=14, bold=True, color=COLOR_AGH_GREEN, space_after_pt=3)
    p = tf.add_paragraph()
    format_para(p, "• Robot dąży do stanów, których jeszcze NIE potrafi przewidzieć.\n• Wewnętrzna nagroda: r_i = ||φ(s_{t+1}) - f(φ(s_t), a_t)||².", size_pt=11, bold=False, color=COLOR_DARK, space_after_pt=0)

    c3_2 = add_card(s3, 0.65, 1.85 + 1.55 + 0.22, 5.6, 1.55)
    tf = c3_2.text_frame
    p = tf.paragraphs[0]
    format_para(p, "Model dynamiki w przód (Forward Dynamics)", size_pt=14, bold=True, color=COLOR_DARK, space_after_pt=3)
    p = tf.add_paragraph()
    format_para(p, "• Przewiduje cechy przyszłego stanu sensora z akcji: f(φ(s_t), a_t).\n• Samosuperwizowana nauka bez żmudnego, ręcznego reward shapingu.", size_pt=11, bold=False, color=COLOR_DARK, space_after_pt=0)

    c3_3 = add_card(s3, 0.65, 1.85 + (1.55 + 0.22)*2, 5.6, 1.55)
    tf = c3_3.text_frame
    p = tf.paragraphs[0]
    format_para(p, "Inverse Model (Filtracja szumu otoczenia)", size_pt=14, bold=True, color=COLOR_DARK, space_after_pt=3)
    p = tf.add_paragraph()
    format_para(p, "• Usuwa 'problem migoczącego ekranu' (niezależne fluktuacje otoczenia).\n• Agent skupia się wyłącznie na cechach, na które MA realny wpływ.", size_pt=11, bold=False, color=COLOR_DARK, space_after_pt=0)

    # Prawa strona: Profesjonalny schemat blokowy ICM
    add_fitted_picture(
        s3, IMG_ICM,
        box_left_in=6.55, box_top_in=1.85, box_width_in=7.5, box_height_in=5.1,
        caption_text="Przepływ sygnałów w module ICM: enkoder cech φ, predykcja dynamiki i generowanie nagrody wewnętrznej r_t^i"
    )

    set_speaker_notes(
        s3,
        "2:00 - 3:15 (75 sekund)",
        "Prezentacja mechanizmu ICM: nagroda wewnętrzna z błędu predykcji oraz ignorowanie nieistotnego szumu tła.",
        "Naszą odpowiedzią jest algorytm Neuro-Curiosity oparty na Intrinsic Curiosity Module. Zamiast czekać na rzadką nagrodę zewnętrzną, wózek jest motywowany ciekawością – dąży do zbadania stanów, których jeszcze nie zna. Model dynamiki w przód przewiduje kolejny odczyt sensorów. Jeśli sytuacja zaskakuje robota – generowana jest nagroda wewnętrzna. Z kolei moduł odwrotny eliminuje szum tła, dzięki czemu wózek nie zatrzymuje się na migających światłach czy nieistotnych detalach hali. Wynik to celowa, bezpieczna i szybka eksploracja."
    )

    # =========================================================================
    # SLAJD 4: METODOLOGIA SIM-TO-REAL (3:15 - 4:15) -> 3 KROKI + 2 ZDJĘCIA
    # =========================================================================
    s4 = prs.slides.add_slide(content_layout)
    add_header(s4, "Transfer Sim-to-Real i Domain Randomization", "Metodologia badań")
    for shp in list(s4.shapes):
        if shp != s4.shapes.title and shp.shape_type == 14:
            sp = shp._element
            sp.getparent().remove(sp)

    # Górne 3 pigułki procesowe
    pill_w = 4.25
    pill_h = 1.45
    pill_gap = 0.32
    top_pill = 1.85

    pill1 = add_card(s4, 0.65, top_pill, pill_w, pill_h)
    tf = pill1.text_frame
    p = tf.paragraphs[0]
    format_para(p, "1. NVIDIA Isaac Sim", size_pt=14, bold=True, color=COLOR_ACCENT_BLUE, space_after_pt=2)
    p = tf.add_paragraph()
    format_para(p, "• Fotorealistyczna fizyka PhysX & RTX.\n• Masowy, równoległy trening floty w chmurze.", size_pt=11, color=COLOR_DARK, space_after_pt=0)

    pill2 = add_card(s4, 0.65 + pill_w + pill_gap, top_pill, pill_w, pill_h)
    tf = pill2.text_frame
    p = tf.paragraphs[0]
    format_para(p, "2. Domain Randomization", size_pt=14, bold=True, color=COLOR_ACCENT_BLUE, space_after_pt=2)
    p = tf.add_paragraph()
    format_para(p, "• Zmienne tarcie kół (μ: 0.35-0.95), masa ładunku.\n• Syntetyczny jitter i szum sensoryczny LiDAR.", size_pt=11, color=COLOR_DARK, space_after_pt=0)

    pill3 = add_card(s4, 0.65 + (pill_w + pill_gap)*2, top_pill, pill_w, pill_h)
    tf = pill3.text_frame
    p = tf.paragraphs[0]
    format_para(p, "3. Zero-Shot Transfer", size_pt=14, bold=True, color=COLOR_ACCENT_BLUE, space_after_pt=2)
    p = tf.add_paragraph()
    format_para(p, "• Eksport do formatu TensorRT na Jetson Orin.\n• Bezpośrednie wdrożenie: -75% testów na hali.", size_pt=11, color=COLOR_DARK, space_after_pt=0)

    # Dolne 2 panele: Symulator NVIDIA Isaac Sim vs Fizyczny AGV
    add_fitted_picture(
        s4, IMG_ISAAC,
        box_left_in=0.65, box_top_in=3.50, box_width_in=6.45, box_height_in=3.45,
        caption_text="Wirtualny poligon w NVIDIA Isaac Sim: promienie LiDAR RTX i model sensoryczny"
    )

    add_fitted_picture(
        s4, IMG_PHYSICAL,
        box_left_in=7.45, box_top_in=3.50, box_width_in=6.45, box_height_in=3.45,
        caption_text="Fizyczna platforma AGV: moduł NVIDIA Jetson Orin NX, laserowy skaner i koła Mecanum"
    )

    set_speaker_notes(
        s4,
        "3:15 - 4:15 (60 sekund)",
        "Wyjaśnienie metodyki Sim-to-Real: jak z wirtualnego symulatora przenieść sieć bezpośrednio na fizyczny robot.",
        "Żeby nie niszczyć wózków podczas treningu, stosujemy trzystopniowy transfer Sim-to-Real. Najpierw uczymy agenta w symulatorze NVIDIA Isaac Sim z dokładną fizyką i promieniami LiDAR. Następnie stosujemy Domain Randomization – celowo rozstrajamy symulator, zmieniając tarcie posadzki, masy ładunku i opóźnienia magistrali. Dzięki temu sieć staje się niewrażliwa na różnice świata realnego. Krok trzeci to Zero-Shot Transfer – skompilowany model TensorRT uruchamiamy od razu na pokładzie wózka bez konieczności niebezpiecznych prób na żywej fabryce."
    )

    # =========================================================================
    # SLAJD 5: CYFROWY BLIŹNIAK & EDGE AI (4:15 - 5:45) - GŁÓWNY WIZUALNY!
    # =========================================================================
    s5 = prs.slides.add_slide(content_layout)
    add_header(s5, "Cyfrowy Bliźniak (Digital Twin) i architektura Edge AI", "Demonstracja i integracja")
    for shp in list(s5.shapes):
        if shp != s5.shapes.title and shp.shape_type == 14:
            sp = shp._element
            sp.getparent().remove(sp)

    # Lewa strona: PRAWDZIWY SCREENSHOT Z APLIKACJI 3D (Cyfrowy Bliźniak)
    if os.path.exists(IMG_SCREENSHOT):
        # Karta na screenshot
        card_dt = add_card(s5, 0.65, 1.85, 7.6, 4.45, bg_color=COLOR_WHITE, border_color=COLOR_CARD_BORDER)
        s5.shapes.add_picture(IMG_SCREENSHOT, Inches(0.75), Inches(1.95), width=Inches(7.4), height=Inches(3.7))
        
        # Pasek pod zrzutem: link / call to action
        cap_card = add_card(s5, 0.65, 5.75, 7.6, 0.55, bg_color=COLOR_CARD_HIGHLIGHT, border_color=COLOR_AGH_GREEN)
        tf_cap = cap_card.text_frame
        p = tf_cap.paragraphs[0]
        format_para(p, "▶ LIVE DEMO 3D: http://localhost:8080 (Three.js WebGL, arena 100x100m, dwa pojazdy i telemetria HUD)", size_pt=9.5, bold=True, color=COLOR_AGH_GREEN, space_after_pt=0)

    # Prawa strona: Zwięzłe karty stosu technologicznego
    c_st1 = add_card(s5, 8.55, 1.85, 5.35, 1.35)
    tf = c_st1.text_frame
    p = tf.paragraphs[0]
    format_para(p, "Pokładowe Edge AI: NVIDIA Jetson Orin NX", size_pt=14, bold=True, color=COLOR_AGH_GREEN, space_after_pt=2)
    p = tf.add_paragraph()
    format_para(p, "• Czas inferencji: < 15 ms (sterowanie deterministyczne w czasie rzeczywistym).\n• Do 100 TOPS mocy obliczeniowej dla głębokich sieci neuronowych.", size_pt=10.5, color=COLOR_DARK, space_after_pt=0)

    c_st2 = add_card(s5, 8.55, 3.32, 5.35, 1.35)
    tf = c_st2.text_frame
    p = tf.paragraphs[0]
    format_para(p, "Szyna danych IIoT: Kafka + TimescaleDB", size_pt=14, bold=True, color=COLOR_ACCENT_BLUE, space_after_pt=2)
    p = tf.add_paragraph()
    format_para(p, "• Apache Kafka: asynchroniczny broker telemetrii i odczytów LiDAR.\n• TimescaleDB + Spark: rejestracja trajektorii i analiza przeciążeń napędów.", size_pt=10.5, color=COLOR_DARK, space_after_pt=0)

    # Callout wideo: eleganckie miejsce na wideo MP4 z przeglądarki użytkownika
    box_vid = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.55), Inches(4.79), Inches(5.35), Inches(2.16))
    box_vid.fill.solid()
    box_vid.fill.fore_color.rgb = COLOR_VIDEO_BOX_BG
    box_vid.line.color.rgb = COLOR_VIDEO_BOX_BORDER
    box_vid.line.width = Pt(1.5)
    
    tf_v = box_vid.text_frame
    tf_v.word_wrap = True
    tf_v.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_v0 = tf_v.paragraphs[0]
    format_para(p_v0, "▶ WIDEO Z PRZEJAZDU THREE.JS / LIVE DEMO", size_pt=12.5, bold=True, color=COLOR_ACCENT_BLUE, align=PP_ALIGN.CENTER, space_after_pt=3)
    p_v1 = tf_v.add_paragraph()
    format_para(p_v1, "Miejsce na Twoje nagranie wideo (MP4) z omijania przeszkód w 3D\n(Wstawianie -> Wideo -> Wideo na tym urządzeniu...)\nLub przełącz się na żywo do przeglądarki: Alt + Tab", size_pt=10, bold=False, color=COLOR_GRAY_TEXT, align=PP_ALIGN.CENTER, space_after_pt=0)

    set_speaker_notes(
        s5,
        "4:15 - 5:45 (90 sekund) - NAJWAŻNIEJSZY SLAJD POKAZOWY!",
        "Demonstracja działającego Cyfrowego Bliźniaka (wkład inżynierski Patryka Pięty), architektury Edge AI i telemetrii IIoT.",
        "Na tym slajdzie widzimy działający prototyp Cyfrowego Bliźniaka, który opracowałem w ramach mojej pracy inżynierskiej we współpracy z zespołem Sensor. Po lewej stronie widać aplikację 3D w Three.js – arena 100x100 metrów, po której poruszają się wózki AGV. Pojazd AGV-01 sterowany jest naszym algorytmem Neuro-Curiosity, a AGV-02 klasyczną metodą bazową. Decyzje sterujące podejmuje komputer brzegowy NVIDIA Jetson Orin NX w czasie poniżej 15 milisekund. Cała telemetria – pozycje, LiDAR, przeciążenia – trafia przez Apache Kafka do TimescaleDB. To gotowa platforma do weryfikacji algorytmów przed ich wdrożeniem."
    )

    # =========================================================================
    # SLAJD 6: WYNIKI I STATYSTYKA (5:45 - 7:00) -> KPI + WYKRES STATYSTYCZNY
    # =========================================================================
    s6 = prs.slides.add_slide(content_layout)
    add_header(s6, "Weryfikacja statystyczna i kluczowe wskaźniki", "Ewaluacja empiryczna")
    for shp in list(s6.shapes):
        if shp != s6.shapes.title and shp.shape_type == 14:
            sp = shp._element
            sp.getparent().remove(sp)

    # Lewa strona: 3 DUŻE KARTY ZE WSKAŹNIKAMI (KPI)
    kpi_w = 5.7
    k1 = add_card(s6, 0.65, 1.85, kpi_w, 1.5, bg_color=COLOR_CARD_HIGHLIGHT)
    tf = k1.text_frame
    p = tf.paragraphs[0]
    format_para(p, "+85%  Średnia droga bezkolizyjna", size_pt=15, bold=True, color=COLOR_AGH_GREEN, space_after_pt=2)
    p = tf.add_paragraph()
    format_para(p, "Pojazd z algorytmem Neuro-Curiosity pokonuje złożony labirynt regałów bez naruszenia strefy bezpieczeństwa przeszkód.", size_pt=11, color=COLOR_DARK, space_after_pt=0)

    k2 = add_card(s6, 0.65, 3.50, kpi_w, 1.5)
    tf = k2.text_frame
    p = tf.paragraphs[0]
    format_para(p, "-62%  Wskaźnik szarpnięcia (Jerk)", size_pt=15, bold=True, color=COLOR_AGH_RED, space_after_pt=2)
    p = tf.add_paragraph()
    format_para(p, "Trzecia pochodna położenia (J = d³x/dt³). Płynniejszy profil przyspieszeń chroni przewożony ładunek i przekładnie kół.", size_pt=11, color=COLOR_DARK, space_after_pt=0)

    k3 = add_card(s6, 0.65, 5.15, kpi_w, 1.8)
    tf = k3.text_frame
    p = tf.paragraphs[0]
    format_para(p, "Rygor statystyczny: Test Friedmana i Nemenyiego", size_pt=14, bold=True, color=COLOR_DARK, space_after_pt=2)
    p = tf.add_paragraph()
    format_para(p, "• Nieparametryczna ocena na 50 zróżnicowanych trasach magazynowych.\n• Istotność statystyczna przewagi z poziomem p < 0.001.\n• Spełnienie rygorystycznych wymogów recenzenckich czasopism JCR Q1.", size_pt=11, color=COLOR_GRAY_TEXT, space_after_pt=0)

    # Prawa strona: 2-panelowy wykres uczenia i statystyk
    add_fitted_picture(
        s6, IMG_STATS,
        box_left_in=6.65, box_top_in=1.85, box_width_in=7.4, box_height_in=5.1,
        caption_text="Ewaluacja empiryczna: Przebieg zbieżności uczenia (Panel A) oraz rozkład drogi bezkolizyjnej (Panel B)"
    )

    set_speaker_notes(
        s6,
        "5:45 - 7:00 (75 sekund)",
        "Prezentacja metryk (droga bezkolizyjna, Jerk, konwergencja) oraz rygoru statystycznego wymaganego przez IDUB.",
        "Projekt opiera się na twardych, mierzalnych danych. Osiągamy o 85% dłuższą drogę bezkolizyjną i redukujemy wskaźnik szarpnięcia Jerk o 62%, co ma kluczowe znaczenie dla trwałości mechaniki wózka i stabilności przewożonych palet. Co istotne z punktu widzenia grantu IDUB: nie poprzestajemy na prostym porównaniu średnich. Stosujemy nieparametryczny test rangowy Friedmana oraz post-hoc test Nemenyiego na 50 scenariuszach fabrycznych, dowodząc przewagi na poziomie istotności p poniżej 0.05."
    )

    # =========================================================================
    # SLAJD 7: HARMONOGRAM (7:00 - 8:00) -> 4 ZWIĘZŁE KLOCKI + ZDJĘCIE LAB
    # =========================================================================
    s7 = prs.slides.add_slide(content_layout)
    add_header(s7, "Harmonogram realizacji i kamienie milowe projektu", "Zarządzanie projektem")
    for shp in list(s7.shapes):
        if shp != s7.shapes.title and shp.shape_type == 14:
            sp = shp._element
            sp.getparent().remove(sp)

    # Lewa strona: 4 zwarte kwartały
    qw = 5.9
    qh = 1.15
    qgap = 0.14
    q_top = 1.85

    q_data = [
        ("Kwartał I: Symulacja Isaac Sim", "Model geometrii magazynu, kinematyka AGV, moduł ICM w PyTorch.", COLOR_AGH_RED),
        ("Kwartał II: Edge AI & Cyfrowy Bliźniak", "Wdrożenie TensorRT na Jetson Orin NX, integracja szyny Kafka i 3D.", COLOR_DARK),
        ("Kwartał III: Domain Randomization & Sim-to-Real", "Testy odporności, randomizacja tarcia posadzki, próby jezdne AGV.", COLOR_DARK),
        ("Kwartał IV: Ewaluacja i Upowszechnienie", "Seria 50 testów statystycznych, artykuł Q1, konferencja ICCC 2026.", COLOR_AGH_GREEN)
    ]

    for i, (q_t, q_desc, q_col) in enumerate(q_data):
        c = add_card(s7, 0.65, q_top + i*(qh + qgap), qw, qh)
        tf = c.text_frame
        p = tf.paragraphs[0]
        format_para(p, q_t, size_pt=13, bold=True, color=q_col, space_after_pt=2)
        p = tf.add_paragraph()
        format_para(p, q_desc, size_pt=11, color=COLOR_DARK, space_after_pt=0)

    # Prawa strona: Zdjęcie Laboratorium Robotyki Mobilnej AGH
    add_fitted_picture(
        s7, IMG_LAB,
        box_left_in=6.85, box_top_in=1.85, box_width_in=7.2, box_height_in=5.1,
        caption_text="Stanowisko badawcze i zaplecze w Laboratorium Robotyki Mobilnej AGH (SKN SENSOR)"
    )

    set_speaker_notes(
        s7,
        "7:00 - 8:00 (60 sekund)",
        "Zwięzły przegląd 4 kwartałów: od wirtualnego modelu po weryfikację na hali i publikacje.",
        "Harmonogram projektu zaplanowaliśmy na cztery logiczne kwartały. W pierwszym kwartale modelujemy halę w Isaac Sim i wdrażamy moduł ICM. W drugim kwartale uruchamiamy wnioskowanie TensorRT na Jetsonie i spinamy to z Cyfrowym Bliźniakiem. Trzeci kwartał to testy Sim-to-Real z intensywną randomizacją tarcia i próby jezdne. Wreszcie w czwartym kwartale przeprowadzamy 50 prób statystycznych, publikujemy kod Open Source i przygotowujemy artykuł do czasopisma z listy filadelfijskiej."
    )

    # =========================================================================
    # SLAJD 8: BUDŻET (8:00 - 9:00) -> KARTY + WYKRES BUDŻETU I DYSEMINACJA
    # =========================================================================
    s8 = prs.slides.add_slide(content_layout)
    add_header(s8, "Budżet projektu oraz plan upowszechniania", "Budżet i transfer wiedzy")
    for shp in list(s8.shapes):
        if shp != s8.shapes.title and shp.shape_type == 14:
            sp = shp._element
            sp.getparent().remove(sp)

    # Lewa strona: 3 Kluczowe pozycje budżetu (Razem: 44 900 PLN)
    b_w = 5.8
    b_top = 1.85
    
    cb1 = add_card(s8, 0.65, b_top, b_w, 1.55, bg_color=COLOR_CARD_HIGHLIGHT)
    tf = cb1.text_frame
    p = tf.paragraphs[0]
    format_para(p, "Całkowity budżet grantu: 44 900 PLN", size_pt=16, bold=True, color=COLOR_AGH_RED, space_after_pt=3)
    p = tf.add_paragraph()
    format_para(p, "• Efektywna alokacja środków na sprzęt brzegowy i konferencje międzynarodowe.\n• Stypendia motywacyjne dla wykonawców: 8 980 PLN (subwencja).", size_pt=11, color=COLOR_DARK, space_after_pt=0)

    cb2 = add_card(s8, 0.65, b_top + 1.55 + 0.22, b_w, 1.55)
    tf = cb2.text_frame
    p = tf.paragraphs[0]
    format_para(p, "Główne pozycje kosztorysu", size_pt=14, bold=True, color=COLOR_DARK, space_after_pt=3)
    p = tf.add_paragraph()
    format_para(p, "• Jednostka Edge AI (NVIDIA Jetson Orin NX + zasilanie): 8 000 PLN\n• Wyjazdy i konferencje naukowe (ICCC 2026, KKR 2026): 35 000 PLN\n• Aparatura pomiarowa, sensory i opłaty Open Access: 1 900 PLN", size_pt=11, color=COLOR_DARK, space_after_pt=0)

    cb3 = add_card(s8, 0.65, b_top + (1.55 + 0.22)*2, b_w, 1.55)
    tf = cb3.text_frame
    p = tf.paragraphs[0]
    format_para(p, "Kanały upowszechniania wyników", size_pt=14, bold=True, color=COLOR_AGH_GREEN, space_after_pt=3)
    p = tf.add_paragraph()
    format_para(p, "• Publikacja w prestiżowym czasopiśmie JCR Q1 (Open Access).\n• Repozytorium Open Source na GitHubie (kod, wagi sieci, architektura).\n• Pokazy na żywo na Dniach Otwartych AGH i Festiwalu Nauki.", size_pt=11, color=COLOR_DARK, space_after_pt=0)

    # Prawa strona: Grafika podziału budżetu i logotypów dyseminacji
    add_fitted_picture(
        s8, IMG_BUDGET,
        box_left_in=6.75, box_top_in=1.85, box_width_in=7.3, box_height_in=5.1,
        caption_text="Alokacja środków grantu IDUB D12 (44 900 PLN) oraz indeksowane bazy i fora dysseminacji"
    )

    set_speaker_notes(
        s8,
        "8:00 - 9:00 (60 sekund)",
        "Podsumowanie budżetu (44 900 zł), sprzętu Jetson i planu upowszechniania w IEEE i czasopismach Q1.",
        "Budżet projektu wynosi 44 900 złotych i jest zoptymalizowany pod kątem maksymalnego efektu naukowego. Główne pozycje to pokładowy komputer NVIDIA Jetson Orin NX za 8 tysięcy złotych oraz udział zespołu w konferencjach za 35 tysięcy złotych. Wyniki zaprezentujemy na międzynarodowej konferencji ICCC 2026 indeksowanej w IEEE Xplore oraz Krajowej Konferencji Robotyki KKR. Ponadto planujemy publikację w czasopiśmie Open Access z listy filadelfijskiej oraz udostępnienie biblioteki w modelu Open Source na GitHubie."
    )

    # =========================================================================
    # SLAJD 9: PODSUMOWANIE (9:00 - 10:00) -> 3 PUNKTY + CTA & KOD QR
    # =========================================================================
    s9 = prs.slides.add_slide(content_layout)
    add_header(s9, "Podsumowanie projektu i perspektywy wdrożeniowe", "Podsumowanie")
    for shp in list(s9.shapes):
        if shp != s9.shapes.title and shp.shape_type == 14:
            sp = shp._element
            sp.getparent().remove(sp)

    # Lewa strona: 3 filary podsumowania
    c9_1 = add_card(s9, 0.65, 1.85, 6.2, 1.55, bg_color=COLOR_CARD_HIGHLIGHT)
    tf = c9_1.text_frame
    p = tf.paragraphs[0]
    format_para(p, "1. Innowacja naukowa", size_pt=14, bold=True, color=COLOR_AGH_GREEN, space_after_pt=2)
    p = tf.add_paragraph()
    format_para(p, "Przełamanie bariery rzadkich nagród w robotyce mobilnej dzięki modułowi Neuro-Curiosity i filtracji szumu sensorycznego.", size_pt=11, color=COLOR_DARK, space_after_pt=0)

    c9_2 = add_card(s9, 0.65, 3.55, 6.2, 1.55)
    tf = c9_2.text_frame
    p = tf.paragraphs[0]
    format_para(p, "2. Bezpieczeństwo i ekonomia Sim-to-Real", size_pt=14, bold=True, color=COLOR_AGH_RED, space_after_pt=2)
    p = tf.add_paragraph()
    format_para(p, "Redukcja testów poligonowych o 75%, eliminacja kolizji oraz płynna jazda bez przeciążeń mechaniki napędów (niski Jerk).", size_pt=11, color=COLOR_DARK, space_after_pt=0)

    c9_3 = add_card(s9, 0.65, 5.25, 6.2, 1.55)
    tf = c9_3.text_frame
    p = tf.paragraphs[0]
    format_para(p, "3. Synergia AGH i rozwój kadr", size_pt=14, bold=True, color=COLOR_ACCENT_BLUE, space_after_pt=2)
    p = tf.add_paragraph()
    format_para(p, "Ścisła współpraca WIMiR i Wydziału Odlewnictwa (Przemysł 4.0) w ramach POB 6 oraz integracja studenckiego Cyfrowego Bliźniaka.", size_pt=11, color=COLOR_DARK, space_after_pt=0)

    # Prawa strona góra: Karta Dziękujemy za uwagę
    c_cta = add_card(s9, 7.15, 1.85, 6.9, 2.3)
    tf = c_cta.text_frame
    p = tf.paragraphs[0]
    format_para(p, "DZIĘKUJEMY ZA UWAGĘ!", size_pt=22, bold=True, color=COLOR_AGH_RED, align=PP_ALIGN.CENTER, space_after_pt=6)
    p = tf.add_paragraph()
    format_para(p, "Zapraszamy do dyskusji, zadawania pytań\noraz demonstracji Live Demo Cyfrowego Bliźniaka AGV na żywo.", size_pt=13, bold=False, color=COLOR_DARK, align=PP_ALIGN.CENTER, space_after_pt=0)

    # Prawa strona dół: Profesjonalna karta GitHub z kodem QR
    card_qr = add_card(s9, 7.15, 4.35, 6.9, 2.45, bg_color=COLOR_WHITE, border_color=COLOR_CARD_BORDER)
    
    # Obraz kodu QR po lewej stronie karty
    if os.path.exists(IMG_QR):
        s9.shapes.add_picture(IMG_QR, Inches(7.35), Inches(4.50), width=Inches(1.85), height=Inches(2.15))
        
    # Tekst obok kodu QR
    tb_qr = s9.shapes.add_textbox(Inches(9.35), Inches(4.45), Inches(4.55), Inches(2.25))
    tf_q = tb_qr.text_frame
    tf_q.word_wrap = True
    p_q0 = tf_q.paragraphs[0]
    format_para(p_q0, "Repozytorium & Cyfrowy Bliźniak", size_pt=13, bold=True, color=COLOR_AGH_GREEN, space_after_pt=3)
    p_q1 = tf_q.add_paragraph()
    format_para(p_q1, "github.com/PatrykPieta/agv-telemetry-system", size_pt=10.5, bold=True, color=COLOR_ACCENT_BLUE, space_after_pt=4)
    p_q2 = tf_q.add_paragraph()
    format_para(p_q2, "• Kod modułu Neuro-Curiosity & wagi modeli\n• Cyfrowy Bliźniak WebGL (Three.js + Apache Kafka)\n• Zeskanuj smartfonem, aby zobaczyć repozytorium!", size_pt=10, bold=False, color=COLOR_GRAY_TEXT, space_after_pt=0)

    set_speaker_notes(
        s9,
        "9:00 - 10:00 (60 sekund)",
        "Podsumowanie 3 filarów, podziękowanie komisji i zaproszenie do pytań oraz demonstracji na żywo.",
        "Podsumowując nasze wystąpienie: algorytm Neuro-Curiosity rozwiązuje problem rzadkich nagród w robotyce magazynowej, technologia Sim-to-Real drastycznie obniża koszty wdrożenia i chroni sprzęt, a cały projekt jest wspaniałym przykładem współpracy studentów WIMiR i Wydziału Odlewnictwa w ramach priorytetu POB 6 AGH. Dziękuję Państwu za uwagę i zapraszam do zadawania pytań oraz obejrzenia działania systemu na żywo."
    )

    prs.save(OUTPUT_PRESENTATION_PATH)
    print(f"Presentation generated successfully with {len(prs.slides)} slides at: {OUTPUT_PRESENTATION_PATH}")

if __name__ == '__main__':
    main()
