# Internal Analytics and Reporting Platform — Static Dashboard Module (بدون تكلفة)

لوحة تحليلات مبيعات كاملة تعمل كملف HTML واحد فقط — بدون سيرفر، بدون قاعدة بيانات،
بدون أي رسوم استضافة (يمكن فتحها محلياً أو رفعها مجاناً على GitHub Pages).

## أين أضع ملفاتي؟

```
metabase-azure-analytics/
├── csv/                        ← ضع ملفاتك الثلاثة هنا (هذا المسار الافتراضي في build.py)
│   ├── orders.csv               ← بيانات الطلبات (order + line-item grain)
│   ├── returns.csv              ← Order ID, Returned
│   └── people.csv               ← Regional Manager, Region
└── dashboard/
    ├── build.py                 ← سكربت البناء (لا تعدّله عادة)
    ├── index.template.html       ← القالب الاحترافي (التصميم من هنا)
    └── dist/
        └── index.html            ← الناتج النهائي — هذا هو الملف الذي تفتحه/ترفعه
```

> **مهم:** مجلد `csv/` في `.gitignore` افتراضياً لأننا افترضنا أن بياناتك التجارية حساسة.
> إذا كانت بيانات تجريبية عادية ولا مانع من رفعها لـ GitHub، احذف السطر `csv/*.csv`
> من ملف `.gitignore` في جذر المشروع.

## كيف أبنيها؟

```bash
python3 dashboard/build.py
```

بدون أي مكتبات خارجية (Python القياسي فقط). الناتج: `dashboard/dist/index.html`.

افتحه مباشرة بالمتصفح، أو استضفه مجاناً:

### الخيار الأسهل والمجاني: GitHub Pages
1. ادفع (`git push`) المشروع لمستودعك على GitHub (تأكد أن `dashboard/dist/index.html` مرفوع، وأنه ليس داخل `.gitignore`).
2. من إعدادات المستودع → Pages → اختر الفرع (`main`) ومجلد `/dashboard/dist` (أو انسخ الملف لمجلد `docs/` في الجذر إذا كانت أداة Pages تتطلب ذلك).
3. رابطك النهائي: `https://<username>.github.io/<repo-name>/`

هذا الخيار **مجاني بالكامل ولا يحتاج Azure إطلاقاً**.

### أو استضافته على نفس خادم Azure (إن كنت تستخدمه أصلاً لـ Metabase)
انسخ `dashboard/dist/index.html` إلى مجلد يخدمه nginx على نفس الـ VM، على مسار مختلف
مثل `/dashboard` بجانب Metabase على `:3000`. لا حاجة لحاوية Docker إضافية لمجرد ملف ثابت.

## إعادة البناء عند تحديث البيانات

كل مرة تُحدّث فيها ملفات CSV، أعد تشغيل:
```bash
python3 dashboard/build.py
```
ثم أعد رفع `dashboard/dist/index.html` الجديد (Pages أو الخادم).

## تخصيص العملة
```bash
CURRENCY=SAR python3 dashboard/build.py
```

## هيكل ملفات CSV المتوقع

**orders.csv** (صف واحد لكل بند طلب): `Order ID, Customer ID, Customer Name, Segment, Order Date, Ship Date, Ship Mode, Region, State/Province, City, Product ID, Product Name, Category, Sub-Category, Sales, Quantity, Discount, Profit`

**returns.csv**: `Order ID, Returned` (القيم: `Yes`/`No` أو فارغ)

**people.csv**: `Regional Manager, Region`

ملفات تجريبية صغيرة موجودة حالياً في `csv/` لتجربة البناء فوراً — استبدلها ببياناتك الحقيقية.
