# دليل النشر السريع - Render.com

## ✅ جاهز للنشر!

### الملفات المطلوبة (موجودة):
- ✅ `render.yaml` - تكوين Render
- ✅ `requirements_render.txt` - dependencies 
- ✅ `Procfile` - أمر التشغيل
- ✅ `gunicorn.conf.py` - إعدادات Gunicorn
- ✅ `runtime.txt` - Python 3.11
- ✅ `.gitignore` - ملفات مستبعدة

## خطوات النشر (5 دقائق):

### 1. رفع الكود إلى GitHub
```bash
git init
git add .
git commit -m "Ready for Render deployment"
git branch -M main
git remote add origin https://github.com/yourusername/clan-lords-bot.git
git push -u origin main
```

### 2. إنشاء خدمة في Render
1. اذهب إلى https://render.com
2. اضغط "New +" → "Web Service"
3. اربط GitHub repository
4. اختر المشروع

### 3. تكوين النشر
- **Build Command**: `pip install -r requirements_render.txt`
- **Start Command**: `gunicorn --config gunicorn.conf.py main:app`
- **Environment**: Python 3

### 4. المتغيرات البيئية
```
DISCORD_TOKEN = your_bot_token_here
SESSION_SECRET = random_secret_string
```

### 5. النشر
- اضغط "Create Web Service"
- انتظر 3-5 دقائق للبناء والنشر

## 🎯 النتيجة:
- رابط البوت: `https://your-app-name.onrender.com`
- البوت سيعمل تلقائياً في Discord
- لوحة المراقبة: `/bot-status`

## ⚠️ ملاحظات:
- الخطة المجانية تنام بعد 15 دقيقة
- استخدم UptimeRobot للحفاظ على النشاط
- البيانات محفوظة في ملفات JSON

## 🆘 مساعدة:
- السجلات: لوحة تحكم Render
- الحالة: زيارة `/` أو `/bot-status`
- إعادة النشر: git push جديد