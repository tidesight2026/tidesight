// ملف اختبار بسيط جداً - بدون أي imports معقدة
export default function SimpleTest() {
  return (
    <div style={{ 
      padding: '50px', 
      fontFamily: 'Arial, sans-serif',
      direction: 'rtl',
      textAlign: 'right'
    }}>
      <h1 style={{ color: 'green', fontSize: '32px', marginBottom: '20px' }}>
        ✅ React يعمل!
      </h1>
      <p style={{ fontSize: '18px', color: '#333' }}>
        إذا رأيت هذا النص، فالمشكلة في App.tsx أو أحد المكونات المعقدة.
      </p>
      <p style={{ fontSize: '18px', color: '#666', marginTop: '10px' }}>
        الوقت: {new Date().toLocaleString('ar-SA')}
      </p>
      <div style={{
        marginTop: '30px',
        padding: '20px',
        backgroundColor: '#f0f0f0',
        borderRadius: '8px'
      }}>
        <p><strong>الخطوة التالية:</strong></p>
        <p>إذا رأيت هذا، فالمشكلة في:</p>
        <ul style={{ marginTop: '10px' }}>
          <li>React Router</li>
          <li>Zustand Store</li>
          <li>أحد المكونات المعقدة</li>
        </ul>
      </div>
    </div>
  )
}

