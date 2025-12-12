"""
سكريبت مساعد لإنشاء ملف .env من env.example
"""
import secrets
import shutil
from pathlib import Path

def create_env_file():
    """إنشاء ملف .env من env.example مع SECRET_KEY آمن"""
    
    env_example = Path('env.example')
    env_file = Path('.env')
    
    if env_file.exists():
        print("⚠️  ملف .env موجود بالفعل!")
        response = input("هل تريد استبداله؟ (y/n): ")
        if response.lower() != 'y':
            print("❌ تم الإلغاء")
            return
    
    if not env_example.exists():
        print(f"❌ ملف {env_example} غير موجود!")
        return
    
    # نسخ env.example إلى .env
    shutil.copy(env_example, env_file)
    print(f"✅ تم نسخ {env_example} إلى {env_file}")
    
    # توليد SECRET_KEY آمن
    secret_key = secrets.token_urlsafe(50)
    
    # قراءة محتوى .env
    content = env_file.read_text(encoding='utf-8')
    
    # استبدال SECRET_KEY
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if line.startswith('SECRET_KEY='):
            new_lines.append(f'SECRET_KEY={secret_key}')
            print("✅ تم توليد SECRET_KEY آمن")
        else:
            new_lines.append(line)
    
    # كتابة المحتوى المحدث
    env_file.write_text('\n'.join(new_lines), encoding='utf-8')
    
    print("\n" + "="*50)
    print("✅ تم إنشاء ملف .env بنجاح!")
    print("="*50)
    print(f"\n📝 SECRET_KEY الجديد: {secret_key[:20]}...")
    print("\n⚠️  مهم: احفظ SECRET_KEY في مكان آمن!")
    print("   لن يتم حفظه مرة أخرى تلقائياً.\n")

if __name__ == '__main__':
    create_env_file()

