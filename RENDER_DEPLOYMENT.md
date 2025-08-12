# دليل النشر على Render.com

## الملفات المطلوبة للنشر
✅ `render.yaml` - تكوين Render
✅ `requirements_render.txt` - المتطلبات 
✅ `Procfile` - أمر التشغيل
✅ `runtime.txt` - إصدار Python

## خطوات النشر

### 1. إنشاء حساب على Render.com
- اذهب إلى https://render.com
- سجل دخول بحساب GitHub

### 2. ربط المشروع
- اضغط "New +" → "Web Service"
- اربط مع GitHub repository
- اختر هذا المشروع

### 3. تكوين المتغيرات البيئية
يجب إضافة هذه المتغيرات في إعدادات Render:

```
DISCORD_TOKEN = your_discord_bot_token_here
SESSION_SECRET = any_random_string_here
```

### 4. إعدادات النشر
- **Build Command**: `pip install -r requirements_render.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 1 main:app`
- **Environment**: Python 3
- **Region**: Oregon (أو أي منطقة قريبة)
- **Plan**: Free

### 5. تأكيد النشر
بعد النشر الناجح:
- ستحصل على رابط مثل: `https://clan-lords-bombsquad-bot.onrender.com`
- البوت سيبدأ تلقائياً عند تشغيل الخدمة
- يمكن زيارة `/bot-status` لمراقبة حالة البوت

## ملاحظات مهمة

### الأداء
- الخطة المجانية تدخل في وضع السكون بعد 15 دقيقة من عدم النشاط
- يمكن استخدام UptimeRobot لإبقاء الخدمة نشطة

### قاعدة البيانات
- البوت يستخدم ملفات JSON محلية للبيانات
- البيانات محفوظة في مجلدات: `data/players.json`, `data/matches.json`, `data/tournaments.json`

### السجلات
- يمكن مراقبة السجلات من لوحة تحكم Render
- السجلات تظهر حالة اتصال Discord والأخطاء

## استكشاف الأخطاء

### البوت لا يتصل بـ Discord
- تأكد من صحة `DISCORD_TOKEN`
- تحقق من أن البوت مدعو للخادم مع الصلاحيات الصحيحة

### الموقع لا يعمل
- تحقق من سجلات البناء والتشغيل
- تأكد من تثبيت جميع المتطلبات بنجاح

### انقطاع الخدمة
- الخطة المجانية لها قيود على الاستخدام
- فكر في ترقية الخطة للاستخدام المكثف