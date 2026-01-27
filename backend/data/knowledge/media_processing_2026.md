# Работа с медиа 2026

## Обработка изображений

### Python + Pillow
```python
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont
import io

# Открытие и базовые операции
img = Image.open('image.jpg')
print(f"Size: {img.size}, Mode: {img.mode}, Format: {img.format}")

# Изменение размера
resized = img.resize((800, 600), Image.Resampling.LANCZOS)
thumbnail = img.copy()
thumbnail.thumbnail((200, 200), Image.Resampling.LANCZOS)

# Обрезка
cropped = img.crop((100, 100, 500, 400))  # left, top, right, bottom

# Поворот и отражение
rotated = img.rotate(45, expand=True, fillcolor='white')
flipped_h = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
flipped_v = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

# Фильтры
blurred = img.filter(ImageFilter.GaussianBlur(radius=5))
sharpened = img.filter(ImageFilter.SHARPEN)
edges = img.filter(ImageFilter.FIND_EDGES)
emboss = img.filter(ImageFilter.EMBOSS)

# Улучшение
enhancer = ImageEnhance.Brightness(img)
brighter = enhancer.enhance(1.5)

enhancer = ImageEnhance.Contrast(img)
more_contrast = enhancer.enhance(1.3)

enhancer = ImageEnhance.Saturation(img)
saturated = enhancer.enhance(1.5)

# Конвертация форматов
img.save('output.png', 'PNG')
img.save('output.webp', 'WEBP', quality=85)
img.save('output.jpg', 'JPEG', quality=90, optimize=True)

# Работа с прозрачностью
rgba = img.convert('RGBA')
r, g, b, a = rgba.split()

# Создание изображения с нуля
new_img = Image.new('RGB', (800, 600), color='white')
draw = ImageDraw.Draw(new_img)
draw.rectangle([50, 50, 200, 150], fill='blue', outline='black')
draw.ellipse([250, 50, 400, 150], fill='red')
draw.text((50, 200), "Hello World", fill='black')

# Водяной знак
watermark = Image.open('watermark.png').convert('RGBA')
img.paste(watermark, (img.width - watermark.width - 10, img.height - watermark.height - 10), watermark)

# Batch processing
from pathlib import Path

def process_images(input_dir: str, output_dir: str, size: tuple):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for img_file in input_path.glob('*.jpg'):
        with Image.open(img_file) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(output_path / img_file.name, quality=85)
```

### OpenCV (Python)
```python
import cv2
import numpy as np

# Чтение и запись
img = cv2.imread('image.jpg')
cv2.imwrite('output.jpg', img)

# BGR to RGB (OpenCV uses BGR)
rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Изменение размера
resized = cv2.resize(img, (800, 600), interpolation=cv2.INTER_LANCZOS4)
scaled = cv2.resize(img, None, fx=0.5, fy=0.5)

# Обрезка
cropped = img[100:400, 100:500]  # [y1:y2, x1:x2]

# Фильтры
blurred = cv2.GaussianBlur(img, (15, 15), 0)
median = cv2.medianBlur(img, 5)
bilateral = cv2.bilateralFilter(img, 9, 75, 75)

# Детекция краёв
edges = cv2.Canny(gray, 100, 200)
laplacian = cv2.Laplacian(gray, cv2.CV_64F)

# Морфологические операции
kernel = np.ones((5, 5), np.uint8)
erosion = cv2.erode(img, kernel, iterations=1)
dilation = cv2.dilate(img, kernel, iterations=1)
opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

# Детекция лиц
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
for (x, y, w, h) in faces:
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

# Контуры
contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(img, contours, -1, (0, 255, 0), 2)

# Трансформации
# Поворот
center = (img.shape[1] // 2, img.shape[0] // 2)
matrix = cv2.getRotationMatrix2D(center, 45, 1.0)
rotated = cv2.warpAffine(img, matrix, (img.shape[1], img.shape[0]))

# Перспектива
pts1 = np.float32([[0, 0], [300, 0], [0, 300], [300, 300]])
pts2 = np.float32([[0, 0], [300, 0], [50, 300], [250, 300]])
matrix = cv2.getPerspectiveTransform(pts1, pts2)
warped = cv2.warpPerspective(img, matrix, (300, 300))

# Гистограмма
hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
equalized = cv2.equalizeHist(gray)

# CLAHE (адаптивная эквализация)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
cl_img = clahe.apply(gray)
```

---

## Обработка видео

### FFmpeg (командная строка)
```bash
# Информация о файле
ffprobe -v quiet -print_format json -show_format -show_streams video.mp4

# Конвертация форматов
ffmpeg -i input.mp4 output.webm
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -c:a aac output.mp4

# Изменение разрешения
ffmpeg -i input.mp4 -vf "scale=1280:720" output.mp4
ffmpeg -i input.mp4 -vf "scale=-1:720" output.mp4  # сохранить пропорции

# Обрезка видео
ffmpeg -i input.mp4 -ss 00:01:00 -t 00:00:30 output.mp4  # с 1:00, 30 секунд
ffmpeg -i input.mp4 -ss 00:01:00 -to 00:02:00 output.mp4  # с 1:00 до 2:00

# Извлечение аудио
ffmpeg -i video.mp4 -vn -acodec mp3 audio.mp3
ffmpeg -i video.mp4 -vn -acodec pcm_s16le audio.wav

# Извлечение кадров
ffmpeg -i video.mp4 -vf "fps=1" frame_%04d.jpg  # 1 кадр в секунду
ffmpeg -i video.mp4 -ss 00:00:10 -vframes 1 thumbnail.jpg  # один кадр

# Создание видео из изображений
ffmpeg -framerate 30 -pattern_type glob -i '*.jpg' -c:v libx264 output.mp4

# Добавление аудио к видео
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac output.mp4

# Наложение водяного знака
ffmpeg -i video.mp4 -i watermark.png -filter_complex "overlay=W-w-10:H-h-10" output.mp4

# Склейка видео
# Создать файл list.txt:
# file 'video1.mp4'
# file 'video2.mp4'
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4

# Ускорение/замедление
ffmpeg -i input.mp4 -filter:v "setpts=0.5*PTS" output.mp4  # 2x быстрее
ffmpeg -i input.mp4 -filter:v "setpts=2*PTS" output.mp4   # 2x медленнее

# GIF из видео
ffmpeg -i video.mp4 -vf "fps=10,scale=320:-1:flags=lanczos" output.gif

# Добавление субтитров
ffmpeg -i video.mp4 -vf "subtitles=subs.srt" output.mp4

# Стабилизация видео
ffmpeg -i shaky.mp4 -vf "vidstabdetect" -f null -
ffmpeg -i shaky.mp4 -vf "vidstabtransform" stabilized.mp4
```

### Python + MoviePy
```python
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip, TextClip,
    CompositeVideoClip, concatenate_videoclips, vfx
)

# Загрузка видео
clip = VideoFileClip("video.mp4")
print(f"Duration: {clip.duration}s, Size: {clip.size}, FPS: {clip.fps}")

# Обрезка
subclip = clip.subclip(10, 30)  # с 10 до 30 секунды

# Изменение размера
resized = clip.resize(height=720)
resized = clip.resize(0.5)  # 50% от оригинала

# Ускорение/замедление
fast = clip.fx(vfx.speedx, 2)  # 2x быстрее
slow = clip.fx(vfx.speedx, 0.5)  # 2x медленнее

# Эффекты
faded = clip.fx(vfx.fadein, 1).fx(vfx.fadeout, 1)
mirrored = clip.fx(vfx.mirror_x)
rotated = clip.rotate(90)

# Текст
txt_clip = TextClip(
    "Hello World",
    fontsize=70,
    color='white',
    font='Arial-Bold'
).set_position('center').set_duration(5)

# Композиция
final = CompositeVideoClip([clip, txt_clip])

# Склейка
clips = [VideoFileClip(f"video{i}.mp4") for i in range(1, 4)]
final = concatenate_videoclips(clips, method="compose")

# Аудио
audio = AudioFileClip("music.mp3")
clip_with_audio = clip.set_audio(audio)

# Водяной знак
logo = ImageClip("logo.png").set_duration(clip.duration)
logo = logo.resize(height=50).set_position(("right", "bottom"))
final = CompositeVideoClip([clip, logo])

# Сохранение
clip.write_videofile(
    "output.mp4",
    codec="libx264",
    audio_codec="aac",
    fps=30,
    preset="medium",
    bitrate="8000k"
)

# GIF
clip.subclip(0, 3).resize(0.3).write_gif("output.gif", fps=10)
```

---

## Обработка аудио

### FFmpeg (аудио)
```bash
# Конвертация форматов
ffmpeg -i audio.wav -acodec mp3 -ab 320k output.mp3
ffmpeg -i audio.mp3 -acodec pcm_s16le output.wav

# Изменение битрейта
ffmpeg -i input.mp3 -ab 128k output.mp3

# Обрезка аудио
ffmpeg -i input.mp3 -ss 00:00:30 -t 00:01:00 output.mp3

# Объединение аудио
ffmpeg -i "concat:audio1.mp3|audio2.mp3" -acodec copy output.mp3

# Изменение громкости
ffmpeg -i input.mp3 -af "volume=2.0" output.mp3  # 2x громче
ffmpeg -i input.mp3 -af "volume=0.5" output.mp3  # 2x тише

# Нормализация громкости
ffmpeg -i input.mp3 -af "loudnorm" output.mp3

# Удаление шума (базовое)
ffmpeg -i input.mp3 -af "highpass=f=200,lowpass=f=3000" output.mp3

# Fade in/out
ffmpeg -i input.mp3 -af "afade=t=in:st=0:d=3,afade=t=out:st=57:d=3" output.mp3

# Изменение скорости без изменения тона
ffmpeg -i input.mp3 -af "atempo=1.5" output.mp3  # 1.5x быстрее

# Изменение тона без изменения скорости
ffmpeg -i input.mp3 -af "asetrate=44100*1.25,aresample=44100" output.mp3
```

### Python + Pydub
```python
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
from pydub.silence import split_on_silence, detect_silence

# Загрузка аудио
audio = AudioSegment.from_file("audio.mp3")
print(f"Duration: {len(audio)}ms, Channels: {audio.channels}, Sample rate: {audio.frame_rate}")

# Конвертация
audio.export("output.wav", format="wav")
audio.export("output.mp3", format="mp3", bitrate="320k")

# Обрезка
segment = audio[10000:30000]  # с 10 до 30 секунды (в миллисекундах)

# Объединение
combined = audio1 + audio2
combined = audio1.append(audio2, crossfade=1000)  # с кроссфейдом

# Громкость
louder = audio + 10  # +10 dB
quieter = audio - 10  # -10 dB
normalized = normalize(audio)

# Fade
faded = audio.fade_in(2000).fade_out(2000)

# Скорость
def change_speed(audio, speed=1.0):
    return audio._spawn(audio.raw_data, overrides={
        "frame_rate": int(audio.frame_rate * speed)
    }).set_frame_rate(audio.frame_rate)

faster = change_speed(audio, 1.5)

# Реверс
reversed_audio = audio.reverse()

# Разделение по тишине
chunks = split_on_silence(
    audio,
    min_silence_len=500,
    silence_thresh=-40,
    keep_silence=200
)

# Наложение
overlay = audio.overlay(background_music, position=0)

# Стерео/моно
mono = audio.set_channels(1)
stereo = audio.set_channels(2)

# Изменение sample rate
resampled = audio.set_frame_rate(44100)
```

### Python + Librosa (анализ аудио)
```python
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

# Загрузка
y, sr = librosa.load("audio.mp3", sr=22050)
duration = librosa.get_duration(y=y, sr=sr)

# Спектрограмма
D = librosa.stft(y)
S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)

plt.figure(figsize=(12, 4))
librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='hz')
plt.colorbar(format='%+2.0f dB')
plt.savefig('spectrogram.png')

# Mel-спектрограмма
S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
S_db = librosa.power_to_db(S, ref=np.max)

# Хромаграмма
chroma = librosa.feature.chroma_stft(y=y, sr=sr)

# Темп и биты
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
beat_times = librosa.frames_to_time(beat_frames, sr=sr)

# MFCC (для распознавания речи)
mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

# Pitch tracking
pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

# Разделение на гармоники и перкуссию
y_harmonic, y_percussive = librosa.effects.hpss(y)

# Изменение тона
y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=4)

# Изменение темпа
y_stretched = librosa.effects.time_stretch(y, rate=1.5)
```

---

## Генерация контента с AI

### Генерация изображений (Stable Diffusion API)
```python
import requests
import base64
from io import BytesIO
from PIL import Image

def generate_image(prompt: str, negative_prompt: str = "", width: int = 512, height: int = 512):
    """Генерация изображения через Stable Diffusion API"""
    response = requests.post(
        "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "text_prompts": [
                {"text": prompt, "weight": 1},
                {"text": negative_prompt, "weight": -1} if negative_prompt else None,
            ],
            "cfg_scale": 7,
            "width": width,
            "height": height,
            "samples": 1,
            "steps": 30,
        }
    )
    
    data = response.json()
    image_data = base64.b64decode(data["artifacts"][0]["base64"])
    return Image.open(BytesIO(image_data))

# Использование
image = generate_image(
    prompt="A beautiful sunset over mountains, photorealistic, 8k",
    negative_prompt="blurry, low quality, distorted"
)
image.save("generated.png")
```

### Генерация аудио/речи (OpenAI TTS)
```python
from openai import OpenAI

client = OpenAI()

def text_to_speech(text: str, voice: str = "alloy", output_file: str = "speech.mp3"):
    """Генерация речи из текста"""
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice=voice,  # alloy, echo, fable, onyx, nova, shimmer
        input=text,
    )
    response.stream_to_file(output_file)

def speech_to_text(audio_file: str) -> str:
    """Транскрипция аудио в текст"""
    with open(audio_file, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
        )
    return transcript.text

# Использование
text_to_speech("Hello, this is a test of text to speech.", voice="nova")
text = speech_to_text("recording.mp3")
```

### Генерация видео (RunwayML API)
```python
import requests
import time

def generate_video(prompt: str, image_url: str = None):
    """Генерация видео через RunwayML Gen-3"""
    headers = {
        "Authorization": f"Bearer {RUNWAY_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "promptText": prompt,
        "model": "gen3a_turbo",
        "duration": 5,
        "ratio": "16:9",
    }
    
    if image_url:
        payload["promptImage"] = image_url
    
    # Создание задачи
    response = requests.post(
        "https://api.dev.runwayml.com/v1/tasks",
        headers=headers,
        json=payload
    )
    task_id = response.json()["id"]
    
    # Ожидание завершения
    while True:
        status = requests.get(
            f"https://api.dev.runwayml.com/v1/tasks/{task_id}",
            headers=headers
        ).json()
        
        if status["status"] == "SUCCEEDED":
            return status["output"][0]
        elif status["status"] == "FAILED":
            raise Exception(status["failure"])
        
        time.sleep(5)

# Использование
video_url = generate_video("A cat walking through a garden, cinematic")
```

---

## Создание контента

### Генерация текста (OpenAI)
```python
from openai import OpenAI

client = OpenAI()

def generate_article(topic: str, style: str = "informative", length: str = "medium"):
    """Генерация статьи на заданную тему"""
    length_tokens = {"short": 500, "medium": 1000, "long": 2000}
    
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": f"You are a professional content writer. Write in a {style} style."
            },
            {
                "role": "user",
                "content": f"Write a comprehensive article about: {topic}"
            }
        ],
        max_tokens=length_tokens.get(length, 1000),
        temperature=0.7,
    )
    
    return response.choices[0].message.content

def generate_social_post(topic: str, platform: str):
    """Генерация поста для социальных сетей"""
    platform_limits = {
        "twitter": 280,
        "instagram": 2200,
        "linkedin": 3000,
        "facebook": 63206,
    }
    
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": f"Create engaging {platform} post. Max {platform_limits.get(platform, 500)} characters."
            },
            {
                "role": "user",
                "content": f"Create a post about: {topic}"
            }
        ],
    )
    
    return response.choices[0].message.content

def generate_seo_content(keyword: str, content_type: str = "article"):
    """Генерация SEO-оптимизированного контента"""
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": """You are an SEO expert. Create content that:
                - Naturally includes the target keyword
                - Has proper heading structure (H1, H2, H3)
                - Includes meta description
                - Is engaging and valuable for readers
                - Follows E-E-A-T principles"""
            },
            {
                "role": "user",
                "content": f"Create SEO-optimized {content_type} for keyword: {keyword}"
            }
        ],
        max_tokens=2000,
    )
    
    return response.choices[0].message.content
```

### Создание презентаций
```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RgbColor
from pptx.enum.text import PP_ALIGN

def create_presentation(title: str, slides_data: list):
    """Создание PowerPoint презентации"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)
    
    # Титульный слайд
    title_slide = prs.slides.add_slide(prs.slide_layouts[6])
    title_box = title_slide.shapes.add_textbox(Inches(1), Inches(3), Inches(14), Inches(2))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(44)
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER
    
    # Контентные слайды
    for slide_data in slides_data:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        
        # Заголовок
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(15), Inches(1))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = slide_data["title"]
        p.font.size = Pt(32)
        p.font.bold = True
        
        # Контент
        content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(15), Inches(6))
        tf = content_box.text_frame
        for point in slide_data["points"]:
            p = tf.add_paragraph()
            p.text = f"• {point}"
            p.font.size = Pt(24)
            p.space_before = Pt(12)
        
        # Изображение (если есть)
        if "image" in slide_data:
            slide.shapes.add_picture(
                slide_data["image"],
                Inches(10), Inches(2),
                width=Inches(5)
            )
    
    prs.save(f"{title}.pptx")

# Использование
slides = [
    {
        "title": "Introduction",
        "points": ["Point 1", "Point 2", "Point 3"],
    },
    {
        "title": "Main Content",
        "points": ["Detail 1", "Detail 2"],
        "image": "chart.png"
    },
]
create_presentation("My Presentation", slides)
```

Источники: Официальная документация библиотек, OpenAI, Stability AI, 2024-2026
