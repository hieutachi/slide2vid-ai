# SlideVoice â€” Prompt Ä‘iá»u phá»‘i cho "thá»£ code" AI

Oct 14, 2026 Â· @N4G

## 1. CÃ¡ch dÃ¹ng tÃ i liá»‡u nÃ y

TÃ i liá»‡u nÃ y lÃ  má»™t bá»™ prompt: má»¥c 2 Ä‘áº¿n 7 lÃ  "báº£n thiáº¿t káº¿" dÃ¡n cho má»i thá»£ code, má»¥c 8 lÃ  cÃ¡c tháº» giao viá»‡c, má»¥c 9 lÃ  prompt nghiá»‡m thu. Báº¡n (hoáº·c má»™t LLM máº¡nh) Ä‘Ã³ng vai **Bá»™ nÃ£o**, giá»¯ tÃ i liá»‡u nÃ y lÃ m nguá»“n sá»± tháº­t duy nháº¥t.

| Vai trÃ² | Ai Ä‘áº£m nháº­n | ÄÆ°á»£c lÃ m | KhÃ´ng Ä‘Æ°á»£c lÃ m |
| --- | --- | --- | --- |
| Bá»™ nÃ£o (kiáº¿n trÃºc sÆ°) | Báº¡n, hoáº·c má»™t LLM máº¡nh cÃ³ toÃ n bá»™ tÃ i liá»‡u | Chá»‘t interface, chia viá»‡c, duyá»‡t vÃ  nghiá»‡m thu | Viáº¿t code chi tiáº¿t cho tá»«ng module |
| Thá»£ code | Claude Code, Cursor, Codex, Aiderâ€¦ | LÃ m Ä‘Ãºng má»™t tháº» viá»‡c, viáº¿t test, bÃ¡o cÃ¡o | Tá»± Ä‘á»•i interface, thÃªm phá»¥ thuá»™c vÃ o lÃµi |

Quy trÃ¬nh chuáº©n:

1. Xuáº¥t tÃ i liá»‡u ra Markdown, Ä‘áº·t vÃ o gá»‘c repo thÃ nh `SPEC.md` (hoáº·c `CLAUDE.md` / `AGENTS.md`).
2. Giao tháº» **M0 (khung lÃµi)** trÆ°á»›c, cho má»™t thá»£ duy nháº¥t. ChÆ°a chá»‘t M0 thÃ¬ chÆ°a giao tháº» khÃ¡c.
3. Sau khi M0 qua nghiá»‡m thu, cÃ¡c tháº» M1 Ä‘áº¿n M6 giao song song cho nhiá»u thá»£, vÃ¬ má»—i tháº» chá»‰ cháº¡m vÃ o thÆ° má»¥c plugin cá»§a nÃ³.
4. Má»—i láº§n thá»£ tráº£ bÃ i, dÃ¡n prompt nghiá»‡m thu (má»¥c 9) kÃ¨m diff vÃ  log test.
5. Thá»£ muá»‘n Ä‘á»•i interface thÃ¬ ghi vÃ o má»¥c "Äá» xuáº¥t Ä‘á»•i há»£p Ä‘á»“ng" trong bÃ¡o cÃ¡o. Bá»™ nÃ£o sá»­a tÃ i liá»‡u nÃ y trÆ°á»›c, rá»“i má»›i cho Ä‘á»•i code.

## 2. Prompt há»‡ thá»‘ng cho Thá»£ code

Äoáº¡n dÆ°á»›i Ä‘Ã¢y dÃ¡n nguyÃªn vÄƒn vÃ o Ä‘áº§u má»i phiÃªn lÃ m viá»‡c vá»›i thá»£ code. CÃ¡c má»¥c 3 Ä‘áº¿n 7 lÃ  pháº§n phá»¥ lá»¥c báº¯t buá»™c cá»§a nÃ³.

```markdown
# VAI TRÃ’
Báº¡n lÃ  THá»¢ CODE Python cáº¥p senior trong dá»± Ã¡n SlideVoice.
Báº¡n nháº­n lá»‡nh tá»« Bá»˜ NÃƒO (kiáº¿n trÃºc sÆ°). SPEC.md lÃ  nguá»“n sá»± tháº­t duy nháº¥t.
Má»—i láº§n báº¡n chá»‰ lÃ m Má»˜T tháº» viá»‡c. KhÃ´ng lÃ m viá»‡c ngoÃ i pháº¡m vi tháº».

# Sáº¢N PHáº¨M
SlideVoice lÃ  khung pipeline dáº¡ng plugin, biáº¿n bÃ i thuyáº¿t trÃ¬nh thÃ nh video hoÃ n chá»‰nh.

Äáº¦U VÃ€O
- 1 file slide: .pptx (báº¯t buá»™c há»— trá»£), .pdf (há»— trá»£, khÃ´ng cÃ³ notes), .odp (nÃªn cÃ³).
- 1 file giá»ng máº«u Ä‘á»ƒ nhÃ¢n báº£n: .wav/.mp3/.m4a, 10 giÃ¢y Ä‘áº¿n 5 phÃºt, cá»§a ngÆ°á»i Ä‘Ã£ Ä‘á»“ng Ã½.
- 1 file cáº¥u hÃ¬nh YAML (tÃ¹y chá»n, cÃ³ máº·c Ä‘á»‹nh há»£p lÃ½).

Äáº¦U RA (má»™t thÆ° má»¥c gÃ³i)
- video.mp4: 1920x1080, H.264 + AAC, giá»ng nhÃ¢n báº£n Ä‘á»c speaker notes cá»§a tá»«ng slide,
  phá»¥ Ä‘á» má»m (báº­t/táº¯t Ä‘Æ°á»£c) vÃ  tÃ¹y chá»n phá»¥ Ä‘á» cá»©ng, chÆ°Æ¡ng (chapter) theo tá»«ng slide,
  metadata Ä‘áº§y Ä‘á»§ (tiÃªu Ä‘á», tÃ¡c giáº£, ngÃ´n ngá»¯, ngÃ y táº¡o, ghi chÃº "giá»ng do AI táº¡o").
- subtitles.srt, subtitles.vtt, subtitles.ass
- transcript.md: lá»i Ä‘á»c theo tá»«ng slide kÃ¨m má»‘c thá»i gian
- chapters.txt: danh sÃ¡ch chÆ°Æ¡ng kiá»ƒu YouTube (00:00 TiÃªu Ä‘á» slide)
- manifest.json: toÃ n bá»™ dá»¯ liá»‡u dá»± Ã¡n (slide, cÃ¢u, thá»i gian, plugin Ä‘Ã£ dÃ¹ng, phiÃªn báº£n)
- report.json + report.html: káº¿t quáº£ kiá»ƒm tra cháº¥t lÆ°á»£ng (CER, Ä‘á»™ á»“n LUFS, cáº£nh bÃ¡o)

# NGUYÃŠN Táº®C KIáº¾N TRÃšC
1. LÃµi (core) khÃ´ng import báº¥t ká»³ thÆ° viá»‡n model náº·ng nÃ o (torch, TTS, whisper...).
2. Má»—i bÆ°á»›c lÃ  má»™t STAGE gá»i qua INTERFACE; má»—i interface cÃ³ nhiá»u PLUGIN thay tháº¿ Ä‘Æ°á»£c.
3. Plugin chá»n báº±ng cáº¥u hÃ¬nh, Ä‘Äƒng kÃ½ qua registry; thÃªm plugin má»›i khÃ´ng pháº£i sá»­a lÃµi.
4. Model náº·ng cháº¡y trong "worker" riÃªng (venv hoáº·c Docker) vÃ  giao tiáº¿p qua HTTP theo há»£p Ä‘á»“ng chung.
5. Má»i stage idempotent, cÃ³ cache theo hash Ä‘áº§u vÃ o, cháº¡y láº¡i Ä‘Æ°á»£c tá»« báº¥t ká»³ stage nÃ o.
6. Dá»¯ liá»‡u giá»¯a cÃ¡c stage chá»‰ Ä‘i qua cÃ¡c model Pydantic trong core/models.py.

# CÃCH Báº N LÃ€M VIá»†C
- Äá»c tháº» viá»‡c, liá»‡t kÃª giáº£ Ä‘á»‹nh trÆ°á»›c khi code. Thiáº¿u thÃ´ng tin thÃ¬ há»i Bá»™ nÃ£o, khÃ´ng Ä‘oÃ¡n.
- Viáº¿t code + test + tÃ i liá»‡u ngáº¯n cho pháº§n cá»§a mÃ¬nh.
- Cháº¡y test, dÃ¡n káº¿t quáº£ tháº­t. KhÃ´ng bao giá» bÃ¡o "Ä‘Ã£ cháº¡y" khi chÆ°a cháº¡y.
- Káº¿t thÃºc báº±ng BÃO CÃO theo Ä‘Ãºng máº«u á»Ÿ má»¥c 9.
```

## 3. Kiáº¿n trÃºc khung plugin

LÃµi chá»‰ lÃ m ba viá»‡c: Ä‘iá»u phá»‘i stage, giá»¯ cache, chá»n plugin theo config. Má»i viá»‡c náº·ng náº±m trong plugin, vÃ  plugin dÃ¹ng model lá»›n thÃ¬ gá»i má»™t worker HTTP riÃªng.

[embedded content: kiáº¿n trÃºc pipeline Â· 9 stage, 1 vÃ²ng kiá»ƒm tra]

NhÃ¡nh slide (1â€“3) vÃ  nhÃ¡nh giá»ng (4â€“5) Ä‘á»™c láº­p nÃªn cháº¡y song song; cÃ¢u nÃ o Ä‘á»c sai quÃ¡ ngÆ°á»¡ng CER thÃ¬ quay láº¡i TTS tá»•ng há»£p láº¡i, cÃ²n áº£nh slide Ä‘i tháº³ng tá»›i Composer.

## 4. Há»£p Ä‘á»“ng dá»¯ liá»‡u vÃ  interface plugin

ÄÃ¢y lÃ  pháº§n thá»£ code M0 pháº£i viáº¿t Ä‘Ãºng tá»«ng chá»¯; cÃ¡c thá»£ sau chá»‰ Ä‘Æ°á»£c implement, khÃ´ng Ä‘Æ°á»£c sá»­a. Má»i thá»i gian tÃ­nh báº±ng giÃ¢y (float), má»i Ä‘Æ°á»ng dáº«n tÆ°Æ¡ng Ä‘á»‘i so vá»›i thÆ° má»¥c lÃ m viá»‡c cá»§a job.

### 4.1 core/models.py

```python
from __future__ import annotations
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field


class Word(BaseModel):
    text: str
    start: float
    end: float
    score: float | None = None  # Ä‘á»™ tin cáº­y cÄƒn chá»‰nh


class Segment(BaseModel):  # má»™t cÃ¢u Ä‘á»c
    id: str  # "s003_02" = slide 3, cÃ¢u 2
    text: str  # cÃ¢u hiá»ƒn thá»‹ trÃªn phá»¥ Ä‘á»
    spoken_text: str  # cÃ¢u Ä‘Ã£ chuáº©n hÃ³a Ä‘á»ƒ TTS Ä‘á»c (sá»‘ -> chá»¯...)
    audio_path: Path | None = None
    start: float | None = None  # má»‘c trong toÃ n video
    end: float | None = None
    words: list[Word] = []
    cer: float | None = None  # lá»—i Ä‘á»c so vá»›i ASR kiá»ƒm tra láº¡i
    attempts: int = 0


class Slide(BaseModel):
    index: int  # báº¯t Ä‘áº§u tá»« 1
    title: str = ""
    body_text: str = ""
    notes_raw: str = ""
    image_path: Path | None = None
    hidden: bool = False
    script: str = ""  # lá»i Ä‘á»c sau khi LLM xá»­ lÃ½
    script_source: Literal["notes", "llm_from_notes", "llm_from_slide", "empty"] = "empty"
    segments: list[Segment] = []
    start: float | None = None
    end: float | None = None


class VoiceProfile(BaseModel):
    ref_audio: Path  # Ä‘oáº¡n máº«u Ä‘Ã£ lÃ m sáº¡ch, 24 kHz mono
    ref_text: str  # lá»i cá»§a Ä‘oáº¡n máº«u (ASR), nhiá»u engine báº¯t buá»™c
    language: str  # "vi", "en"...
    extra: dict = {}  # dá»¯ liá»‡u riÃªng cá»§a engine (embedding, speaker id)
    consent_confirmed: bool = False


class DeckMeta(BaseModel):
    title: str = ""
    author: str = ""
    language: str = "vi"
    created_at: str = ""


class Project(BaseModel):
    job_id: str
    source_slides: Path
    source_voice: Path
    meta: DeckMeta = DeckMeta()
    slides: list[Slide] = []
    voice: VoiceProfile | None = None
    stage_status: dict[str, Literal["pending", "done", "failed", "skipped"]] = {}
    plugins_used: dict[str, str] = {}  # stage -> "tÃªn_plugin@phiÃªn_báº£n"
    warnings: list[str] = []
```

### 4.2 core/interfaces.py

```python
from abc import ABC, abstractmethod
from pathlib import Path
from .models import Project, Slide, Segment, VoiceProfile


class Plugin(ABC):
    name: str = ""
    version: str = "0.1.0"

    def __init__(self, config: dict, workdir: Path): ...
    def healthcheck(self) -> None: ...  # raise PluginUnavailable náº¿u thiáº¿u phá»¥ thuá»™c/worker


class SlideRenderer(Plugin):  # slide -> áº£nh + text + notes
    @abstractmethod
    def render(self, project: Project, out_dir: Path, width: int, height: int) -> list[Slide]: ...


class VoicePreparer(Plugin):  # file giá»ng thÃ´ -> VoiceProfile
    @abstractmethod
    def prepare(self, raw_audio: Path, language: str, out_dir: Path) -> VoiceProfile: ...


class LLMProvider(Plugin):  # gá»i mÃ´ hÃ¬nh ngÃ´n ngá»¯, tráº£ JSON Ä‘Ãºng schema
    @abstractmethod
    def complete_json(self, system: str, user: str, schema: dict) -> dict: ...


class ScriptWriter(Plugin):  # notes -> lá»i Ä‘á»c tá»± nhiÃªn, chia cÃ¢u
    @abstractmethod
    def write(self, slide: Slide, deck_context: str, llm: LLMProvider | None) -> Slide: ...


class TextNormalizer(Plugin):  # "2026" -> "hai nghÃ¬n khÃ´ng trÄƒm hai mÆ°Æ¡i sÃ¡u"
    @abstractmethod
    def normalize(self, text: str, language: str) -> str: ...


class TTSEngine(Plugin):  # giá»ng nhÃ¢n báº£n
    @abstractmethod
    def load_voice(self, voice: VoiceProfile) -> None: ...
    @abstractmethod
    def synthesize(
        self, text: str, out_path: Path, speed: float = 1.0
    ) -> float: ...  # tráº£ vá» Ä‘á»™ dÃ i (s)


class Aligner(Plugin):  # ASR kiá»ƒm tra + cÄƒn chá»‰nh tá»«ng tá»«
    @abstractmethod
    def transcribe(self, audio: Path, language: str) -> str: ...
    @abstractmethod
    def align(self, audio: Path, text: str, language: str) -> list["Word"]: ...


class SubtitleWriter(Plugin):
    @abstractmethod
    def write(
        self, project: Project, out_dir: Path
    ) -> dict[str, Path]: ...  # {"srt":..., "vtt":..., "ass":...}


class AvatarRenderer(Plugin):  # tÃ¹y chá»n: ngÆ°á»i dáº«n nÃ³i khá»›p kháº©u hÃ¬nh
    @abstractmethod
    def render(self, face_image: Path, audio: Path, out_path: Path) -> Path: ...


class Composer(Plugin):  # ghÃ©p áº£nh + audio + phá»¥ Ä‘á» + chÆ°Æ¡ng + metadata
    @abstractmethod
    def compose(self, project: Project, subtitles: dict[str, Path], out_path: Path) -> Path: ...
```

### 4.3 Registry vÃ  há»£p Ä‘á»“ng worker

- ÄÄƒng kÃ½ plugin báº±ng decorator `@register("tts", "xtts")` vÃ  báº±ng entry point `slidevoice.plugins` Ä‘á»ƒ plugin cÃ i ngoÃ i cÅ©ng Ä‘Æ°á»£c nháº­n.
- Plugin dÃ¹ng model náº·ng lÃ  má»™t lá»›p má»ng gá»i worker HTTP. Má»i worker cÃ³ `GET /health` vÃ  `POST /run` nháº­n/tráº£ JSON; file trao Ä‘á»•i qua thÆ° má»¥c chung Ä‘Æ°á»£c mount, khÃ´ng gá»­i base64 khi file lá»›n hÆ¡n 10 MB.
- Lá»—i dÃ¹ng cÃ¡c lá»›p ngoáº¡i lá»‡ chung trong `core/errors.py`: `PluginUnavailable`, `StageFailed`, `InputInvalid`, `ConsentMissing`.

### 4.4 Danh má»¥c plugin máº·c Ä‘á»‹nh

Má»—i stage cÃ³ má»™t plugin máº·c Ä‘á»‹nh cháº¡y Ä‘Æ°á»£c khÃ´ng cáº§n GPU, vÃ  cÃ¡c plugin cháº¥t lÆ°á»£ng cao hÆ¡n cáº¯m vÃ o sau. TÃªn repo láº¥y tá»« trÃ­ nhá»› Ä‘áº¿n giá»¯a 2026, chÆ°a Ä‘Æ°á»£c kiá»ƒm tra láº¡i; thá»£ code pháº£i xÃ¡c minh phiÃªn báº£n vÃ  giáº¥y phÃ©p trÆ°á»›c khi dÃ¹ng.

| Stage | Plugin máº·c Ä‘á»‹nh | Plugin thay tháº¿ | Ghi chÃº cho thá»£ code |
| --- | --- | --- | --- |
| SlideRenderer | `libreoffice` (soffice headless â†’ PDF â†’ PNG báº±ng pdf2image) + python-pptx Ä‘á»c notes | `pdf_only` (PyMuPDF), `powerpoint_com` (Windows) | CÃ i font tiáº¿ng Viá»‡t trong worker; slide 4:3 thÃ¬ thÃªm viá»n, khÃ´ng kÃ©o giÃ£n; bá» slide áº©n náº¿u cáº¥u hÃ¬nh yÃªu cáº§u |
| VoicePreparer | `basic`: ffmpeg â†’ 24 kHz mono, cáº¯t láº·ng báº±ng VAD (silero-vad), chá»n Ä‘oáº¡n 6â€“15 s sáº¡ch nháº¥t, chuáº©n hÃ³a -23 LUFS | `deepfilter` (DeepFilterNet khá»­ á»“n), `demucs` (tÃ¡ch giá»ng khá»i nháº¡c ná»n) | Tá»± sinh `ref_text` báº±ng Aligner; cáº£nh bÃ¡o náº¿u máº«u dÆ°á»›i 6 s hoáº·c SNR tháº¥p |
| LLMProvider | `openai_compat` (má»i API tÆ°Æ¡ng thÃ­ch OpenAI: OpenAI, OpenRouter, DeepSeek, Groqâ€¦; chá»‰ cáº§n base_url + API key) | `anthropic`, `none` | Báº¯t buá»™c tráº£ JSON Ä‘Ãºng schema; tá»± thá»­ láº¡i tá»‘i Ä‘a 3 láº§n khi JSON há»ng; API key Ä‘á»c tá»« biáº¿n mÃ´i trÆ°á»ng; plugin cohere cho dÃ²ng Command, anthropic cho Claude; Ollama chá»‰ lÃ  tÃ¹y chá»n cháº¡y local |
| ScriptWriter | `passthrough`: dÃ¹ng notes nguyÃªn vÄƒn, chá»‰ tÃ¡ch cÃ¢u | `llm_rewrite`: viáº¿t láº¡i notes thÃ nh lá»i nÃ³i tá»± nhiÃªn; `llm_from_slide`: notes trá»‘ng thÃ¬ sinh tá»« ná»™i dung slide | KhÃ´ng Ä‘Æ°á»£c bá»‹a sá»‘ liá»‡u khÃ´ng cÃ³ trong slide/notes; Ä‘Ã¡nh dáº¥u `script_source` |
| TextNormalizer | `vi_rules` (sá»‘, ngÃ y, Ä‘Æ¡n vá»‹, viáº¿t táº¯t tiáº¿ng Viá»‡t) + `en_rules` | `llm_normalize` | Giá»¯ `text` gá»‘c cho phá»¥ Ä‘á», chá»‰ Ä‘á»•i `spoken_text` cho TTS |
| TTSEngine | `xtts` (idiap/coqui-ai-TTS, cÃ³ báº£n viXTTS cho tiáº¿ng Viá»‡t) | `f5tts` (SWivid/F5-TTS, báº£n Viá»‡t hÃ³a), `gpt_sovits`, `cosyvoice`, `fish_speech`, `openvoice`, `vieneu` | Má»—i engine lÃ  má»™t worker riÃªng; tá»•ng há»£p theo tá»«ng cÃ¢u; ghi láº¡i seed Ä‘á»ƒ tÃ¡i láº­p |
| Aligner | `faster_whisper` (ASR kiá»ƒm tra) + cÄƒn chá»‰nh theo cÃ¢u | `whisperx` (cÄƒn chá»‰nh má»©c tá»«), `stable_ts` | DÃ¹ng cho cáº£ ref_text, kiá»ƒm tra CER vÃ  má»‘c thá»i gian tá»«ng tá»« |
| SubtitleWriter | `standard`: SRT + VTT + ASS | `karaoke_ass` (tÃ´ sÃ¡ng tá»«ng tá»«) | Quy táº¯c ngáº¯t dÃ²ng á»Ÿ má»¥c 5 |
| AvatarRenderer | `none` | `musetalk`, `sadtalker`, `hallo`, `liveportrait` | Chá»‰ cháº¡y khi cáº¥u hÃ¬nh cÃ³ áº£nh khuÃ´n máº·t; Ä‘áº·t á»Ÿ gÃ³c dÆ°á»›i pháº£i |
| Composer | `ffmpeg`: ghÃ©p clip tá»«ng slide, chÃ¨n phá»¥ Ä‘á» má»m, chÆ°Æ¡ng, metadata, chuáº©n hÃ³a -16 LUFS | `moviepy` (khi cáº§n hiá»‡u á»©ng chuyá»ƒn cáº£nh phá»©c táº¡p) | Gá»i ffmpeg qua subprocess vá»›i danh sÃ¡ch tham sá»‘, khÃ´ng ghÃ©p chuá»—i shell |

## 5. Phá»¥ Ä‘á», metadata vÃ  gÃ³i Ä‘áº§u ra

Video chá»‰ Ä‘Æ°á»£c coi lÃ  "hoÃ n chá»‰nh" khi Ä‘á»§ nÄƒm lá»›p thÃ´ng tin: hÃ¬nh, tiáº¿ng, phá»¥ Ä‘á», chÆ°Æ¡ng vÃ  metadata, cá»™ng vá»›i cÃ¡c file Ä‘i kÃ¨m.

### 5.1 Dá»±ng dÃ²ng thá»i gian

1. Má»—i slide báº¯t Ä‘áº§u báº±ng `lead_in` 0,5 s im láº·ng, sau Ä‘Ã³ láº§n lÆ°á»£t cÃ¡c cÃ¢u, giá»¯a cÃ¡c cÃ¢u `gap` 0,25 s, cuá»‘i slide `tail` 0,8 s.
2. Slide khÃ´ng cÃ³ lá»i Ä‘á»c hiá»ƒn thá»‹ `empty_slide_duration` 3 s (cáº¥u hÃ¬nh Ä‘Æ°á»£c) vÃ  ghi cáº£nh bÃ¡o.
3. Má»‘c `start/end` cá»§a cÃ¢u tÃ­nh tá»« Ä‘á»™ dÃ i audio tháº­t, khÃ´ng Æ°á»›c lÆ°á»£ng. Má»‘c tá»«ng tá»« láº¥y tá»« Aligner rá»“i cá»™ng offset cá»§a cÃ¢u.
4. Chuyá»ƒn cáº£nh giá»¯a slide (crossfade 0,3 s) khÃ´ng Ä‘Æ°á»£c lÃ m lá»‡ch má»‘c phá»¥ Ä‘á».

### 5.2 Quy táº¯c phá»¥ Ä‘á»

- Tá»‘i Ä‘a 2 dÃ²ng, má»—i dÃ²ng tá»‘i Ä‘a 42 kÃ½ tá»± (tiáº¿ng Viá»‡t tÃ­nh theo kÃ½ tá»± Unicode Ä‘Ã£ dá»±ng sáºµn NFC).
- Má»—i khá»‘i phá»¥ Ä‘á» hiá»ƒn thá»‹ tá»« 1 s Ä‘áº¿n 7 s; cÃ¢u dÃ i thÃ¬ tÃ¡ch theo dáº¥u cÃ¢u, rá»“i theo má»‘c tá»«.
- KhÃ´ng ngáº¯t dÃ²ng giá»¯a sá»‘ vÃ  Ä‘Æ¡n vá»‹, giá»¯a tÃªn riÃªng nhiá»u chá»¯.
- Phá»¥ Ä‘á» hiá»ƒn thá»‹ `text` gá»‘c (cÃ³ sá»‘, viáº¿t táº¯t), khÃ´ng hiá»ƒn thá»‹ `spoken_text`.
- Kiá»ƒu ASS máº·c Ä‘á»‹nh: font Be Vietnam Pro hoáº·c Noto Sans, viá»n Ä‘en 2 px, cÃ¡ch Ä‘Ã¡y 6% chiá»u cao, khÃ´ng che logo gÃ³c.

### 5.3 NhÃºng vÃ o video.mp4

- Phá»¥ Ä‘á» má»m dáº¡ng `mov_text`, cÃ³ tháº» ngÃ´n ngá»¯ (`language=vie`). TÃ¹y chá»n `burn_in: true` thÃ¬ váº½ tháº³ng lÃªn hÃ¬nh báº±ng file ASS.
- ChÆ°Æ¡ng: má»™t chÆ°Æ¡ng má»—i slide, tÃªn chÆ°Æ¡ng lÃ  tiÃªu Ä‘á» slide (rá»—ng thÃ¬ "Slide N"), ghi qua file FFMETADATA.
- Metadata: `title`, `artist` (tÃ¡c giáº£), `comment` ("Giá»ng Ä‘á»c Ä‘Æ°á»£c táº¡o báº±ng AI tá»« máº«u giá»ng Ä‘Ã£ Ä‘Æ°á»£c Ä‘á»“ng Ã½"), `creation_time`, `language`, `encoder` (SlideVoice + phiÃªn báº£n).
- Ã‚m thanh: AAC 192 kbps, 48 kHz, chuáº©n hÃ³a -16 LUFS, Ä‘á»‰nh khÃ´ng vÆ°á»£t -1 dBTP.

### 5.4 CÃ¡c file Ä‘i kÃ¨m

| File | Ná»™i dung | DÃ¹ng Ä‘á»ƒ |
| --- | --- | --- |
| `video.mp4` | Video hoÃ n chá»‰nh | Xem, Ä‘Äƒng táº£i |
| `subtitles.srt` / `.vtt` / `.ass` | Phá»¥ Ä‘á» theo cÃ¢u; ASS cÃ³ thá»ƒ theo tá»« | ÄÄƒng YouTube, web, chá»‰nh sá»­a |
| `transcript.md` | Lá»i Ä‘á»c theo slide, cÃ³ má»‘c thá»i gian | Äá»c láº¡i, lÃ m tÃ i liá»‡u |
| `chapters.txt` | Dáº¡ng `00:00 TiÃªu Ä‘á»` | DÃ¡n vÃ o mÃ´ táº£ YouTube |
| `manifest.json` | ToÃ n bá»™ `Project` Ä‘Ã£ tuáº§n tá»± hÃ³a | Cháº¡y láº¡i, gá»¡ lá»—i |
| `report.json` / `report.html` | CER tá»«ng cÃ¢u, LUFS, cáº£nh bÃ¡o, thá»i gian má»—i stage | Kiá»ƒm tra cháº¥t lÆ°á»£ng |

## 6. Cáº¥u trÃºc thÆ° má»¥c, cáº¥u hÃ¬nh vÃ  CLI

LÃµi lÃ  má»™t gÃ³i Python nháº¹; má»—i worker náº·ng náº±m trong `workers/` vá»›i Dockerfile riÃªng Ä‘á»ƒ khÃ´ng xung Ä‘á»™t phá»¥ thuá»™c.

```text
slidevoice/
â”œâ”€â”€ SPEC.md                      # tÃ i liá»‡u nÃ y
â”œâ”€â”€ pyproject.toml               # chá»‰ phá»¥ thuá»™c nháº¹: pydantic, typer, pyyaml, httpx, python-pptx, rich
â”œâ”€â”€ slidevoice/
â”‚   â”œâ”€â”€ core/
â”‚   â”‚   â”œâ”€â”€ models.py            # má»¥c 4
â”‚   â”‚   â”œâ”€â”€ interfaces.py        # má»¥c 4
â”‚   â”‚   â”œâ”€â”€ registry.py          # @register + entry points
â”‚   â”‚   â”œâ”€â”€ pipeline.py          # cháº¡y stage theo thá»© tá»±, cache, resume
â”‚   â”‚   â”œâ”€â”€ cache.py             # hash Ä‘áº§u vÃ o + config cá»§a stage
â”‚   â”‚   â”œâ”€â”€ config.py            # Ä‘á»c YAML, gá»™p vá»›i máº·c Ä‘á»‹nh, kiá»ƒm tra
â”‚   â”‚   â”œâ”€â”€ errors.py
â”‚   â”‚   â””â”€â”€ worker_client.py     # client HTTP chung cho worker
â”‚   â”œâ”€â”€ plugins/
â”‚   â”‚   â”œâ”€â”€ render/  voice/  llm/  script/  normalize/
â”‚   â”‚   â”œâ”€â”€ tts/  align/  subtitle/  avatar/  compose/
â”‚   â”‚   â””â”€â”€ (má»—i plugin: má»™t file .py + test riÃªng)
â”‚   â”œâ”€â”€ report/                  # sinh report.json, report.html
â”‚   â””â”€â”€ cli.py
â”œâ”€â”€ workers/
â”‚   â”œâ”€â”€ xtts/  f5tts/  gpt_sovits/  whisper/  musetalk/
â”‚   â”‚   â””â”€â”€ (Dockerfile, server.py, requirements.txt, README.md)
â”‚   â””â”€â”€ docker-compose.yml
â”œâ”€â”€ configs/
â”‚   â”œâ”€â”€ default.yaml
â”‚   â”œâ”€â”€ vi_cpu.yaml              # cháº¡y Ä‘Æ°á»£c trÃªn CPU, cháº¥t lÆ°á»£ng cÆ¡ báº£n
â”‚   â””â”€â”€ vi_gpu_best.yaml
â”œâ”€â”€ samples/                     # 1 deck 3 slide + 1 giá»ng máº«u ngáº¯n Ä‘á»ƒ test
â””â”€â”€ tests/
    â”œâ”€â”€ unit/  integration/  golden/
```

### 6.1 configs/default.yaml

```yaml
project:
  language: vi
  title: ""            # trá»‘ng thÃ¬ láº¥y tá»« thuá»™c tÃ­nh file pptx
  author: ""
  voice_consent: false  # Báº®T BUá»˜C true thÃ¬ má»›i cháº¡y stage TTS

render:   { plugin: libreoffice, width: 1920, height: 1080, skip_hidden: true }
voice:    { plugin: basic, denoise: false, ref_min_sec: 6, ref_max_sec: 15 }
llm:
  plugin: openai_compat
  base_url: https://api.openai.com/v1   # hoáº·c báº¥t ká»³ endpoint tÆ°Æ¡ng thÃ­ch OpenAI
  api_key_env: LLM_API_KEY             # chá»‰ ghi TÃŠN biáº¿n mÃ´i trÆ°á»ng, khÃ´ng ghi key
  model: <tÃªn model cá»§a nhÃ  cung cáº¥p>
  temperature: 0.3
  timeout_sec: 60
  max_retries: 3                       # khi gáº·p 429 / 5xx, backoff lÅ©y thá»«a
script:   { plugin: llm_rewrite, style: "thÃ¢n thiá»‡n, rÃµ rÃ ng", max_words_per_slide: 180,
            fallback_when_no_notes: llm_from_slide }
normalize: { plugin: vi_rules }
tts:
  plugin: xtts
  worker_url: http://localhost:8101
  speed: 1.0
  seed: 42
align:    { plugin: faster_whisper, worker_url: http://localhost:8201, model: large-v3,
            word_level: true }
qa:       { max_cer: 0.15, max_retries: 2, target_lufs: -16 }
timing:   { lead_in: 0.5, gap: 0.25, tail: 0.8, empty_slide_duration: 3.0, transition: 0.3 }
subtitle: { plugin: standard, max_chars_per_line: 42, max_lines: 2, burn_in: false }
avatar:   { plugin: none, face_image: null, position: bottom_right, scale: 0.22 }
compose:  { plugin: ffmpeg, fps: 30, crf: 20, preset: medium }
```

### 6.2 CLI

```bash
slidevoice run   --slides deck.pptx --voice me.wav --config configs/vi_cpu.yaml --out out/
slidevoice run   ... --from-stage tts          # cháº¡y láº¡i tá»« má»™t stage
slidevoice resume out/job_20261014_1530       # tiáº¿p tá»¥c job dá»Ÿ
slidevoice stage render --slides deck.pptx    # cháº¡y riÃªng má»™t stage Ä‘á»ƒ thá»­
slidevoice plugins                            # liá»‡t kÃª plugin + healthcheck
slidevoice preview --slide 3                  # chá»‰ dá»±ng slide 3 Ä‘á»ƒ nghe thá»­ giá»ng
```

## 7. Quy táº¯c code báº¯t buá»™c

Thá»£ code vi pháº¡m má»™t quy táº¯c dÆ°á»›i Ä‘Ã¢y thÃ¬ bÃ i bá»‹ tráº£ vá», dÃ¹ cháº¡y Ä‘Æ°á»£c.

**Cháº¥t lÆ°á»£ng code**

- Python 3.11, type hint Ä‘áº§y Ä‘á»§, `ruff` + `mypy --strict` cho `core/`, khÃ´ng cáº£nh bÃ¡o.
- KhÃ´ng hardcode Ä‘Æ°á»ng dáº«n, URL, tÃªn model; má»i thá»© Ä‘i qua config. API key chá»‰ Ä‘á»c tá»« biáº¿n mÃ´i trÆ°á»ng, khÃ´ng bao giá» ghi vÃ o config, log, manifest hay report.
- Log báº±ng `logging` vá»›i tÃªn stage; khÃ´ng dÃ¹ng `print`. Tiáº¿n Ä‘á»™ hiá»ƒn thá»‹ báº±ng `rich`.
- Gá»i lá»‡nh ngoÃ i (ffmpeg, soffice) báº±ng `subprocess.run([...], check=True)` vá»›i danh sÃ¡ch tham sá»‘, cÃ³ timeout.
- KhÃ´ng thÃªm phá»¥ thuá»™c vÃ o `pyproject.toml` cá»§a lÃµi náº¿u tháº» viá»‡c khÃ´ng cho phÃ©p.

**Lá»—i vÃ  phá»¥c há»“i**

- Plugin thiáº¿u phá»¥ thuá»™c hoáº·c worker khÃ´ng pháº£n há»“i â†’ `PluginUnavailable` vá»›i hÆ°á»›ng dáº«n kháº¯c phá»¥c cá»¥ thá»ƒ.
- Má»™t cÃ¢u TTS lá»—i â†’ thá»­ láº¡i theo `qa.max_retries` vá»›i seed khÃ¡c; váº«n lá»—i thÃ¬ ghi cáº£nh bÃ¡o, chÃ¨n im láº·ng Ä‘Ãºng Ä‘á»™ dÃ i Æ°á»›c tÃ­nh, pipeline khÃ´ng dá»«ng.
- CÃ¢u cÃ³ CER lá»›n hÆ¡n `qa.max_cer` â†’ tá»•ng há»£p láº¡i; sau láº§n cuá»‘i váº«n vÆ°á»£t thÃ¬ giá»¯ báº£n tá»‘t nháº¥t vÃ  bÃ¡o trong report.
- `voice_consent: false` â†’ dá»«ng trÆ°á»›c stage TTS vá»›i `ConsentMissing`, khÃ´ng cÃ³ cá» nÃ o bá» qua Ä‘Æ°á»£c.

**Cache vÃ  cháº¡y láº¡i**

- KhÃ³a cache cá»§a stage = hash(Ä‘áº§u vÃ o cá»§a stage + config cá»§a stage + tÃªn vÃ  phiÃªn báº£n plugin).
- Káº¿t quáº£ tá»«ng stage lÆ°u vÃ o `workdir/<stage>/` vÃ  cáº­p nháº­t `manifest.json` sau má»—i stage.
- Cache TTS á»Ÿ má»©c tá»«ng cÃ¢u: sá»­a má»™t cÃ¢u notes chá»‰ tá»•ng há»£p láº¡i Ä‘Ãºng cÃ¢u Ä‘Ã³.

**Kiá»ƒm thá»­**

- Má»—i plugin cÃ³ unit test cháº¡y Ä‘Æ°á»£c khÃ´ng cáº§n GPU, dÃ¹ng mock cho worker.
- `tests/integration/` cháº¡y cáº£ pipeline trÃªn `samples/` vá»›i plugin giáº£ (`fake_tts` sinh tiáº¿ng bÃ­p Ä‘Ãºng Ä‘á»™ dÃ i) trong dÆ°á»›i 60 s.
- `tests/golden/` so sÃ¡nh phá»¥ Ä‘á» vÃ  chÆ°Æ¡ng sinh ra vá»›i file chuáº©n Ä‘Ã£ duyá»‡t.
- Kiá»ƒm tra video Ä‘áº§u ra báº±ng `ffprobe`: cÃ³ luá»“ng video, audio, phá»¥ Ä‘á», sá»‘ chÆ°Æ¡ng báº±ng sá»‘ slide, metadata Ä‘á»§ trÆ°á»ng.

## 8. Lá»™ trÃ¬nh vÃ  tháº» giao viá»‡c

Thá»© tá»±: M0 lÃ m trÆ°á»›c má»™t mÃ¬nh; M1 Ä‘áº¿n M6 cháº¡y song song sau khi M0 qua nghiá»‡m thu; M7 ghÃ©p táº¥t cáº£; M8 vÃ  M9 lÃ  pháº§n má»Ÿ rá»™ng. Má»—i tháº» dÃ¡n sau prompt há»‡ thá»‘ng á»Ÿ má»¥c 2.

### 8.1 Máº«u tháº» giao viá»‡c

```markdown
# THáºº VIá»†C: <mÃ£> â€” <tÃªn>
PHáº M VI: chá»‰ Ä‘Æ°á»£c sá»­a cÃ¡c Ä‘Æ°á»ng dáº«n: <danh sÃ¡ch>
INTERFACE PHáº¢I IMPLEMENT: <tÃªn lá»›p trong core/interfaces.py>
Äáº¦U VÃ€O / Äáº¦U RA: <mÃ´ táº£, kÃ¨m file máº«u trong samples/>
TIÃŠU CHÃ XONG:
- [ ] ...
KHÃ”NG ÄÆ¯á»¢C: Ä‘á»•i core/models.py, core/interfaces.py; thÃªm phá»¥ thuá»™c vÃ o lÃµi
BÃO CÃO: theo máº«u má»¥c 9
```

### 8.2 CÃ¡c tháº»

**M0 â€” Khung lÃµi.** Viáº¿t `core/` Ä‘Ãºng má»¥c 4 vÃ  7, `cli.py`, registry, pipeline cÃ³ cache vÃ  resume, `config.py` vá»›i `default.yaml`. Viáº¿t plugin giáº£ cho má»i stage (`fake_render`, `fake_tts`, `fake_align`...) Ä‘á»ƒ pipeline cháº¡y háº¿t tá»« Ä‘áº§u Ä‘áº¿n cuá»‘i. Xong khi: `slidevoice run` trÃªn `samples/` vá»›i cáº¥u hÃ¬nh `fake.yaml` sinh Ä‘á»§ gÃ³i Ä‘áº§u ra (video cÃ³ thá»ƒ lÃ  mÃ u ná»n), test integration xanh, `--from-stage` vÃ  `resume` hoáº¡t Ä‘á»™ng.

**M1 â€” SlideRenderer.** Plugin `libreoffice` vÃ  `pdf_only`. Äá»c title, body_text, notes, slide áº©n, metadata deck báº±ng python-pptx; xuáº¥t PNG Ä‘Ãºng kÃ­ch thÆ°á»›c, giá»¯ tá»‰ lá»‡. Xong khi: deck máº«u cÃ³ slide 4:3, slide áº©n, slide khÃ´ng notes, chá»¯ tiáº¿ng Viá»‡t cÃ³ dáº¥u Ä‘á»u cho áº£nh Ä‘Ãºng vÃ  text Ä‘Ãºng.

**M2 â€” VoicePreparer + Aligner.** Plugin `basic`, `deepfilter`; worker `whisper` (faster-whisper) cÃ³ `/transcribe` vÃ  `/align`. Xong khi: tá»« file giá»ng 2 phÃºt cÃ³ nháº¡c ná»n nháº¹, sinh Ä‘Æ°á»£c `ref_audio` 6â€“15 s sáº¡ch vÃ  `ref_text` Ä‘Ãºng; cÄƒn chá»‰nh má»©c tá»« trÃªn audio máº«u lá»‡ch dÆ°á»›i 100 ms.

**M3 â€” TTSEngine.** Worker `xtts` trÆ°á»›c, rá»“i `f5tts`. Má»—i worker cÃ³ `/health`, `/load_voice`, `/synthesize`. Xong khi: Ä‘á»c 20 cÃ¢u tiáº¿ng Viá»‡t máº«u, CER trung bÃ¬nh dÆ°á»›i 0,10, cÃ¹ng seed thÃ¬ cÃ¹ng káº¿t quáº£, Ä‘á»•i engine chá»‰ báº±ng má»™t dÃ²ng config.

**M4 â€” LLMProvider + ScriptWriter + TextNormalizer.** Plugin `openai_compat`, `llm_rewrite`, `llm_from_slide`, `vi_rules`. Prompt cho LLM náº±m trong file `.md` riÃªng, khÃ´ng nhÃºng trong code. Gá»i API cÃ³ timeout, thá»­ láº¡i khi gáº·p lá»—i 429/5xx, ghi sá»‘ token vÃ  chi phÃ­ Æ°á»›c tÃ­nh vÃ o report; thÃªm plugin cohere (Command) vÃ  anthropic dÃ¹ng SDK gá»‘c. Xong khi: notes gáº¡ch Ä‘áº§u dÃ²ng thÃ nh lá»i nÃ³i liá»n máº¡ch, khÃ´ng thÃªm sá»‘ liá»‡u láº¡ (kiá»ƒm báº±ng test so khá»›p sá»‘), sá»‘ vÃ  ngÃ y Ä‘Æ°á»£c Ä‘á»c Ä‘Ãºng tiáº¿ng Viá»‡t.

**M5 â€” SubtitleWriter.** Plugin `standard`, `karaoke_ass`, tuÃ¢n thá»§ quy táº¯c má»¥c 5. Xong khi: test golden khá»›p, khÃ´ng khá»‘i nÃ o quÃ¡ 42 kÃ½ tá»± má»—i dÃ²ng hoáº·c ngoÃ i khoáº£ng 1â€“7 s.

**M6 â€” Composer.** Plugin `ffmpeg`: clip tá»«ng slide, crossfade, phá»¥ Ä‘á» má»m vÃ  cá»©ng, chÆ°Æ¡ng, metadata, chuáº©n hÃ³a LUFS. Xong khi: `ffprobe` xÃ¡c nháº­n Ä‘á»§ luá»“ng, chÆ°Æ¡ng, metadata; phá»¥ Ä‘á» lá»‡ch tiáº¿ng dÆ°á»›i 150 ms.

**M7 â€” TÃ­ch há»£p vÃ  QA.** Ná»‘i plugin tháº­t vÃ o pipeline, vÃ²ng kiá»ƒm tra CER vÃ  tá»•ng há»£p láº¡i, `report.html`. Xong khi: deck 10 slide tháº­t cháº¡y tá»« Ä‘áº§u Ä‘áº¿n cuá»‘i trÃªn cáº£ `vi_cpu.yaml` vÃ  `vi_gpu_best.yaml`.

**M8 â€” AvatarRenderer (tÃ¹y chá»n).** Worker `musetalk`, ghÃ©p ngÆ°á»i dáº«n vÃ o gÃ³c theo config.

**M9 â€” Giao diá»‡n (tÃ¹y chá»n).** FastAPI + má»™t trang web Ä‘Æ¡n giáº£n: táº£i slide vÃ  giá»ng, chá»n cáº¥u hÃ¬nh, xem tiáº¿n Ä‘á»™, nghe thá»­ tá»«ng slide, sá»­a lá»i tá»«ng cÃ¢u rá»“i dá»±ng láº¡i.

## 9. BÃ¡o cÃ¡o cá»§a thá»£ code vÃ  prompt nghiá»‡m thu

Thá»£ code luÃ´n káº¿t thÃºc báº±ng máº«u bÃ¡o cÃ¡o dÆ°á»›i Ä‘Ã¢y; Bá»™ nÃ£o dÃ¹ng prompt nghiá»‡m thu Ä‘á»ƒ cháº¥m vÃ  quyáº¿t Ä‘á»‹nh nháº­n hay tráº£ bÃ i.

### 9.1 Máº«u bÃ¡o cÃ¡o (thá»£ code Ä‘iá»n)

```markdown
# BÃO CÃO: <mÃ£ tháº»>
1. ÄÃ£ lÃ m: <tÃ³m táº¯t 3â€“5 dÃ²ng>
2. File thay Ä‘á»•i: <danh sÃ¡ch Ä‘Æ°á»ng dáº«n>
3. Giáº£ Ä‘á»‹nh Ä‘Ã£ dÃ¹ng: <...>
4. Káº¿t quáº£ test (dÃ¡n nguyÃªn vÄƒn output): <...>
5. TiÃªu chÃ­ xong: tá»«ng má»¥c trong tháº», Ä‘Ã¡nh dáº¥u [x] hoáº·c [ ] kÃ¨m lÃ½ do
6. Rá»§i ro / viá»‡c cÃ²n dá»Ÿ: <...>
7. Äá» xuáº¥t Ä‘á»•i há»£p Ä‘á»“ng (náº¿u cÃ³): <interface nÃ o, Ä‘á»•i gÃ¬, vÃ¬ sao>
```

### 9.2 Prompt nghiá»‡m thu (Bá»™ nÃ£o dÃ¹ng)

```markdown
# VAI TRÃ’
Báº¡n lÃ  Bá»˜ NÃƒO kiáº¿n trÃºc sÆ° cá»§a dá»± Ã¡n SlideVoice, Ä‘ang nghiá»‡m thu bÃ i cá»§a má»™t thá»£ code.
Nguá»“n sá»± tháº­t: SPEC.md Ä‘Ã­nh kÃ¨m. Báº¡n kháº¯t khe, cá»¥ thá»ƒ, khÃ´ng khen chung chung.

# Äáº¦U VÃ€O
- Tháº» viá»‡c Ä‘Ã£ giao: <dÃ¡n>
- BÃ¡o cÃ¡o cá»§a thá»£: <dÃ¡n>
- Diff hoáº·c cÃ¡c file thay Ä‘á»•i: <dÃ¡n>
- Log test: <dÃ¡n>

# KIá»‚M TRA THEO THá»¨ Tá»°
1. Pháº¡m vi: cÃ³ sá»­a file ngoÃ i pháº¡m vi tháº», hoáº·c sá»­a core/models.py, core/interfaces.py khÃ´ng?
2. Há»£p Ä‘á»“ng: cÃ³ implement Ä‘Ãºng interface, Ä‘Ãºng chá»¯ kÃ½ hÃ m, Ä‘Ãºng kiá»ƒu tráº£ vá»?
3. TiÃªu chÃ­ xong: tá»«ng má»¥c cÃ³ báº±ng chá»©ng tháº­t trong log test khÃ´ng? Má»¥c nÃ o chá»‰ Ä‘Æ°á»£c "tuyÃªn bá»‘"?
4. Quy táº¯c má»¥c 7: hardcode, print, shell string, thiáº¿u timeout, thiáº¿u xá»­ lÃ½ lá»—i, thiáº¿u cache.
5. An toÃ n: cÃ³ Ä‘Æ°á»ng nÃ o bá» qua voice_consent khÃ´ng? CÃ³ ghi Ä‘Ã¨ file Ä‘áº§u vÃ o cá»§a ngÆ°á»i dÃ¹ng khÃ´ng?
6. Cháº¥t lÆ°á»£ng Ä‘áº§u ra (náº¿u cÃ³ file máº«u): phá»¥ Ä‘á», chÆ°Æ¡ng, metadata, LUFS, CER.
7. Äá» xuáº¥t Ä‘á»•i há»£p Ä‘á»“ng: cháº¥p nháº­n hay tá»« chá»‘i, kÃ¨m lÃ½ do; náº¿u cháº¥p nháº­n, viáº¿t Ä‘oáº¡n sá»­a SPEC.md.

# Äáº¦U RA
- Káº¾T LUáº¬N: NHáº¬N / NHáº¬N CÃ“ ÄIá»€U KIá»†N / TRáº¢ Vá»€
- Danh sÃ¡ch lá»—i, má»—i lá»—i: má»©c (cháº·n / nÃªn sá»­a / gá»£i Ã½), vá»‹ trÃ­ file:dÃ²ng, cÃ¡ch sá»­a
- Náº¿u TRáº¢ Vá»€: viáº¿t sáºµn THáºº VIá»†C Sá»¬A Lá»–I theo máº«u tháº» á»Ÿ má»¥c 8 Ä‘á»ƒ giao láº¡i cho thá»£
- Tháº» tiáº¿p theo nÃªn giao (náº¿u NHáº¬N)
```

### 9.3 TiÃªu chÃ­ cháº¥p nháº­n toÃ n dá»± Ã¡n

- [ ] Má»™t lá»‡nh `slidevoice run` biáº¿n deck 10 slide + 1 phÃºt giá»ng máº«u thÃ nh gÃ³i Ä‘áº§u ra Ä‘á»§ 8 loáº¡i file á»Ÿ má»¥c 5.
- [ ] Giá»ng trong video Ä‘Æ°á»£c ngÆ°á»i nghe quen giá»ng gá»‘c nháº­n ra; CER trung bÃ¬nh dÆ°á»›i 0,10.
- [ ] Phá»¥ Ä‘á» lá»‡ch tiáº¿ng dÆ°á»›i 150 ms; sá»‘ chÆ°Æ¡ng báº±ng sá»‘ slide khÃ´ng áº©n.
- [ ] Äá»•i engine TTS, LLM hoáº·c Aligner chá»‰ báº±ng sá»­a config, khÃ´ng sá»­a code.
- [ ] Sá»­a notes cá»§a má»™t slide rá»“i cháº¡y láº¡i chá»‰ tá»•ng há»£p láº¡i cÃ¢u bá»‹ Ä‘á»•i.
- [ ] KhÃ´ng cháº¡y Ä‘Æ°á»£c TTS khi `voice_consent` chÆ°a báº­t; video luÃ´n cÃ³ metadata ghi rÃµ giá»ng do AI táº¡o.
