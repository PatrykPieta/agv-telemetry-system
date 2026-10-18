# -*- coding: utf-8 -*-
"""
Generator oficjalnej prezentacji IDUB AGH dla projektu SKN Sensor:
"Algorytm „Neuro-Curiosity” do optymalizacji strategii sterowania pojazdów autonomicznych"
Format: 16:9 Widescreen, Oficjalny Szablon AGH + IDUB + KN SENSOR.
Czas trwania: 10 minut (9 slajdów) z kompletnymi notatkami prelegenta (Speaker Notes).
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

BASE_TEMPLATE_PATH = '/app/presentation/sensor_ref.pptx'
OUTPUT_PRESENTATION_PATH = '/app/presentation/Prezentacja_IDUB_Neuro_Curiosity_AGH.pptx'
SCREENSHOT_PATH = '/app/presentation/digital_twin_screenshot.png'

# AGH & Brand Palette
COLOR_AGH_RED = RGBColor(153, 0, 0)       # #990000
COLOR_AGH_GREEN = RGBColor(0, 102, 51)    # #006633
COLOR_DARK = RGBColor(25, 25, 25)         # #191919
COLOR_GRAY_TEXT = RGBColor(80, 80, 80)    # #505050
COLOR_CARD_BG = RGBColor(248, 249, 250)   # #F8F9FA
COLOR_CARD_BORDER = RGBColor(220, 224, 230)
COLOR_CARD_BG_HIGHLIGHT = RGBColor(240, 248, 243)
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_ACCENT_BLUE = RGBColor(13, 71, 161) # #0D47A1

def format_paragraph(p, text, size_pt=14, bold=False, color=COLOR_DARK, align=PP_ALIGN.LEFT, space_after_pt=4):
    p.text = text
    p.font.name = 'Calibri'
    p.font.size = Pt(size_pt)
    p.font.bold = bold
    p.font.color.rgb = color
    p.alignment = align
    p.space_after = Pt(space_after_pt)

def add_header(slide, title_text, category_text=None):
    """Sets standard title on layout 1 slides without overlapping the IDUB logo."""
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
        format_paragraph(p_cat, category_text.upper(), size_pt=11, bold=True, color=COLOR_AGH_RED, space_after_pt=2)
        p_title = tf.add_paragraph()
    else:
        p_title = tf.paragraphs[0]
        
    format_paragraph(p_title, title_text, size_pt=23, bold=True, color=COLOR_DARK, space_after_pt=0)

def add_card(slide, left_in, top_in, width_in, height_in, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER):
    """Adds a clean card box container."""
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

def set_speaker_notes(slide, time_range, objective, script):
    """Sets structured speaker notes on slide for Presenter View."""
    notes_tf = slide.notes_slide.notes_text_frame
    notes_tf.clear()
    
    p0 = notes_tf.paragraphs[0]
    format_paragraph(p0, f"⏱ CZAS: {time_range}", size_pt=13, bold=True, color=COLOR_AGH_RED, space_after_pt=4)
    
    p1 = notes_tf.add_paragraph()
    format_paragraph(p1, f"🎯 CEL SLAJDU: {objective}", size_pt=11, bold=True, color=COLOR_AGH_GREEN, space_after_pt=6)
    
    p2 = notes_tf.add_paragraph()
    format_paragraph(p2, "📝 SKRYPT WYPOWIEDZI PRELEGENCI:", size_pt=11, bold=True, color=COLOR_DARK, space_after_pt=3)
    
    p3 = notes_tf.add_paragraph()
    format_paragraph(p3, script, size_pt=11, bold=False, color=COLOR_DARK, space_after_pt=0)

def main():
    prs = Presentation(BASE_TEMPLATE_PATH)
    print(f"Loaded template with {len(prs.slides)} slides. Dimensions: {prs.slide_width} x {prs.slide_height}")
    
    # Keep slide 0 (Title slide), remove all others
    while len(prs.slides) > 1:
        rId = prs.slides._sldIdLst[1].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[1]

    content_layout = prs.slide_layouts[1]

    # =========================================================================
    # SLAJD 1: TYTUŁOWY (0:00 - 1:00)
    # =========================================================================
    s0 = prs.slides[0]
    
    # Title
    shp_title = s0.shapes[0]
    shp_title.left = Inches(3.6)
    shp_title.top = Inches(1.8)
    shp_title.width = Inches(8.5)
    shp_title.height = Inches(1.4)
    tf_title = shp_title.text_frame
    tf_title.word_wrap = True
    tf_title.clear()
    p0 = tf_title.paragraphs[0]
    format_paragraph(p0, "Algorytm „Neuro-Curiosity”", size_pt=28, bold=True, color=COLOR_DARK, space_after_pt=2)
    p1 = tf_title.add_paragraph()
    format_paragraph(p1, "do optymalizacji strategii sterowania pojazdów autonomicznych", size_pt=21, bold=True, color=COLOR_AGH_RED, space_after_pt=0)

    # Subtitle / Grant info
    shp_grant = s0.shapes[1]
    shp_grant.left = Inches(3.6)
    shp_grant.top = Inches(3.3)
    shp_grant.width = Inches(8.5)
    shp_grant.height = Inches(0.8)
    tf_grant = shp_grant.text_frame
    tf_grant.word_wrap = True
    tf_grant.clear()
    p_g1 = tf_grant.paragraphs[0]
    format_paragraph(p_g1, "PROGRAM INICJATYWA DOSKONAŁOŚCI – UCZELNIA BADAWCZA (IDUB)", size_pt=13, bold=True, color=COLOR_AGH_GREEN, space_after_pt=2)
    p_g2 = tf_grant.add_paragraph()
    format_paragraph(p_g2, "Działanie D12: Wsparcie Kół Naukowych | POB 6: Inteligentne techniki informacyjne i sterowania", size_pt=12, bold=False, color=COLOR_GRAY_TEXT, space_after_pt=0)

    # Institution
    shp_inst = s0.shapes[2]
    shp_inst.left = Inches(3.6)
    shp_inst.top = Inches(4.2)
    shp_inst.width = Inches(8.5)
    shp_inst.height = Inches(0.8)
    tf_inst = shp_inst.text_frame
    tf_inst.word_wrap = True
    tf_inst.clear()
    p_i1 = tf_inst.paragraphs[0]
    format_paragraph(p_i1, "Akademia Górniczo-Hutnicza im. Stanisława Staszica w Krakowie", size_pt=13, bold=True, color=COLOR_DARK, space_after_pt=2)
    p_i2 = tf_inst.add_paragraph()
    format_paragraph(p_i2, "Koło Naukowe SENSOR • WIMiR (Katedra Automatyzacji Procesów) & Wydział Odlewnictwa", size_pt=12, bold=False, color=COLOR_GRAY_TEXT, space_after_pt=0)

    # Team & Supervisor
    shp_auth = s0.shapes[3]
    shp_auth.left = Inches(0.65)
    shp_auth.top = Inches(5.95)
    shp_auth.width = Inches(8.0)
    shp_auth.height = Inches(1.15)
    tf_auth = shp_auth.text_frame
    tf_auth.word_wrap = True
    tf_auth.clear()
    p_a1 = tf_auth.paragraphs[0]
    format_paragraph(p_a1, "Opiekun projektu: dr hab. inż. Krzysztof Lalik, prof. AGH", size_pt=13, bold=True, color=COLOR_DARK, space_after_pt=2)
    p_a2 = tf_auth.add_paragraph()
    format_paragraph(p_a2, "Zespół projektowy: Patryk Pięta (Cyfrowy Bliźniak), Radosław Homa, Zuzanna Tatar, Jakub Pryma, Mikołaj Bednarczyk, Marcin Wandur, Adam Szulęcki, Maciej Wiszniewski, Dawid Piecuch", size_pt=11, bold=False, color=COLOR_GRAY_TEXT, space_after_pt=0)

    # Clean white badge covering legacy text on right book graphic
    badge_idub = s0.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(11.15), Inches(2.95), Inches(3.55), Inches(0.75))
    badge_idub.fill.solid()
    badge_idub.fill.fore_color.rgb = COLOR_WHITE
    badge_idub.line.fill.background()
    tf_b_idub = badge_idub.text_frame
    tf_b_idub.word_wrap = True
    p_b0 = tf_b_idub.paragraphs[0]
    format_paragraph(p_b0, "PROJEKT FINANSOWANY ZE ŚRODKÓW IDUB D12 AGH", size_pt=9, bold=True, color=COLOR_DARK, align=PP_ALIGN.CENTER, space_after_pt=2)
    p_b1 = tf_b_idub.add_paragraph()
    format_paragraph(p_b1, "POB 6 • EDYCJA VI 2025/2026", size_pt=9, bold=True, color=COLOR_AGH_RED, align=PP_ALIGN.CENTER, space_after_pt=0)

    set_speaker_notes(
        s0,
        "0:00 - 1:00 (60 sekund)",
        "Przedstawienie tematu, jednostki, zespołu SKN Sensor oraz osadzenia projektu w IDUB D12 / POB 6.",
        "Dzień dobry Państwu. Nazywam się Patryk Pięta i w imieniu Koła Naukowego SENSOR działającego przy Wydziale Inżynierii Mechanicznej i Robotyki oraz Wydziale Odlewnictwa AGH, mam zaszczyt przedstawić projekt badawczy pt. «Algorytm Neuro-Curiosity do optymalizacji strategii sterowania pojazdów autonomicznych». Projekt realizujemy pod opieką naukową dr. hab. inż. Krzysztofa Lalika w ramach grantu IDUB D12 z wpisaniem w Priorytetowy Obszar Badawczy POB 6. Nasz projekt łączy zaawansowane metody sztucznej inteligencji, brzegowe przetwarzanie Edge AI oraz platformę Cyfrowego Bliźniaka do sterowania pojazdami autonomicznymi w inteligentnych fabrykach Przemysłu 4.0."
    )

    # =========================================================================
    # SLAJD 2: PROBLEM BADAWCZY I WYZWANIA (1:00 - 2:00)
    # =========================================================================
    s2 = prs.slides.add_slide(content_layout)
    add_header(s2, "Wyzwania intralogistyki 4.0 i ograniczenia klasycznego RL", "Problem badawczy i motywacja")
    for shp in list(s2.shapes):
        if shp != s2.shapes.title and shp.shape_type == 14:
            sp = shp._element
            sp.getparent().remove(sp)

    col_w = 4.2
    gap = 0.35
    start_left = 0.65
    top_pos = 1.85
    card_h = 4.8

    # Col 1: Rzadkie nagrody
    c1 = add_card(s2, start_left, top_pos, col_w, card_h)
    tf1 = c1.text_frame
    p = tf1.paragraphs[0]
    format_paragraph(p, "1. Rzadkie nagrody (Sparse Rewards)", size_pt=16, bold=True, color=COLOR_AGH_RED, space_after_pt=12)
    items1 = [
        ("Problem błądzenia losowego:", True),
        ("W wielkopowierzchniowych magazynach nagroda pojawia się dopiero po dotarciu do stacji docelowej.", False),
        ("Brak sygnału zwrotnego:", True),
        ("Klasyczny agent RL wykonuje miliony bezużytecznych losowych ruchów w pustej przestrzeni.", False),
        ("Sztuczny reward shaping:", True),
        ("Ręczne projektowanie nagród cząstkowych prowadzi do nieoptymalnych i niebezpiecznych heurystyk.", False)
    ]
    for text, bold in items1:
        p = tf1.add_paragraph()
        format_paragraph(p, ("• " if not bold else "") + text, size_pt=13, bold=bold, color=COLOR_DARK if bold else COLOR_GRAY_TEXT, space_after_pt=6)

    # Col 2: Klątwa wielowymiarowości
    c2 = add_card(s2, start_left + col_w + gap, top_pos, col_w, card_h)
    tf2 = c2.text_frame
    p = tf2.paragraphs[0]
    format_paragraph(p, "2. Klątwa wielowymiarowości", size_pt=16, bold=True, color=COLOR_AGH_RED, space_after_pt=12)
    items2 = [
        ("Złożona percepcja sensoryczna:", True),
        ("Chmury punktów LiDAR 2D/3D oraz kamery generują gigantyczną przestrzeń stanów (high-dimensional state space).", False),
        ("Rzadkie stany użyteczne:", True),
        ("Nowe punkty pomiarowe są silnie rozproszone, co drastycznie obniża pewność decyzji sterującej.", False),
        ("Szum otoczenia:", True),
        ("Zmienne oświetlenie, odblaski i detale tła zakłócają proces uczenia standardowych sieci neuronowych.", False)
    ]
    for text, bold in items2:
        p = tf2.add_paragraph()
        format_paragraph(p, ("• " if not bold else "") + text, size_pt=13, bold=bold, color=COLOR_DARK if bold else COLOR_GRAY_TEXT, space_after_pt=6)

    # Col 3: Ryzyko sprzętowe
    c3 = add_card(s2, start_left + (col_w + gap)*2, top_pos, col_w, card_h)
    tf3 = c3.text_frame
    p = tf3.paragraphs[0]
    format_paragraph(p, "3. Eksploracja ε-greedy a sprzęt", size_pt=16, bold=True, color=COLOR_AGH_RED, space_after_pt=12)
    items3 = [
        ("Niedopuszczalne kolizje:", True),
        ("Eksploracja losowa w świecie fizycznym grozi uszkodzeniem AGV, regałów i ładunku.", False),
        ("Wysoki wskaźnik szarpnięcia (Jerk):", True),
        ("Losowe zmiany kierunku i prędkości prowadzą do przeciążeń kinematycznych i zużycia silników.", False),
        ("Bariera Sim-to-Real:", True),
        ("Polityka sterowania wytrenowana naiwnie w symulatorze zawodzi na rzeczywistym robocie przemysłowym.", False)
    ]
    for text, bold in items3:
        p = tf3.add_paragraph()
        format_paragraph(p, ("• " if not bold else "") + text, size_pt=13, bold=bold, color=COLOR_DARK if bold else COLOR_GRAY_TEXT, space_after_pt=6)

    set_speaker_notes(
        s2,
        "1:00 - 2:00 (60 sekund)",
        "Wskazanie barier klasycznego Reinforcement Learning w intralogistyce: rzadkie nagrody, wielowymiarowość i ryzyko kolizji.",
        "Przejdźmy do problemu badawczego. Nowoczesna intralogistyka wymaga wdrażania autonomicznych wózków AGV i robotów AMR w dynamicznych środowiskach magazynowych. Chcąc zoptymalizować sterowanie za pomocą uczenia ze wzmocnieniem, napotykamy na trzy kluczowe bariery. Po pierwsze: rzadkie nagrody – w dużej hali pojazd nie wie, czy jedzie dobrze, dopóki przypadkowo nie dotrze do celu. Po drugie: klątwa wielowymiarowości chmur punktów LiDAR – agent gubi się w szumie informacyjnym. Po trzecie: eksploracja losowa epsilon-greedy w świecie rzeczywistym grozi kolizjami ze sprzętem i gwałtownym szarpaniem napędów. Nasz projekt rozwiązuje te problemy u źródła."
    )

    # =========================================================================
    # SLAJD 3: ALGORYTM NEURO-CURIOSITY (2:00 - 3:15)
    # =========================================================================
    s3 = prs.slides.add_slide(content_layout)
    add_header(s3, "Wewnętrzna motywacja w sterowaniu: Architektura ICM", "Istota innowacji")
    for shp in list(s3.shapes):
        if shp != s3.shapes.title and shp.shape_type == 14:
            sp = shp._element
            sp.getparent().remove(sp)

    c_left = add_card(s3, 0.65, 1.85, 6.4, 4.8)
    tf_l = c_left.text_frame
    p = tf_l.paragraphs[0]
    format_paragraph(p, "Intrinsic Curiosity Module (ICM)", size_pt=17, bold=True, color=COLOR_AGH_GREEN, space_after_pt=10)
    t_items = [
        ("Biologiczna inspiracja:", True),
        ("Robot eksploruje środowisko motywowany ciekawością poznawczą – dąży do stanów, których jeszcze nie potrafi przewidzieć.", False),
        ("Model dynamiki w przód (Forward Dynamics):", True),
        ("Sieć neuronowa przewiduje przyszły stan sensora: s_pred = f(s_t, a_t).", False),
        ("Wewnętrzna nagroda (Intrinsic Reward):", True),
        ("Nagroda jest proporcjonalna do błędu predykcji: r_i = ||s_pred - s_{t+1}||².", False),
        ("Inverse Dynamics Model:", True),
        ("Równoczesne przewidywanie wykonanej akcji a_t eliminuje wpływ szumu tła (TV problem) i ignoruje czynniki niezależne od robota.", False)
    ]
    for text, bold in t_items:
        p = tf_l.add_paragraph()
        format_paragraph(p, ("• " if not bold else "") + text, size_pt=13, bold=bold, color=COLOR_DARK if bold else COLOR_GRAY_TEXT, space_after_pt=5)

    c_right = add_card(s3, 7.35, 1.85, 6.4, 4.8, bg_color=COLOR_CARD_BG_HIGHLIGHT)
    tf_r = c_right.text_frame
    p = tf_r.paragraphs[0]
    format_paragraph(p, "Przewagi nad metodami klasycznymi", size_pt=17, bold=True, color=COLOR_AGH_GREEN, space_after_pt=10)
    adv_items = [
        ("Całkowita eliminacja błądzenia losowego:", True),
        ("Pojazd aktywnie bada nieznane korytarze i przeszkody, szybko budując trajektorie bezkolizyjne.", False),
        ("Samosuperwizowana adaptacja:", True),
        ("Agent nie potrzebuje zewnętrznych punktów orientacyjnych ani gęstej siatki nagród.", False),
        ("Formuła łącznej nagrody:", True),
        ("R_total = R_zewnętrzna (zadanie transportowe) + beta * R_wewnętrzna (Neuro-Curiosity).", False),
        ("Odporność na dynamiczne przeszkody:", True),
        ("Pojawienie się nowej przeszkody (np. pieszy, paleta) generuje błąd predykcji, pobudzając ciekawość i bezpieczne ominięcie.", False)
    ]
    for text, bold in adv_items:
        p = tf_r.add_paragraph()
        format_paragraph(p, ("• " if not bold else "") + text, size_pt=13, bold=bold, color=COLOR_DARK if bold else COLOR_GRAY_TEXT, space_after_pt=5)

    set_speaker_notes(
        s3,
        "2:00 - 3:15 (75 sekund)",
        "Wyjaśnienie mechanizmu ICM (Forward i Inverse Model) oraz wewnętrznej motywacji w sterowaniu pojazdem AGV.",
        "Kluczową innowacją naszego projektu jest algorytm Neuro-Curiosity oparty na Intrinsic Curiosity Module. Zamiast czekać na rzadką nagrodę zewnętrzną lub błądzić losowo, agent uczy się na bazie wewnętrznego błędu predykcji. Model dynamiki w przód stara się przewidzieć, jak zmieni się odczyt sensorów po wykonaniu ruchu. Jeżeli stan jest dla pojazdu zaskakujący – pojawia się wewnętrzna nagroda motywująca do jego zbadania. Równocześnie moduł odwrotny (Inverse Model) eliminuje problem szumu tła, ignorując elementy, na które agent nie ma wpływu. Dzięki temu pojazd autonomiczny aktywnie i bezpiecznie eksploruje przestrzeń fabryczną."
    )

    # =========================================================================
    # SLAJD 4: METODOLOGIA SIM-TO-REAL (3:15 - 4:15)
    # =========================================================================
    s4 = prs.slides.add_slide(content_layout)
    add_header(s4, "Transfer wiedzy Sim-to-Real i Domain Randomization", "Metodologia badań")
    for shp in list(s4.shapes):
        if shp != s4.shapes.title and shp.shape_type == 14:
            sp = shp._element
            sp.getparent().remove(sp)

    step_w = 4.2
    s4_c1 = add_card(s4, 0.65, 1.85, step_w, 4.8)
    tf = s4_c1.text_frame
    p = tf.paragraphs[0]
    format_paragraph(p, "Krok 1: NVIDIA Isaac Sim", size_pt=16, bold=True, color=COLOR_ACCENT_BLUE, space_after_pt=10)
    for t, b in [
        ("Fotorealistyczne środowisko 3D:", True),
        ("Silnik NVIDIA PhysX oraz akceleracja RTX zapewniają wierne odwzorowanie fizyki i optyki.", False),
        ("Emulacja sensorów w czasie rzeczywistym:", True),
        ("Generowanie wiązek LiDAR 2D/3D, odczytów enkoderów, kamer RGB-D i dynamiki podwozia AGV.", False),
        ("Wielowątkowy trening masowy:", True),
        ("Tysiące wirtualnych instancji robotów trenujących równolegle w chmurze obliczeniowej.", False)
    ]:
        p = tf.add_paragraph()
        format_paragraph(p, ("• " if not b else "") + t, size_pt=13, bold=b, color=COLOR_DARK if b else COLOR_GRAY_TEXT, space_after_pt=6)

    s4_c2 = add_card(s4, 0.65 + step_w + gap, 1.85, step_w, 4.8)
    tf = s4_c2.text_frame
    p = tf.paragraphs[0]
    format_paragraph(p, "Krok 2: Domain Randomization", size_pt=16, bold=True, color=COLOR_ACCENT_BLUE, space_after_pt=10)
    for t, b in [
        ("Zwalczanie Reality Gap:", True),
        ("Sztuczne różnicowanie warunków symulacji uodparnia sieć neuronową na niedoskonałości świata realnego.", False),
        ("Parametry losowe:", True),
        ("• Współczynnik tarcia kół: mi in [0.35, 0.95]\n• Masa ładunku paletowego: +/- 30%\n• Opóźnienia magistrali komunikacyjnej (Jitter): 5-50 ms", False),
        ("Szum sensoryczny:", True),
        ("Symulacja dryfu żyroskopu, martwych stref LiDAR i zmiennego oświetlenia hali fabrycznej.", False)
    ]:
        p = tf.add_paragraph()
        format_paragraph(p, ("• " if not b else "") + t, size_pt=13, bold=b, color=COLOR_DARK if b else COLOR_GRAY_TEXT, space_after_pt=6)

    s4_c3 = add_card(s4, 0.65 + (step_w + gap)*2, 1.85, step_w, 4.8)
    tf = s4_c3.text_frame
    p = tf.paragraphs[0]
    format_paragraph(p, "Krok 3: Zero-Shot Transfer", size_pt=16, bold=True, color=COLOR_ACCENT_BLUE, space_after_pt=10)
    for t, b in [
        ("Wdrożenie na platformie brzegowej:", True),
        ("Eksport wytrenowanej polityki do formatu NVIDIA TensorRT na układzie Jetson Orin NX.", False),
        ("Bezpośredni transfer (Zero-Shot):", True),
        ("Polityka sterowania działa na fizycznym pojeździe bez konieczności niebezpiecznego dotrenowywania na hali.", False),
        ("Kluczowy rezultat:", True),
        ("Oszczędność czasu i kosztów: redukcja fizycznych testów poligonowych o ponad 75%.", False)
    ]:
        p = tf.add_paragraph()
        format_paragraph(p, ("• " if not b else "") + t, size_pt=13, bold=b, color=COLOR_DARK if b else COLOR_GRAY_TEXT, space_after_pt=6)

    set_speaker_notes(
        s4,
        "3:15 - 4:15 (60 sekund)",
        "Prezentacja metodologii Sim-to-Real: od symulacji w NVIDIA Isaac Sim przez Domain Randomization do transferu Zero-Shot.",
        "Aby bezpiecznie przenieść inteligencję z komputera na fizyczny pojazd, stosujemy metodologię Sim-to-Real. W pierwszym kroku trenujemy agenta w symulatorze NVIDIA Isaac Sim z pełną fizyką i emulacją LiDAR-a. Aby uniknąć tzw. Reality Gap – czyli rozbieżności między wirtualnym światem a halą przemysłową – stosujemy Domain Randomization. Losowo zmieniamy współczynniki tarcia posadzki, masy ładunków i opóźnienia sieciowe. W efekcie sieć neuronowa staje się tak odporna, że w trzecim kroku realizujemy transfer Zero-Shot – bezpośrednie wdrożenie na platformę pokładową NVIDIA Jetson Orin NX bez ryzyka uszkodzenia sprzętu."
    )

    # =========================================================================
    # SLAJD 5: ARCHITEKTURA EDGE AI & CYFROWY BLIŹNIAK (4:15 - 5:45) - GŁÓWNY WIZUALNY!
    # =========================================================================
    s5 = prs.slides.add_slide(content_layout)
    add_header(s5, "Cyfrowy Bliźniak (Digital Twin) i architektura Edge AI", "Demonstracja i integracja")
    for shp in list(s5.shapes):
        if shp != s5.shapes.title and shp.shape_type == 14:
            sp = shp._element
            sp.getparent().remove(sp)

    # Left: The Digital Twin Screenshot
    if os.path.exists(SCREENSHOT_PATH):
        img_left = Inches(0.65)
        img_top = Inches(1.85)
        img_w = Inches(7.6)
        img_h = Inches(4.5)
        s5.shapes.add_picture(SCREENSHOT_PATH, img_left, img_top, width=img_w, height=img_h)
        
        # Caption box under image
        cap_card = add_card(s5, 0.65, 6.45, 7.6, 0.45, bg_color=COLOR_WHITE, border_color=None)
        tf_cap = cap_card.text_frame
        p = tf_cap.paragraphs[0]
        format_paragraph(p, "Rys. 1. Stanowisko Cyfrowego Bliźniaka AGV (Three.js/WebGL): Porównanie AGV-01 (Neuro-Curiosity) oraz AGV-02 (Baseline) na arenie 100x100m z telemetrią na żywo.", size_pt=10, bold=False, color=COLOR_GRAY_TEXT, space_after_pt=0)

    # Right Card: System Architecture & IIoT Pipeline
    c_arch = add_card(s5, 8.55, 1.85, 5.2, 5.0)
    tf_a = c_arch.text_frame
    p = tf_a.paragraphs[0]
    format_paragraph(p, "Stos technologiczny platformy", size_pt=16, bold=True, color=COLOR_AGH_RED, space_after_pt=10)

    arch_points = [
        ("Edge AI – NVIDIA Jetson Orin NX:", True),
        ("Kompaktowy moduł pokładowy (do 100 TOPS AI). Autonomiczne podejmowanie decyzji w czasie <15 ms bez opóźnień chmurowych.", False),
        ("Szyna danych IIoT – Apache Kafka:", True),
        ("Wysokoprzepustowy broker zdarzeń przesyłający telemetrię pojazdów, stany LiDAR oraz metryki ciekawości.", False),
        ("Analiza i przechowywanie:", True),
        ("• TimescaleDB – hybrydowa baza szeregów czasowych\n• Apache Spark Streaming – analityka anomalii i szarpnięć", False),
        ("Wizualizacja i Nadzór Floty (Three.js & Grafana):", True),
        ("Wirtualna reprezentacja fabryki 3D, geofencing, dynamiczne wykrywanie kolizji i monitoring akumulatorów na żywo.", False),
        ("Wkład inżynierski Patryka Pięty:", True),
        ("Kompletna platforma Digital Twin integrująca modele fizyczne z algorytmami AI SKN Sensor.", False)
    ]
    for t, b in arch_points:
        p = tf_a.add_paragraph()
        format_paragraph(p, ("• " if not b else "") + t, size_pt=12, bold=b, color=COLOR_DARK if b else COLOR_GRAY_TEXT, space_after_pt=4)

    set_speaker_notes(
        s5,
        "4:15 - 5:45 (90 sekund) - KLUCZOWY PUNKT WIZUALNY!",
        "Demonstracja działającego stanowiska Cyfrowego Bliźniaka (zrzut ekranu), roli Patryka Pięty i architektury IIoT (Kafka, TimescaleDB, Spark, Jetson).",
        "Na tym slajdzie widzą Państwo kluczowy element demonstracyjny projektu – działający Cyfrowy Bliźniak floty AGV, stanowiący fundament mojej pracy inżynierskiej na Wydziale Odlewnictwa realizowanej we współpracy z SKN Sensor. Po lewej stronie widzimy trójwymiarową arenę 100x100 metrów stworzoną w Three.js, gdzie na żywo porównujemy pojazd AGV-01 sterowany algorytmem Neuro-Curiosity z pojazdem referencyjnym. Po prawej stronie przedstawiono architekturę Edge IIoT: jednostkę brzegową NVIDIA Jetson Orin NX podejmującą decyzje w czasie poniżej 15 ms, brokera Apache Kafka oraz bazę TimescaleDB i analitykę Spark Streaming. Platforma ta pozwala weryfikować zachowanie algorytmów zanim trafią na fizyczną posadzkę fabryczną."
    )

    # =========================================================================
    # SLAJD 6: BADANIA EMPIRYCZNE I WERYFIKACJA STATYSTYCZNA (5:45 - 7:00)
    # =========================================================================
    s6 = prs.slides.add_slide(content_layout)
    add_header(s6, "Badania porównawcze i rygorystyczna weryfikacja statystyczna", "Metodyka ewaluacji")
    for shp in list(s6.shapes):
        if shp != s6.shapes.title and shp.shape_type == 14:
            sp = shp._element
            sp.getparent().remove(sp)

    c_m1 = add_card(s6, 0.65, 1.85, 6.4, 4.8)
    tf_m1 = c_m1.text_frame
    p = tf_m1.paragraphs[0]
    format_paragraph(p, "Metryki efektywności i bezpieczeństwa", size_pt=17, bold=True, color=COLOR_AGH_GREEN, space_after_pt=10)
    metrics = [
        ("Średnia droga bezkolizyjna (Mean Free Path):", True),
        ("Mierzona odległość przebyta przez AGV w złożonym magazynie bez naruszenia strefy bezpieczeństwa (geofence/przeszkody).", False),
        ("Wskaźnik szarpnięcia (Jerk Metric):", True),
        ("Trzecia pochodna położenia J = d³x/dt³. Minimalizacja szarpnięć gwarantuje stabilność ładunku i wydłuża żywotność przekładni.", False),
        ("Tempo konwergencji (Convergence Rate):", True),
        ("Liczba epizodów treningowych niezbędna do osiągnięcia 98% skuteczności nawigacyjnej w nowym otoczeniu.", False),
        ("Współczynnik pokrycia przestrzeni (Coverage Ratio):", True),
        ("Procent efektywnie zmapowanego magazynu w pierwszych minutach pracy bez udziału człowieka.", False)
    ]
    for t, b in metrics:
        p = tf_m1.add_paragraph()
        format_paragraph(p, ("• " if not b else "") + t, size_pt=13, bold=b, color=COLOR_DARK if b else COLOR_GRAY_TEXT, space_after_pt=5)

    c_m2 = add_card(s6, 7.35, 1.85, 6.4, 4.8, bg_color=COLOR_CARD_BG_HIGHLIGHT)
    tf_m2 = c_m2.text_frame
    p = tf_m2.paragraphs[0]
    format_paragraph(p, "Aparatura statystyczna (Testy Friedmana i Nemenyiego)", size_pt=17, bold=True, color=COLOR_AGH_GREEN, space_after_pt=10)
    stats_pts = [
        ("Eliminacja przypadkowości wyników:", True),
        ("Proste porównanie średnich jest niewystarczające w środowiskach stochastycznych.", False),
        ("Nieparametryczny Test Friedmana:", True),
        ("Ocenia rangi efektywności porównywanych algorytmów (Neuro-Curiosity vs Epsilon-Greedy vs PPO Baseline) na wielu trasach testowych.", False),
        ("Test Post-Hoc Nemenyiego:", True),
        ("Precyzyjne wyznaczenie krytycznej różnicy (Critical Difference CD) i wskazanie, które algorytmy różnią się w sposób statystycznie istotny (p < 0.05).", False),
        ("Naukowa rzetelność publikacji:", True),
        ("Zastosowanie rygoru statystycznego spełnia najwyższe standardy recenzenckie prestiżowych czasopism z listy filadelfijskiej (JCR Q1).", False)
    ]
    for t, b in stats_pts:
        p = tf_m2.add_paragraph()
        format_paragraph(p, ("• " if not b else "") + t, size_pt=13, bold=b, color=COLOR_DARK if b else COLOR_GRAY_TEXT, space_after_pt=5)

    set_speaker_notes(
        s6,
        "5:45 - 7:00 (75 sekund)",
        "Prezentacja metryk ewaluacyjnych (droga bezkolizyjna, Jerk, konwergencja) oraz rygoru statystycznego (Test Friedmana i Nemenyiego).",
        "Projekt kładzie olbrzymi nacisk na rygor metodologiczny. Ewaluację opieramy na czterech mierzalnych wskaźnikach: drodze bezkolizyjnej, wskaźniku szarpnięcia Jerk (kluczowym dla ochrony delikatnych ładunków i mechaniki pojazdu), tempie zbieżności uczenia oraz pokryciu magazynu. Ponadto, zgodnie z wytycznymi konkursu IDUB, stosujemy rygorystyczny aparat statystyczny: nieparametryczny test Friedmana oceniający zachowanie algorytmów na wielu trasach oraz post-hoc test Nemenyiego z poziomem p < 0.05. Pozwala to jednoznacznie udowodnić recenzentom, że przewaga Neuro-Curiosity nie jest dziełem przypadku."
    )

    # =========================================================================
    # SLAJD 7: HARMONOGRAM REALIZACJI I KAMIENIE MILOWE (7:00 - 8:00)
    # =========================================================================
    s7 = prs.slides.add_slide(content_layout)
    add_header(s7, "Harmonogram realizacji i kamienie milowe projektu", "Zarządzanie projektem")
    for shp in list(s7.shapes):
        if shp != s7.shapes.title and shp.shape_type == 14:
            sp = shp._element
            sp.getparent().remove(sp)

    q_w = 6.4
    q_h = 2.35
    q_gap_x = 0.35
    q_gap_y = 0.25
    q_top1 = 1.85
    q_top2 = q_top1 + q_h + q_gap_y

    quarters = [
        (0.65, q_top1, "Kwartał I: Modelowanie i Symulacja Isaac Sim", [
            ("Kamień milowy 1:", "Implementacja modułu ICM i forward dynamics w PyTorch."),
            ("Zadanie:", "Stworzenie wirtualnej geometrii magazynu 3D oraz kinematyki AGV w NVIDIA Isaac Sim."),
            ("Rezultat:", "Wstępne wagi modelu wytrenowane w środowisku czysto symulacyjnym.")
        ]),
        (0.65 + q_w + q_gap_x, q_top1, "Kwartał II: Integracja Edge AI & Cyfrowy Bliźniak", [
            ("Kamień milowy 2:", "Uruchomienie wnioskowania TensorRT na NVIDIA Jetson Orin NX."),
            ("Zadanie:", "Integracja pipeline'u telemetrii: broker Kafka, TimescaleDB oraz wizualizacja Three.js."),
            ("Rezultat:", "Działający Digital Twin w czasie rzeczywistym z opóźnieniem <15 ms.")
        ]),
        (0.65, q_top2, "Kwartał III: Domain Randomization i Sim-to-Real", [
            ("Kamień milowy 3:", "Testy zero-shot transfer na fizycznej platformie jezdnej."),
            ("Zadanie:", "Wprowadzenie losowości tarcia, oświetlenia i opóźnień w symulatorze."),
            ("Rezultat:", "Potwierdzenie odporności algorytmu na warunki rzeczywiste bez kolizji.")
        ]),
        (0.65 + q_w + q_gap_x, q_top2, "Kwartał IV: Ewaluacja Statystyczna i Upowszechnienie", [
            ("Kamień milowy 4:", "Raport badawczy, artykuł Q1 i wystąpienie konferencyjne."),
            ("Zadanie:", "Wykonanie testów Friedmana/Nemenyiego na 50 scenariuszach fabrycznych."),
            ("Rezultat:", "Prezentacja na ICCC 2026 i KKR oraz publikacja repozytorium GitHub Open Source.")
        ])
    ]

    for q_left, q_top, q_title, q_items in quarters:
        card = add_card(s7, q_left, q_top, q_w, q_h)
        tf_q = card.text_frame
        p = tf_q.paragraphs[0]
        format_paragraph(p, q_title, size_pt=15, bold=True, color=COLOR_AGH_RED, space_after_pt=6)
        for label, val in q_items:
            p = tf_q.add_paragraph()
            p.text = f"• {label} {val}"
            p.font.name = 'Calibri'
            p.font.size = Pt(12)
            p.font.color.rgb = COLOR_DARK
            p.space_after = Pt(3)

    set_speaker_notes(
        s7,
        "7:00 - 8:00 (60 sekund)",
        "Omówienie 4 kwartałów realizacji grantu i konkretnych kamieni milowych od symulacji po publikacje.",
        "Harmonogram projektu podzielono na cztery logiczne kwartały. W pierwszym kwartale skupiamy się na modelowaniu geometrii w NVIDIA Isaac Sim oraz implementacji architektury ICM. W kwartale drugim optymalizujemy modele do formatu TensorRT na Jetsonie Orin NX i łączymy szynę telemetrii Cyfrowego Bliźniaka. W kwartale trzecim realizujemy transfer Sim-to-Real z intensywną Domain Randomization na stanowisku fizycznym. Wreszcie w kwartale czwartym przeprowadzamy pełną serię 50 testów statystycznych, przygotowujemy publikację naukową i udostępniamy kod w modelu Open Source."
    )

    # =========================================================================
    # SLAJD 8: BUDŻET PROJEKTU I UPOWSZECHNIANIE (8:00 - 9:00)
    # =========================================================================
    s8 = prs.slides.add_slide(content_layout)
    add_header(s8, "Budżet projektu oraz plan upowszechniania wyników", "Budżet i transfer wiedzy")
    for shp in list(s8.shapes):
        if shp != s8.shapes.title and shp.shape_type == 14:
            sp = shp._element
            sp.getparent().remove(sp)

    c_b = add_card(s8, 0.65, 1.85, 6.4, 4.8)
    tf_b = c_b.text_frame
    p = tf_b.paragraphs[0]
    format_paragraph(p, "Kosztorys grantu IDUB (Łącznie: 44 900 PLN)", size_pt=17, bold=True, color=COLOR_AGH_RED, space_after_pt=10)

    budget_rows = [
        ("1. Jednostka procesująca Edge AI:", "8 000,00 PLN", "Moduł NVIDIA Jetson Orin NX + carrier board + zasilanie przemysłowe"),
        ("2. Konferencje naukowe i delegacje:", "35 000,00 PLN", "Udział zespołu w ICCC 2026 (IEEE) oraz 18. KKR (Krajowa Konf. Robotyki)"),
        ("3. Materiały konstrukcyjne:", "500,00 PLN", "Mocowania sensorów, elementy montażowe podwozia AGV"),
        ("4. Oprzyrządowanie elektroniczne:", "500,00 PLN", "Okablowanie CAN/Ethernet, zabezpieczenia przeciwprzepięciowe"),
        ("5. Usługi (publikacje i Open Access):", "900,00 PLN", "Proofreading językowy, przygotowanie posterów naukowych"),
        ("Stypendia motywacyjne dla studentów:", "8 980,00 PLN", "Finansowane w ramach subwencji dydaktycznej jednostki")
    ]
    for cat, kw, desc in budget_rows:
        p = tf_b.add_paragraph()
        format_paragraph(p, f"• {cat}  {kw}", size_pt=13, bold=True, color=COLOR_DARK, space_after_pt=1)
        p_sub = tf_b.add_paragraph()
        format_paragraph(p_sub, f"   {desc}", size_pt=11, bold=False, color=COLOR_GRAY_TEXT, space_after_pt=5)

    c_d = add_card(s8, 7.35, 1.85, 6.4, 4.8, bg_color=COLOR_CARD_BG_HIGHLIGHT)
    tf_d = c_d.text_frame
    p = tf_d.paragraphs[0]
    format_paragraph(p, "Plan upowszechniania i wpływ na otoczenie", size_pt=17, bold=True, color=COLOR_AGH_GREEN, space_after_pt=10)

    diss_pts = [
        ("Publikacje w czasopismach JCR Q1 / Core A:", True),
        ("Artykuł podsumowujący transfer Sim-to-Real w systemach intralogistycznych w modelu Open Access.", False),
        ("Widoczność w bazach Scopus i IEEE Xplore:", True),
        ("Publikacja wyników w materiałach 27th International Carpathian Control Conference ICCC 2026.", False),
        ("Repozytorium Open Source na GitHubie:", True),
        ("Udostępnienie kodów źródłowych modułu ICM, wag modeli oraz komponentów Cyfrowego Bliźniaka dla społeczności akademickiej.", False),
        ("Promocja AGH i Dni Otwarte:", True),
        ("Demonstracja autonomicznych pojazdów AGV na żywo podczas Dni Otwartych AGH oraz Targów Organizacji Studenckich dla kandydatów na studia.", False)
    ]
    for t, b in diss_pts:
        p = tf_d.add_paragraph()
        format_paragraph(p, ("• " if not b else "") + t, size_pt=13, bold=b, color=COLOR_DARK if b else COLOR_GRAY_TEXT, space_after_pt=5)

    set_speaker_notes(
        s8,
        "8:00 - 9:00 (60 sekund)",
        "Prezentacja budżetu grantu (44 900 PLN), jednostki Jetson Orin NX, konferencji ICCC/KKR oraz planu upowszechniania.",
        "Budżet projektu wynosi 44 900 PLN i został skonstruowany w sposób wysoce efektywny kosztowo. Kluczowe pozycje to pokładowy moduł Edge AI NVIDIA Jetson Orin NX za 8 tysięcy złotych oraz udział zespołu w konferencjach naukowych za 35 tysięcy złotych. Pozwoli nam to zaprezentować wyniki na międzynarodowej konferencji ICCC 2026 indeksowanej w IEEE Xplore oraz Krajowej Konferencji Robotyki KKR. Ponadto planujemy publikację w prestiżowym czasopiśmie Open Access, udostępnienie biblioteki na GitHubie oraz prezentację działania robotów na Dniach Otwartych AGH, budując pozycję uczelni jako lidera Przemysłu 4.0."
    )

    # =========================================================================
    # SLAJD 9: PODSUMOWANIE I WNIOSKI (9:00 - 10:00)
    # =========================================================================
    s9 = prs.slides.add_slide(content_layout)
    add_header(s9, "Podsumowanie projektu i perspektywy wdrożeniowe", "Podsumowanie")
    for shp in list(s9.shapes):
        if shp != s9.shapes.title and shp.shape_type == 14:
            sp = shp._element
            sp.getparent().remove(sp)

    col_w9 = 4.2
    c9_1 = add_card(s9, start_left, top_pos, col_w9, 4.8)
    tf = c9_1.text_frame
    p = tf.paragraphs[0]
    format_paragraph(p, "Innowacja Naukowa", size_pt=17, bold=True, color=COLOR_AGH_RED, space_after_pt=12)
    for t, b in [
        ("Przełamanie barier RL:", True),
        ("Skuteczna nawigacja w środowiskach o rzadkich nagrodach bez konieczności kosztownego reward engineeringu.", False),
        ("Odporność na szum sensoryczny:", True),
        ("Moduł ICM filtruje nieistotne fluktuacje otoczenia magazynowego.", False),
        ("Wysoki potencjał publikacyjny:", True),
        ("Tematyka Deep RL i ciekawości maszynowej to jeden z najszybciej rosnących trendów wg bazy SciVal.", False)
    ]:
        p = tf.add_paragraph()
        format_paragraph(p, ("• " if not b else "") + t, size_pt=13, bold=b, color=COLOR_DARK if b else COLOR_GRAY_TEXT, space_after_pt=6)

    c9_2 = add_card(s9, start_left + col_w9 + gap, top_pos, col_w9, 4.8)
    tf = c9_2.text_frame
    p = tf.paragraphs[0]
    format_paragraph(p, "Wartość Przemysłowa", size_pt=17, bold=True, color=COLOR_AGH_GREEN, space_after_pt=12)
    for t, b in [
        ("Ekonomia wdrożenia Sim-to-Real:", True),
        ("Drastyczne obniżenie kosztów integracji autonomicznych wózków dla sektora MŚP i Przemysłu 4.0.", False),
        ("Bezpieczeństwo infrastruktury:", True),
        ("Minimalizacja wskaźnika Jerk i eliminacja losowych zderzeń chroni pojazdy i linie produkcyjne.", False),
        ("Kompaktowy Edge Computing:", True),
        ("Pełna autonomia na pokładzie AGV bez konieczności stałego łącza z chmurą.", False)
    ]:
        p = tf.add_paragraph()
        format_paragraph(p, ("• " if not b else "") + t, size_pt=13, bold=b, color=COLOR_DARK if b else COLOR_GRAY_TEXT, space_after_pt=6)

    c9_3 = add_card(s9, start_left + (col_w9 + gap)*2, top_pos, col_w9, 4.8, bg_color=COLOR_CARD_BG_HIGHLIGHT)
    tf = c9_3.text_frame
    p = tf.paragraphs[0]
    format_paragraph(p, "Integracja i Rozwój AGH", size_pt=17, bold=True, color=COLOR_ACCENT_BLUE, space_after_pt=12)
    for t, b in [
        ("Synergia wydziałowa:", True),
        ("Połączenie kompetencji WIMiR (Robotyka) oraz Wydziału Odlewnictwa (Przemysł 4.0) w ramach Priorytetowego Obszaru Badawczego POB 6.", False),
        ("Rozwój Cyfrowego Bliźniaka:", True),
        ("Praktyczne wykorzystanie platformy inżynierskiej do badań grantowych i edukacji przyszłych kadr inżynierskich AGH.", False),
        ("Dziękujemy za uwagę!", True),
        ("Zapraszamy do pytań i dyskusji.", False)
    ]:
        p = tf.add_paragraph()
        format_paragraph(p, ("• " if not b else "") + t, size_pt=13, bold=b, color=COLOR_DARK if b else COLOR_GRAY_TEXT, space_after_pt=6)

    set_speaker_notes(
        s9,
        "9:00 - 10:00 (60 sekund)",
        "Podsumowanie 3 filarów sukcesu projektu: innowacja naukowa, wartość przemysłowa i synergia wewnątrz AGH. Zaproszenie do pytań.",
        "Podsumowując nasze wystąpienie: algorytm Neuro-Curiosity rozwiązuje kluczowy problem rzadkich nagród w robotyce mobilnej. Z perspektywy przemysłowej pozwala na bezpieczny, bezkolizyjny transfer Sim-to-Real bez ryzyka zniszczenia pojazdów i ładunków. Co szczególnie ważne, projekt łączy wiedzę i zaangażowanie studentów WIMiR oraz Wydziału Odlewnictwa, integrując platformę Cyfrowego Bliźniaka z realnymi badaniami naukowymi AGH w ramach POB 6. Dziękuję bardzo Państwu za uwagę i zapraszam do zadawania pytań."
    )

    prs.save(OUTPUT_PRESENTATION_PATH)
    print(f"Successfully generated presentation with {len(prs.slides)} slides at: {OUTPUT_PRESENTATION_PATH}")

if __name__ == '__main__':
    main()
