import time
import random

class MockRPLidar:
    """
    Zaślepka (Mock) sprzętowego LiDAR-a. 
    Posiada API identyczne z oryginalną biblioteką rplidar-roboticia.
    """
    def __init__(self, port='/dev/ttyUSB0'):
        self.port = port
        print(f"[Hardware HAL] Inicjalizacja wirtualnego lasera na porcie {self.port}")

    def connect(self):
        print("[Hardware HAL] Połączono z symulowanym rotorem.")

    def disconnect(self):
        print("[Hardware HAL] Odłączono zasilanie lasera.")

    def stop(self):
        pass

    def stop_motor(self):
        pass

    def iter_measurments(self):
        """
        Główna metoda API. W oryginale czyta z kabla USB, my tutaj generujemy dane.
        Zwraca generator krotek: (new_scan, quality, angle, distance_mm)
        """
        while True:
            # 1 obrót. Zakładamy rozdzielczość 500 punktów na obrót (jak w prawdziwym C1)
            for step in range(500):
                angle = (step / 500.0) * 360.0
                
                # new_scan jest True tylko dla pierwszego punktu w nowym obrocie
                new_scan = True if step == 0 else False
                
                # 1. Generowanie tła (szum daleko od nas, np. ściany hali 5-8 metrów)
                distance_mm = random.uniform(5000, 8000)
                quality = random.randint(10, 50)

                # 2. Obiekt 1: Jasny słupek z przodu (kąt 350 do 10 stopni)
                if angle >= 350 or angle <= 10:
                    distance_mm = random.uniform(1450, 1550) # ~1.5 metra w milimetrach!
                    quality = random.randint(200, 255)       # Mocne odbicie
                
                # 3. Obiekt 2: Ciemna przeszkoda po lewej (kąt 85 do 95 stopni)
                elif 85 <= angle <= 95:
                    distance_mm = random.uniform(2150, 2250) # ~2.2 metra
                    quality = random.randint(10, 30)         # Słabe odbicie

                # Czas symulacji: żeby wypluć 500 pomiarów w 0.1s (10 Hz), 
                # każdy pomiar musi zająć 0.0002 sekundy.
                time.sleep(0.0002) 
                
                # Wypluwamy surową krotkę, DOKŁADNIE taką, jaką daje sprzęt
                yield (new_scan, quality, angle, distance_mm)