# AI ช่วยเล่นเกม - Streamlit Edition

เครื่องมือช่วยเล่นเกมที่ใช้ AI วิเคราะห์กระดานเกมผ่าน OpenAI Vision API

## ฟีเจอร์

- 📸 ถ่ายภาพกระดานเกม
- 🤖 วิเคราะห์ด้วย AI (OpenAI Vision gpt-4o-mini)
- 🎯 4 โหมดการวิเคราะห์: เชิงกลยุทธ์, เชิงการสอน, เชิงรายละเอียด, เชิงสบายๆ
- 🔊 อ่านผลการวิเคราะห์ออกเสียง
- 📱 รองรับมือถือ

## ติดตั้ง

### ใช้ Conda (แนะนำ)

```bash
conda env create -f environment.yml
conda activate ai-grid-guide
```

### ใช้ pip

```bash
pip install -r requirements.txt
```

## ตั้งค่า

1. คัดลอก `.env.example` เป็น `.env`:
```bash
cp .env.example .env
```

2. ใส่ OpenAI API key ของคุณใน `.env`:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

หรือใส่ API key ตรงๆ ในแอป (sidebar)

## รันแอป

```bash
streamlit run streamlit_app.py
```

แอปจะเปิดที่ `http://localhost:8501`

## วิธีใช้

1. ใส่ OpenAI API key ใน sidebar (หรือตั้งค่าใน `.env`)
2. เลือกโหมดการวิเคราะห์
3. กด "📸 ถ่ายภาพกระดาน" เพื่อถ่ายรูป
4. กด "🎯 วิเคราะห์" เพื่อให้ AI วิเคราะห์
5. กด "🔊 อ่านออกเสียง" เพื่อฟังผลการวิเคราะห์

## โครงสร้างโปรเจค

```
ai-grid-guide/
├── streamlit_app.py          # แอปหลัก
├── src/
│   ├── __init__.py
│   ├── openai_client.py      # เชื่อมต่อ OpenAI API
│   └── prompts.py            # โหมดการวิเคราะห์
├── requirements.txt          # Python dependencies
├── environment.yml           # Conda environment
├── .env.example             # ตัวอย่าง API key
└── README.md
```

## Deploy

Deploy ไปยัง Streamlit Cloud:

1. Push code ไป GitHub
2. ไปที่ [share.streamlit.io](https://share.streamlit.io)
3. เชื่อมต่อ repository
4. เพิ่ม `OPENAI_API_KEY` ใน Secrets
5. Deploy

## เวอร์ชันเดิม

เวอร์ชัน HTML/JavaScript เก็บไว้ใน `index.html` และ `index.js`
