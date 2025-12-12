// ملف اختبار بسيط للتأكد من أن React يعمل
export default function SimpleApp() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial', direction: 'rtl' }}>
      <h1 style={{ color: 'green', fontSize: '24px' }}>
        ✅ React يعمل! هذا ملف اختبار بسيط
      </h1>
      <p>إذا رأيت هذا النص، فالمشكلة في App.tsx أو أحد المكونات</p>
      <p>إذا لم ترَ أي شيء، فالمشكلة في React نفسه أو التحميل</p>
      <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#f0f0f0' }}>
        <p>تاريخ: {new Date().toLocaleString('ar-SA')}</p>
      </div>
    </div>
  )
}

