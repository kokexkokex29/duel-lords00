# 📚 قائمة المكتبات المستخدمة | Libraries Used

## 🤖 Discord Bot Libraries
```python
discord.py==2.3.2           # مكتبة Discord الرئيسية
```

## 🌐 Web Server Libraries  
```python
Flask==3.0.0                # خادم الويب
Werkzeug==3.0.1            # أدوات WSGI
gunicorn==23.0.0           # خادم WSGI للإنتاج
```

## 📊 Database & Data Libraries
```python
# لا توجد قاعدة بيانات خارجية - يستخدم JSON files
```

## ⏰ Scheduling Libraries
```python
APScheduler==3.10.4        # جدولة المهام والتذكيرات
```

## 🔧 Utility Libraries
```python
nest-asyncio==1.6.0        # دعم async loops متداخلة
email-validator==2.1.0     # التحقق من البريد الإلكتروني
requests==2.31.0           # HTTP requests
```

## 🗄️ Database Libraries (اختيارية)
```python
psycopg2-binary==2.9.9     # PostgreSQL (للمشاريع المستقبلية)
flask-sqlalchemy==3.1.1   # ORM للقواعد البيانات
```

## 🐍 Python Standard Libraries المستخدمة
```python
import os                   # متغيرات النظام
import json                 # معالجة JSON  
import logging             # تسجيل الأحداث
import threading           # معالجة متوازية
import asyncio             # البرمجة غير المتزامنة
import datetime            # التاريخ والوقت
from typing import Optional # Type hints
```

## 📦 تثبيت جميع المكتبات

### طريقة 1: pip
```bash
pip install discord.py==2.3.2
pip install Flask==3.0.0
pip install Werkzeug==3.0.1
pip install gunicorn==23.0.0
pip install APScheduler==3.10.4
pip install nest-asyncio==1.6.0
pip install email-validator==2.1.0
pip install requests==2.31.0
pip install psycopg2-binary==2.9.9
pip install flask-sqlalchemy==3.1.1
```

### طريقة 2: requirements.txt
```txt
discord.py==2.3.2
Flask==3.0.0
Werkzeug==3.0.1
gunicorn==23.0.0
APScheduler==3.10.4
nest-asyncio==1.6.0
email-validator==2.1.0
requests==2.31.0
psycopg2-binary==2.9.9
flask-sqlalchemy==3.1.1
```

## 🔍 وصف المكتبات

| المكتبة | الاستخدام |
|---------|-----------|
| **discord.py** | التفاعل مع Discord API وإنشاء البوت |
| **Flask** | خادم الويب ولوحة التحكم |
| **gunicorn** | تشغيل التطبيق في الإنتاج |
| **APScheduler** | جدولة تذكيرات المباريات |
| **nest-asyncio** | حل مشاكل event loops |
| **requests** | طلبات HTTP للخدمات الخارجية |
| **email-validator** | التحقق من صحة البيانات |
| **psycopg2-binary** | دعم PostgreSQL للمستقبل |

## 🚀 إعداد البيئة

1. **Python 3.11+** مطلوب
2. **Discord Bot Token** مطلوب
3. **Replit Secrets** للتوكن الآمن

جميع هذه المكتبات مثبتة ومُعدة في المشروع الحالي!