# SlideVoice Quickstart Guide 🇻🇳

> _Từ 0 đến video chỉ trong 15 phút — hướng dẫn chi tiết cho người mới bắt đầu._

---

## 🎯 Mục lục

1. [Yêu cầu hệ thống](#1-yêu-cầu-hệ-thống)
2. [Cài đặt Python](#2-cài-đặt-python)
3. [Cài đặt SlideVoice](#3-cài-đặt-slidevoice)
4. [Cấu hình LLM](#4-cấu-hình-llm)
5. [Chuẩn bị bài giảng](#5-chuẩn-bị-bài-giảng)
6. [Chạy pipeline](#6-chạy-pipeline)
7. [Kết quả](#7-kết-quả)
8. [Xử lý lỗi thường gặp](#8-xử-lý-lỗi-thường-gặp)

---

## 1. Yêu cầu hệ thống

| Thành phần | Tối thiểu | Khuyến nghị |
|-----------|-----------|-------------|
| **Hệ điều hành** | Windows 10+ / Ubuntu 22.04+ | Windows 11 / Ubuntu 24.04 |
| **Python** | 3.11+ | 3.11 |
| **RAM** | 8 GB | 16 GB |
| **Ổ cứng** | 5 GB trống | 20 GB (cho nhiều video) |
| **GPU** ✨ | Không bắt buộc | NVIDIA RTX 3060+ (CUDA 12.1) |

> 💡 **GPU** chỉ cần nếu muốn TTS real-time qua VieNeu worker. Pipeline vẫn chạy CPU tốt.

---

## 2. Cài đặt Python

### Windows

1. Tải **Python 3.11** từ [python.org/downloads](https://www.python.org/downloads/)
2. **QUAN TRỌNG:** Trong cài đặt, **nhớ tick** ✅ _"Add Python to PATH"_
3. Mở **Command Prompt** (`Win + R` → `cmd` → Enter), kiểm tra:

```batch
python --version
```

Kết quả: `Python 3.11.x`

### Linux

```bash
sudo apt update && sudo apt install -y python3.11 python3.11-venv python3-pip
python3.11 --version
```

---

## 3. Cài đặt SlideVoice

### Bước 1: Mở terminal ở thư mục dự án

```batch
cd D:\SOFT\STV
```

### Bước 2: Chạy script setup (tự động)

**Windows:**
```batch
scripts\setup.bat
```

Script này sẽ: ✅ Kiểm tra Python 3.11 → ✅ Tạo venv `.venv` → ✅ Cài `slidevoice` editable → ✅ Cài thư viện cần → ✅ Smoke test

### Bước 3: Activate venv (mỗi khi dùng)

```batch
.venv\Scripts\activate
```

Dấu nhắc đổi thành: `(.venv) D:\SOFT\STV>`

### Bước 4: Kiểm tra

```batch
slidevoice --help
```