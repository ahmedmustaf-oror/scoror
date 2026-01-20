from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime, timedelta
import uuid
import hashlib
import urllib.parse

# مسارات الملفات
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LICENSES_FILE = os.path.join(BASE_DIR, 'data', 'licenses.json')
REQUESTS_FILE = os.path.join(BASE_DIR, 'data', 'requests.json')

# تأكد من وجود مجلد data
os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)

def load_data(filename):
    """تحميل بيانات JSON"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
    
    # بيانات افتراضية إذا كان الملف غير موجود
    if 'licenses' in filename:
        return {"licenses": []}
    return {"requests": []}

def save_data(filename, data):
    """حفظ بيانات JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        return True
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        return False

def send_telegram_notification(message):
    """إرسال إشعار للتليجرام"""
    try:
        import requests
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '8403184945:AAHKgw2NHjNowyMlOTvfoR6rjGvw9IRDK6U')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID', '7709999332')
        
        if bot_token and chat_id and bot_token != '8403184945:AAHKgw2NHjNowyMlOTvfoR6rjGvw9IRDK6U':
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            requests.post(url, json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }, timeout=5)
    except:
        pass

def generate_admin_panel():
    """إنشاء HTML للوحة التحكم"""
    return '''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 لوحة تحكم نظام التراخيص</title>
    <style>
        :root {
            --primary: #4361ee;
            --secondary: #3a0ca3;
            --success: #4cc9f0;
            --warning: #f72585;
            --danger: #7209b7;
            --light: #f8f9fa;
            --dark: #212529;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', 'Cairo', Arial, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: var(--dark);
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        /* Header */
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .header h1 {
            color: var(--primary);
            font-size: 2.5rem;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .header p {
            color: #666;
            font-size: 1.1rem;
            line-height: 1.6;
        }
        
        /* Stats Cards */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
            transition: transform 0.3s, box-shadow 0.3s;
            text-align: center;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
        }
        
        .stat-card h3 {
            color: #666;
            font-size: 1rem;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .stat-card .count {
            font-size: 3rem;
            font-weight: bold;
            margin: 15px 0;
        }
        
        .stat-pending { border-top: 5px solid #ff9800; }
        .stat-active { border-top: 5px solid #4caf50; }
        .stat-blocked { border-top: 5px solid #f44336; }
        .stat-expired { border-top: 5px solid #9e9e9e; }
        
        .stat-pending .count { color: #ff9800; }
        .stat-active .count { color: #4caf50; }
        .stat-blocked .count { color: #f44336; }
        .stat-expired .count { color: #9e9e9e; }
        
        /* Search Box */
        .search-container {
            position: relative;
            margin: 30px 0;
        }
        
        .search-box {
            width: 100%;
            padding: 18px 20px 18px 50px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 1.1rem;
            outline: none;
            transition: all 0.3s;
            background: white url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23666" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>') no-repeat 20px center;
        }
        
        .search-box:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.2);
        }
        
        /* License Cards */
        .licenses-container {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .license-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
            transition: all 0.3s;
            border-right: 5px solid #ccc;
        }
        
        .license-card:hover {
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
        }
        
        .license-card.pending { border-color: #ff9800; }
        .license-card.active { border-color: #4caf50; }
        .license-card.blocked { border-color: #f44336; }
        .license-card.expired { border-color: #9e9e9e; }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
        }
        
        .card-header h3 {
            color: var(--dark);
            font-size: 1.4rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-badge {
            padding: 8px 20px;
            border-radius: 25px;
            font-size: 0.9rem;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-pending { background: #fff3cd; color: #856404; }
        .status-active { background: #d4edda; color: #155724; }
        .status-blocked { background: #f8d7da; color: #721c24; }
        .status-expired { background: #e2e3e5; color: #383d41; }
        
        .card-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .info-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        
        .info-icon {
            font-size: 1.2rem;
            min-width: 30px;
        }
        
        .info-item strong {
            color: #666;
            min-width: 100px;
        }
        
        .info-item span {
            color: var(--dark);
            font-weight: 500;
        }
        
        /* Action Buttons */
        .action-buttons {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-top: 25px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            font-size: 1rem;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 7px 15px rgba(0, 0, 0, 0.2);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn-approve { background: linear-gradient(135deg, #4caf50, #2e7d32); color: white; }
        .btn-block { background: linear-gradient(135deg, #f44336, #c62828); color: white; }
        .btn-renew { background: linear-gradient(135deg, #2196f3, #0d47a1); color: white; }
        .btn-details { background: linear-gradient(135deg, #ff9800, #ef6c00); color: white; }
        
        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        }
        
        .empty-state img {
            width: 150px;
            margin-bottom: 20px;
            opacity: 0.7;
        }
        
        .empty-state h3 {
            color: #666;
            margin-bottom: 10px;
            font-size: 1.5rem;
        }
        
        .empty-state p {
            color: #999;
            font-size: 1.1rem;
        }
        
        /* Loading */
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid var(--primary);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .header h1 { font-size: 2rem; }
            .stats-grid { grid-template-columns: 1fr; }
            .card-info { grid-template-columns: 1fr; }
            .card-header { flex-direction: column; align-items: flex-start; gap: 15px; }
            .action-buttons { flex-direction: column; }
            .btn { width: 100%; justify-content: center; }
        }
        
        /* Animation */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .license-card {
            animation: fadeIn 0.5s ease-out;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🚀 نظام إدارة التراخيص</h1>
            <p>إدارة وتفعيل تراخيص البرامج بكل سهولة | يعمل على Vercel</p>
        </div>
        
        <!-- Statistics -->
        <div class="stats-grid">
            <div class="stat-card stat-pending">
                <h3>⏳ الطلبات المعلقة</h3>
                <div class="count" id="pending-count">0</div>
                <p>بانتظار الموافقة</p>
            </div>
            <div class="stat-card stat-active">
                <h3>✅ التراخيص النشطة</h3>
                <div class="count" id="active-count">0</div>
                <p>قيد الاستخدام</p>
            </div>
            <div class="stat-card stat-blocked">
                <h3>❌ التراخيص المحظورة</h3>
                <div class="count" id="blocked-count">0</div>
                <p>غير مفعلة</p>
            </div>
            <div class="stat-card stat-expired">
                <h3>⏰ التراخيص المنتهية</h3>
                <div class="count" id="expired-count">0</div>
                <p>انتهت صلاحيتها</p>
            </div>
        </div>
        
        <!-- Search -->
        <div class="search-container">
            <input type="text" 
                   class="search-box" 
                   placeholder="🔍 ابحث باسم العميل، IP، المعرف، أو الحالة..."
                   onkeyup="filterLicenses()"
                   id="searchInput">
        </div>
        
        <!-- Licenses Container -->
        <div id="licenses-container" class="licenses-container">
            <div class="loading">
                <div class="loading-spinner"></div>
                <p>جاري تحميل البيانات...</p>
            </div>
        </div>
    </div>
    
    <!-- Modal for License Details -->
    <div id="licenseModal" class="modal" style="display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); align-items: center; justify-content: center;">
        <div style="background: white; padding: 30px; border-radius: 15px; max-width: 600px; width: 90%; max-height: 80vh; overflow-y: auto;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2 style="color: var(--primary);">تفاصيل الترخيص</h2>
                <button onclick="closeModal()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #666;">×</button>
            </div>
            <div id="modalContent"></div>
        </div>
    </div>
    
    <script>
        let allLicenses = [];
        let currentFilter = 'all';
        
        // Load data on page load
        document.addEventListener('DOMContentLoaded', loadData);
        
        async function loadData() {
            try {
                showLoading();
                const response = await fetch('/api/admin/data');
                if (!response.ok) throw new Error('Network error');
                
                const data = await response.json();
                allLicenses = data.licenses || [];
                
                // Sort by creation date (newest first)
                allLicenses.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
                
                displayLicenses(allLicenses);
                updateStats();
                
            } catch (error) {
                console.error('Error loading data:', error);
                document.getElementById('licenses-container').innerHTML = `
                    <div class="empty-state">
                        <div style="font-size: 3rem; margin-bottom: 20px;">😟</div>
                        <h3>خطأ في تحميل البيانات</h3>
                        <p>تأكد من اتصال الإنترنت وحاول مرة أخرى</p>
                        <button class="btn btn-renew" onclick="loadData()" style="margin-top: 20px;">
                            🔄 إعادة المحاولة
                        </button>
                    </div>
                `;
            }
        }
        
        function showLoading() {
            document.getElementById('licenses-container').innerHTML = `
                <div class="loading">
                    <div class="loading-spinner"></div>
                    <p>جاري تحميل البيانات...</p>
                </div>
            `;
        }
        
        function displayLicenses(licenses) {
            const container = document.getElementById('licenses-container');
            
            if (licenses.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div style="font-size: 3rem; margin-bottom: 20px;">📭</div>
                        <h3>لا توجد تراخيص حالياً</h3>
                        <p>سيظهر هنا الترخيص الأول عند طلبه</p>
                    </div>
                `;
                return;
            }
            
            let html = '';
            
            licenses.forEach((lic, index) => {
                const statusConfig = {
                    'pending': { text: '⏳ معلق', class: 'pending', color: '#ff9800' },
                    'active': { text: '✅ نشط', class: 'active', color: '#4caf50' },
                    'blocked': { text: '❌ محظور', class: 'blocked', color: '#f44336' },
                    'expired': { text: '⏰ منتهي', class: 'expired', color: '#9e9e9e' }
                };
                
                const status = statusConfig[lic.status] || statusConfig.pending;
                const expiresDate = lic.expires_at ? 
                    new Date(lic.expires_at).toLocaleDateString('ar-EG', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                    }) : 
                    'غير محدد';
                
                const createdDate = new Date(lic.created_at).toLocaleDateString('ar-EG', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                
                html += `
                    <div class="license-card ${status.class}" data-index="${index}">
                        <div class="card-header">
                            <h3>
                                <span style="background: ${status.color}; color: white; padding: 5px 12px; border-radius: 20px; font-size: 0.9rem; margin-right: 10px;">
                                    ${status.text}
                                </span>
                                👤 ${lic.client_name}
                            </h3>
                            <button class="btn btn-details" onclick="showLicenseDetails(${index})">
                                📋 التفاصيل
                            </button>
                        </div>
                        
                        <div class="card-info">
                            <div class="info-item">
                                <span class="info-icon">🌐</span>
                                <strong>IP:</strong>
                                <span>${lic.client_ip || 'غير معروف'}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-icon">🆔</span>
                                <strong>المعرف:</strong>
                                <span style="font-family: monospace;">${lic.hardware_id.substring(0, 20)}...</span>
                            </div>
                            <div class="info-item">
                                <span class="info-icon">📅</span>
                                <strong>التاريخ:</strong>
                                <span>${createdDate}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-icon">⏰</span>
                                <strong>الانتهاء:</strong>
                                <span>${expiresDate}</span>
                            </div>
                        </div>
                        
                        <p style="margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 10px;">
                            <strong>📝 الملاحظات:</strong> ${lic.notes || 'لا توجد ملاحظات'}
                        </p>
                        
                        <div class="action-buttons">
                            ${lic.status === 'pending' ? `
                                <button class="btn btn-approve" onclick="approveLicense('${lic.id}', 7)">
                                    ✅ تفعيل أسبوع
                                </button>
                                <button class="btn btn-approve" onclick="approveLicense('${lic.id}', 30)">
                                    ✅ تفعيل شهر
                                </button>
                                <button class="btn btn-approve" onclick="approveLicense('${lic.id}', 365)">
                                    ✅ تفعيل سنة
                                </button>
                                <button class="btn btn-block" onclick="blockLicense('${lic.id}')">
                                    ❌ رفض
                                </button>
                            ` : ''}
                            
                            ${lic.status === 'active' ? `
                                <button class="btn btn-renew" onclick="renewLicense('${lic.id}', 30)">
                                    🔄 تجديد شهر
                                </button>
                                <button class="btn btn-block" onclick="blockLicense('${lic.id}')">
                                    ❌ حظر
                                </button>
                            ` : ''}
                            
                            ${lic.status === 'blocked' ? `
                                <button class="btn btn-approve" onclick="approveLicense('${lic.id}', 30)">
                                    ✅ إعادة التفعيل
                                </button>
                            ` : ''}
                            
                            ${lic.status === 'expired' ? `
                                <button class="btn btn-renew" onclick="renewLicense('${lic.id}', 30)">
                                    🔄 تجديد
                                </button>
                            ` : ''}
                        </div>
                    </div>
                `;
            });
            
            container.innerHTML = html;
        }
        
        function showLicenseDetails(index) {
            const lic = allLicenses[index];
            
            const modalContent = document.getElementById('modalContent');
            modalContent.innerHTML = `
                <div style="margin-bottom: 20px;">
                    <h3 style="color: var(--primary); margin-bottom: 15px;">معلومات الترخيص</h3>
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 15px;">
                        <p><strong>👤 اسم العميل:</strong> ${lic.client_name}</p>
                        <p><strong>🌐 عنوان IP:</strong> ${lic.client_ip}</p>
                        <p><strong>🆔 معرف الجهاز:</strong></p>
                        <pre style="background: white; padding: 10px; border-radius: 5px; overflow-x: auto; margin: 10px 0;">${lic.hardware_id}</pre>
                        <p><strong>🔑 مفتاح الترخيص:</strong> ${lic.license_key || 'غير متاح'}</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 15px;">
                        <p><strong>📅 تاريخ الإنشاء:</strong> ${new Date(lic.created_at).toLocaleString('ar-EG')}</p>
                        <p><strong>⏰ تاريخ الانتهاء:</strong> ${lic.expires_at ? new Date(lic.expires_at).toLocaleString('ar-EG') : 'غير محدد'}</p>
                        <p><strong>📊 الحالة:</strong> ${lic.status}</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
                        <p><strong>📝 الملاحظات:</strong></p>
                        <p>${lic.notes || 'لا توجد ملاحظات'}</p>
                    </div>
                </div>
            `;
            
            document.getElementById('licenseModal').style.display = 'flex';
        }
        
        function closeModal() {
            document.getElementById('licenseModal').style.display = 'none';
        }
        
        async function approveLicense(id, days) {
            const notes = prompt('أدخل ملاحظات (اختياري):', 'تم التفعيل من الأدمن');
            if (notes === null) return;
            
            try {
                const response = await fetch(`/api/admin/approve/${id}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({days: days, notes: notes})
                });
                
                const result = await response.json();
                if (result.success) {
                    alert(`✅ تم التفعيل بنجاح!\n🔑 مفتاح الترخيص: ${result.license_key}\n⏰ المدة: ${days} يوم`);
                    loadData();
                } else {
                    alert('❌ فشل التفعيل: ' + (result.error || ''));
                }
            } catch (error) {
                alert('❌ خطأ في الاتصال بالسيرفر');
            }
        }
        
        async function blockLicense(id) {
            if (!confirm('هل أنت متأكد من حظر هذا الترخيص؟\nسيتم منع العميل من استخدام البرنامج.')) return;
            
            try {
                const response = await fetch(`/api/admin/block/${id}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                
                const result = await response.json();
                if (result.success) {
                    alert('❌ تم الحظر بنجاح!');
                    loadData();
                } else {
                    alert('❌ فشل الحظر');
                }
            } catch (error) {
                alert('❌ خطأ في الاتصال بالسيرفر');
            }
        }
        
        async function renewLicense(id, days) {
            try {
                const response = await fetch(`/api/admin/renew/${id}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({days: days})
                });
                
                const result = await response.json();
                if (result.success) {
                    alert(`🔄 تم التجديد بنجاح!\n⏰ تمت إضافة ${days} يوم`);
                    loadData();
                } else {
                    alert('❌ فشل التجديد');
                }
            } catch (error) {
                alert('❌ خطأ في الاتصال بالسيرفر');
            }
        }
        
        function filterLicenses() {
            const search = document.getElementById('searchInput').value.toLowerCase();
            const filtered = allLicenses.filter(lic => 
                lic.client_name.toLowerCase().includes(search) ||
                lic.client_ip.includes(search) ||
                lic.hardware_id.toLowerCase().includes(search) ||
                lic.status.includes(search) ||
                (lic.notes && lic.notes.toLowerCase().includes(search))
            );
            displayLicenses(filtered);
        }
        
        function updateStats() {
            const pending = allLicenses.filter(l => l.status === 'pending').length;
            const active = allLicenses.filter(l => l.status === 'active').length;
            const blocked = allLicenses.filter(l => l.status === 'blocked').length;
            const expired = allLicenses.filter(l => l.status === 'expired').length;
            
            document.getElementById('pending-count').textContent = pending;
            document.getElementById('active-count').textContent = active;
            document.getElementById('blocked-count').textContent = blocked;
            document.getElementById('expired-count').textContent = expired;
        }
        
        // Auto refresh every 30 seconds
        setInterval(loadData, 30000);
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('licenseModal');
            if (event.target === modal) {
                closeModal();
            }
        }
        
        // Handle Enter key in search
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                filterLicenses();
            }
        });
    </script>
</body>
</html>
    '''

class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path == '/' or self.path == '/admin':
                # Serve admin panel
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                admin_html = generate_admin_panel()
                self.wfile.write(admin_html.encode('utf-8'))
                
            elif self.path == '/api/admin/data':
                # Return all license data
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                licenses_data = load_data(LICENSES_FILE)
                self.wfile.write(json.dumps(licenses_data, default=str).encode('utf-8'))
                
            else:
                self.send_response(404)
                self.end_headers()
                
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
            
            try:
                data = json.loads(post_data.decode('utf-8'))
            except:
                data = {}
            
            response = {}
            
            if self.path == '/api/request_activation':
                response = self.handle_activation(data)
                
            elif self.path == '/api/check_license':
                response = self.check_license(data)
                
            elif self.path.startswith('/api/admin/approve/'):
                license_id = self.path.split('/')[-1]
                response = self.approve_license(license_id, data)
                
            elif self.path.startswith('/api/admin/block/'):
                license_id = self.path.split('/')[-1]
                response = self.block_license(license_id)
                
            elif self.path.startswith('/api/admin/renew/'):
                license_id = self.path.split('/')[-1]
                response = self.renew_license(license_id, data)
            
            else:
                self.send_response(404)
                self.end_headers()
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(response, default=str).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def handle_activation(self, data):
        """Handle activation request"""
        licenses_data = load_data(LICENSES_FILE)
        
        hardware_id = data.get('hardware_id', '').strip()
        client_name = data.get('client_name', 'مستخدم').strip()
        
        if not hardware_id or len(hardware_id) < 10:
            return {"error": "معرف الجهاز غير صالح"}
        
        # Check if already exists
        for lic in licenses_data.get("licenses", []):
            if lic.get("hardware_id") == hardware_id:
                return {
                    "status": lic.get("status", "unknown"),
                    "message": "الجهاز مسجل مسبقاً",
                    "license_key": lic.get("license_key")
                }
        
        # Create new license
        license_key = str(uuid.uuid4())[:8].upper()
        new_license = {
            "id": str(uuid.uuid4()),
            "license_key": license_key,
            "client_name": client_name,
            "client_ip": self.headers.get('X-Forwarded-For', self.headers.get('X-Real-IP', 'Unknown')),
            "hardware_id": hardware_id,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "notes": "بانتظار موافقة الأدمن"
        }
        
        licenses_data.setdefault("licenses", []).append(new_license)
        save_data(LICENSES_FILE, licenses_data)
        
        # Send notification
        ip_address = self.headers.get('X-Forwarded-For', self.headers.get('X-Real-IP', 'Unknown'))
        message = f"📥 طلب تفعيل جديد!\n\n👤 العميل: {client_name}\n🆔 المعرف: {hardware_id[:20]}...\n🌐 IP: {ip_address}\n📅 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        send_telegram_notification(message)
        
        return {
            "success": True,
            "status": "pending",
            "message": "تم إرسال طلب التفعيل. سيتم التواصل معك قريباً.",
            "request_id": new_license["id"]
        }
    
    def check_license(self, data):
        """Check license validity"""
        licenses_data = load_data(LICENSES_FILE)
        
        license_key = data.get('license_key', '').strip()
        hardware_id = data.get('hardware_id', '').strip()
        
        for lic in licenses_data.get("licenses", []):
            if lic.get("hardware_id") == hardware_id and lic.get("license_key") == license_key:
                
                if lic.get("status") == "active":
                    expires = lic.get("expires_at")
                    if expires:
                        try:
                            expires_date = datetime.fromisoformat(expires)
                            if expires_date > datetime.now():
                                return {
                                    "valid": True,
                                    "status": "active",
                                    "expires": expires,
                                    "client": lic.get("client_name"),
                                    "message": "الترخيص ساري المفعول"
                                }
                            else:
                                lic["status"] = "expired"
                                save_data(LICENSES_FILE, licenses_data)
                                return {
                                    "valid": False,
                                    "status": "expired",
                                    "message": "انتهت صلاحية الترخيص"
                                }
                        except:
                            pass
                    
                    # If no expiration date, it's permanent
                    return {
                        "valid": True,
                        "status": "active",
                        "client": lic.get("client_name"),
                        "message": "الترخيص دائم"
                    }
                
                return {
                    "valid": False,
                    "status": lic.get("status", "unknown"),
                    "message": f"حالة الترخيص: {lic.get('status', 'غير معروف')}"
                }
        
        return {
            "valid": False,
            "message": "الترخيص غير موجود أو غير صالح"
        }
    
    def approve_license(self, license_id, data):
        """Approve a license request"""
        licenses_data = load_data(LICENSES_FILE)
        
        # Find the license
        license_to_approve = None
        license_index = -1
        
        for i, lic in enumerate(licenses_data.get("licenses", [])):
            if lic.get("id") == license_id:
                license_to_approve = lic
                license_index = i
                break
        
        if not license_to_approve:
            return {"error": "الترخيص غير موجود"}
        
        # Update license
        days = int(data.get('days', 30))
        notes = data.get('notes', 'تم التفعيل من الأدمن')
        
        license_to_approve["status"] = "active"
        license_to_approve["expires_at"] = (datetime.now() + timedelta(days=days)).isoformat()
        license_to_approve["notes"] = notes
        license_to_approve["approved_at"] = datetime.now().isoformat()
        
        licenses_data["licenses"][license_index] = license_to_approve
        save_data(LICENSES_FILE, licenses_data)
        
        # Send notification
        message = f"✅ تم تفعيل ترخيص!\n\n👤 العميل: {license_to_approve.get('client_name')}\n🔑 المفتاح: {license_to_approve.get('license_key')}\n⏰ المدة: {days} يوم\n📅 الانتهاء: {license_to_approve.get('expires_at')}"
        send_telegram_notification(message)
        
        return {
            "success": True,
            "license_key": license_to_approve.get("license_key"),
            "days": days,
            "expires_at": license_to_approve.get("expires_at")
        }
    
    def block_license(self, license_id):
        """Block a license"""
        licenses_data = load_data(LICENSES_FILE)
        
        for lic in licenses_data.get("licenses", []):
            if lic.get("id") == license_id:
                lic["status"] = "blocked"
                lic["notes"] = "محظور من الأدمن"
                lic["blocked_at"] = datetime.now().isoformat()
                break
        
        save_data(LICENSES_FILE, licenses_data)
        return {"success": True}
    
    def renew_license(self, license_id, data):
        """Renew a license"""
        licenses_data = load_data(LICENSES_FILE)
        
        for lic in licenses_data.get("licenses", []):
            if lic.get("id") == license_id:
                days = int(data.get('days', 30))
                current_expires = lic.get("expires_at")
                
                if current_expires:
                    try:
                        new_expires = datetime.fromisoformat(current_expires) + timedelta(days=days)
                    except:
                        new_expires = datetime.now() + timedelta(days=days)
                else:
                    new_expires = datetime.now() + timedelta(days=days)
                
                lic["expires_at"] = new_expires.isoformat()
                lic["status"] = "active"
                lic["notes"] = f"تم التجديد لـ {days} يوم"
                break
        
        save_data(LICENSES_FILE, licenses_data)
        return {"success": True}
