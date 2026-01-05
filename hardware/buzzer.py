
"""
hardware/buzzer.py - 蜂鳴器音樂控制
"""
from machine import Pin, PWM
import uasyncio

# 音階頻率表
NOTE_FREQS = {
    'C4': 262, 'D4': 294, 'E4': 330, 'F4': 349, 'G4': 392,
    'A4': 440, 'B4': 494, 'C5': 523, 'Bb4':466, 'G3': 196,
    'E5': 659, 'D#5': 622, 'D5': 587, 'Ab4': 415, 'REST': 0
}

# 小星星樂譜
NOTES_TWINKLE = [
    ('C4', 500), ('C4', 500), ('G4', 500), ('G4', 500),
    ('A4', 500), ('A4', 500), ('G4', 1000),
    ('F4', 500), ('F4', 500), ('E4', 500), ('E4', 500),
    ('D4', 500), ('D4', 500), ('C4', 1000),
]

class Buzzer:
    def __init__(self, pin_num):
        self.pwm = PWM(Pin(pin_num))
        self.pwm.duty(0)
        self.is_playing = False
        self._stop_flag = False

    def stop(self):
        """停止播放"""
        self._stop_flag = True
        self.pwm.duty(0)
        self.is_playing = False

    async def play_song(self, notes=NOTES_TWINKLE):
        """
        非同步播放歌曲
        notes: list of (note_name, duration_ms)
        """
        if self.is_playing:
            return

        self.is_playing = True
        self._stop_flag = False
        print("[Buzzer] 開始播放音樂")

        try:
            for note, duration in notes:
                if self._stop_flag:
                    break
                
                freq = NOTE_FREQS.get(note, 0)
                if freq == 0:
                    self.pwm.duty(0)
                else:
                    self.pwm.freq(freq)
                    self.pwm.duty(512) # 50% duty cycle
                
                # 每個音符之間稍微停頓，讓非同步任務切換
                await uasyncio.sleep_ms(duration)
                
                # 短暫靜音讓音符分開
                self.pwm.duty(0)
                await uasyncio.sleep_ms(20)

        except Exception as e:
            print(f"[Buzzer] 播放錯誤: {e}")
        finally:
            self.pwm.duty(0)
            self.is_playing = False
            print("[Buzzer] 播放結束")




