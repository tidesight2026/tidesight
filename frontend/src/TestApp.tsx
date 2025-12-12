// ملف اختبار بسيط للتأكد من أن React يعمل
export default function TestApp() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1 style={{ color: 'red', fontSize: '24px' }}>
        ✅ React يعمل! هذا ملف اختبار
      </h1>
      <p>إذا رأيت هذا النص، فالمشكلة في App.tsx أو أحد المكونات</p>
      <p>إذا لم ترَ أي شيء، فالمشكلة في React نفسه أو التحميل</p>
    </div>
  )
}
