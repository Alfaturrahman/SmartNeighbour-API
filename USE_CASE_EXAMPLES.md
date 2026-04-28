# 📖 Tutorial: Use Case Examples - SmartNeighbour

> Panduan step-by-step untuk use case paling umum dalam SmartNeighbour

---

## 📋 Daftar Use Case

1. [RW Membuat RT Baru](#1-rw-membuat-rt-baru)
2. [RT Mendaftarkan Warga Baru](#2-rt-mendaftarkan-warga-baru)
3. [Warga Submit Feedback & RT Reply](#3-warga-submit-feedback--rt-reply)
4. [RT Membuat Pengumuman](#4-rt-membuat-pengumuman)
5. [RW Membuat Jadwal Keamanan](#5-rw-membuat-jadwal-keamanan)
6. [Reset Password User](#6-reset-password-user)
7. [Filter & Search Data](#7-filter--search-data)
8. [View Dashboard Statistics](#8-view-dashboard-statistics)

---

## 1. RW Membuat RT Baru

### 🎯 Goal
RW ingin menambahkan RT baru ke dalam sistem dan memberikan akses login ke RT tersebut.

### 📝 Step-by-Step

#### **Step 1: RW Login**

**Frontend (`app/login/page.tsx`):**
```typescript
const handleLogin = async (e: React.FormEvent) => {
  e.preventDefault();
  
  const response = await authService.login(
    'rw@example.com',
    'password123'
  );
  
  // Save tokens & user data
  tokenManager.setTokens(response.access, response.refresh);
  tokenManager.setUser(response.user);
  
  // Redirect ke RT Management
  router.replace('/rt-management');
};
```

**API Call:**
```
POST /api/auth/login/
Body: { "email": "rw@example.com", "password": "password123" }
Response: { "access": "...", "refresh": "...", "user": {...} }
```

---

#### **Step 2: Buka RT Management Page**

**Frontend (`app/rt-management/page.tsx`):**
```typescript
useEffect(() => {
  // Verify user is RW
  const userData = localStorage.getItem('user');
  const parsedUser = JSON.parse(userData);
  
  if (parsedUser.role !== 'rw') {
    showErrorAlert('Akses Ditolak', 'Hanya RW yang dapat mengelola RT');
    router.push('/dashboard');
    return;
  }
  
  // Fetch existing RT list
  fetchRTs();
}, []);
```

---

#### **Step 3: Click "Tambah RT"**

**Frontend:**
```typescript
const openAddModal = () => {
  setEditingId(null);
  setFormData({
    name: '',
    email: '',
    phone: '',
    area: '',
    address: ''
  });
  setModalOpen(true);
};
```

**UI:**
```jsx
<button onClick={openAddModal} className="btn-primary">
  + Tambah RT
</button>

{modalOpen && (
  <Modal title="Tambah RT Baru" onClose={() => setModalOpen(false)}>
    <form onSubmit={handleSubmit}>
      <input name="name" placeholder="Nama RT (contoh: RT 01)" />
      <input name="email" placeholder="Email RT" />
      <input name="phone" placeholder="Nomor Telepon" />
      <input name="area" placeholder="Area (contoh: Blok A)" />
      <textarea name="address" placeholder="Alamat" />
      <button type="submit">Simpan</button>
    </form>
  </Modal>
)}
```

---

#### **Step 4: Isi Form & Submit**

**Frontend:**
```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setIsLoading(true);
  
  try {
    // Validasi form
    if (!formData.name || !formData.email) {
      await showErrorAlert('Error', 'Nama dan email wajib diisi');
      return;
    }
    
    // Call API create RT
    const response = await rtService.create(formData);
    
    // Response berisi credentials
    await Swal.fire({
      title: 'RT Berhasil Dibuat!',
      html: `
        <div class="text-left">
          <p><strong>Nama:</strong> ${response.data.rt_name}</p>
          <p><strong>Email:</strong> ${response.data.user_email}</p>
          <p><strong>Password:</strong> 
            <code class="bg-gray-100 px-2 py-1 rounded">
              ${response.data.generated_password}
            </code>
          </p>
          <p class="text-sm text-red-600 mt-4">
            ⚠️ Mohon catat credentials ini dan berikan ke RT untuk login
          </p>
        </div>
      `,
      icon: 'success',
      confirmButtonText: 'OK, Saya Sudah Catat'
    });
    
    // Refresh list RT
    fetchRTs();
    setModalOpen(false);
    
  } catch (error: any) {
    const errorMessage = 
      error?.error || 
      error?.detail || 
      'Gagal membuat RT';
    
    await showErrorAlert('Error', errorMessage);
  } finally {
    setIsLoading(false);
  }
};
```

**API Call:**
```
POST /api/rw/create_rt/
Headers: Authorization: Bearer <access_token>
Body: {
  "name": "RT 01",
  "email": "rt01@example.com",
  "phone": "081234567890",
  "area": "Blok A",
  "address": "Jl. Mawar No. 1"
}

Response: {
  "success": true,
  "message": "RT berhasil dibuat",
  "data": {
    "rt_id": 1,
    "rt_name": "RT 01",
    "user_email": "rt01@example.com",
    "generated_password": "passw0rd",
    "note": "Berikan email dan password ini ke RT untuk login"
  }
}
```

**Backend Process:**
1. Validate email unique
2. Create User dengan role='rt', password='passw0rd'
3. Create RT profile linked ke User
4. Link RT ke RW yang login
5. Return credentials

---

#### **Step 5: RW Kasih Credentials ke RT**

**RW Action:**
- Screenshot atau catat credentials
- Berikan ke RT via WhatsApp/Email/Langsung
- RT bisa login dengan email & password tersebut

---

#### **Step 6: RT Login Pertama Kali**

**RT opens app:**
```
Email: rt01@example.com
Password: passw0rd
```

**After login:**
- Redirect ke `/warga-management` (RT dashboard)
- RT bisa mulai manage warga

---

### ✅ Result

1. ✅ RT baru berhasil dibuat
2. ✅ User account untuk RT sudah ada
3. ✅ RT linked ke RW
4. ✅ RT bisa login dan manage warga

---

## 2. RT Mendaftarkan Warga Baru

### 🎯 Goal
RT ingin mendaftarkan warga baru ke sistem dengan data lengkap (KTP, KK, dll).

### 📝 Step-by-Step

#### **Step 1: RT Login & Buka Warga Management**

```typescript
// RT login dengan credentials yang dikasih RW
const response = await authService.login('rt01@example.com', 'passw0rd');

// Auto-redirect ke /warga-management
```

---

#### **Step 2: Click "Tambah Warga"**

**Frontend (`app/warga-management/page.tsx`):**
```typescript
const openAddModal = () => {
  setFormData({
    name: '',
    email: '',
    phone: '',
    address: '',
    ktp: '',
    kk: '',
    jumlah_keluarga: 1,
    kepala_keluarga: '',
    status: 'aktif'
  });
  setModalOpen(true);
};
```

**UI:**
```jsx
<Modal title="Tambah Warga Baru">
  <form onSubmit={handleCreateWarga}>
    {/* Data Pribadi */}
    <input name="name" placeholder="Nama Lengkap" required />
    <input name="email" placeholder="Email" required />
    <input name="phone" placeholder="Nomor Telepon" required />
    <textarea name="address" placeholder="Alamat Lengkap" required />
    
    {/* Data Kependudukan */}
    <input name="ktp" placeholder="NIK (16 digit)" maxLength={16} />
    <input name="kk" placeholder="No. KK (16 digit)" maxLength={16} />
    <input name="jumlah_keluarga" type="number" min={1} />
    <input name="kepala_keluarga" placeholder="Nama Kepala Keluarga" />
    
    {/* Status */}
    <select name="status">
      <option value="aktif">Aktif</option>
      <option value="tidak aktif">Tidak Aktif</option>
    </select>
    
    <button type="submit">Daftarkan Warga</button>
  </form>
</Modal>
```

---

#### **Step 3: Isi Form Lengkap & Submit**

**Frontend:**
```typescript
const handleCreateWarga = async (e: React.FormEvent) => {
  e.preventDefault();
  setIsLoading(true);
  
  try {
    // Validasi KTP & KK (16 digit)
    if (formData.ktp && formData.ktp.length !== 16) {
      await showErrorAlert('Error', 'NIK harus 16 digit');
      return;
    }
    
    if (formData.kk && formData.kk.length !== 16) {
      await showErrorAlert('Error', 'No. KK harus 16 digit');
      return;
    }
    
    // Call API
    const response = await wargaService.create(formData);
    
    // Show credentials
    await Swal.fire({
      title: 'Warga Berhasil Didaftarkan!',
      html: `
        <div class="text-left">
          <p><strong>Nama:</strong> ${response.data.resident_name}</p>
          <p><strong>Email:</strong> ${response.data.user_email}</p>
          <p><strong>Password:</strong> 
            <code>${response.data.generated_password}</code>
          </p>
          <p class="text-sm mt-4">
            📱 Berikan credentials ini ke warga untuk akses aplikasi
          </p>
        </div>
      `,
      icon: 'success'
    });
    
    // Refresh warga list
    fetchWarga();
    setModalOpen(false);
    
  } catch (error: any) {
    await showErrorAlert('Error', error.error || 'Gagal mendaftarkan warga');
  } finally {
    setIsLoading(false);
  }
};
```

**API Call:**
```
POST /api/rt/create_resident/
Headers: Authorization: Bearer <access_token>
Body: {
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "081234567890",
  "address": "Blok A No. 10",
  "ktp": "1234567890123456",
  "kk": "9876543210987654",
  "jumlah_keluarga": 4,
  "kepala_keluarga": "John Doe",
  "status": "aktif"
}

Response: {
  "success": true,
  "message": "Warga berhasil didaftarkan",
  "data": {
    "resident_id": 1,
    "resident_name": "John Doe",
    "user_email": "john@example.com",
    "generated_password": "passw0rd"
  }
}
```

**Backend Process:**
1. Validate email unique
2. Create User dengan role='warga'
3. Create Resident profile dengan data lengkap
4. Link Resident ke RT yang login
5. Return credentials

---

#### **Step 4: RT Kasih Credentials ke Warga**

**RT Action:**
- Print atau catat credentials
- Berikan ke warga
- Warga bisa login dan submit feedback

---

### ✅ Result

1. ✅ Warga terdaftar dengan data lengkap
2. ✅ Warga punya akun untuk login
3. ✅ Data tersimpan di RT yang benar
4. ✅ Warga bisa akses aplikasi

---

## 3. Warga Submit Feedback & RT Reply

### 🎯 Goal
Warga ingin submit keluhan, dan RT memberikan respon.

### 📝 Step-by-Step

#### **Step 1: Warga Login**

```typescript
// Warga login dengan credentials dari RT
const response = await authService.login('john@example.com', 'passw0rd');

// Auto-redirect ke /announcements (warga homepage)
```

---

#### **Step 2: Warga Buka Feedback Page**

**Frontend (`app/feedback/page.tsx`):**
```typescript
useEffect(() => {
  const userData = localStorage.getItem('user');
  const parsedUser = JSON.parse(userData);
  setUser(parsedUser);
  
  // Load feedback list
  fetchFeedbacks();
}, []);
```

**UI:**
```jsx
// Warga bisa lihat feedback di RT-nya (transparansi)
<div className="feedback-list">
  {feedbacks.map(feedback => (
    <FeedbackCard 
      key={feedback.id} 
      feedback={feedback}
      canReply={false}  // Warga tidak bisa reply
    />
  ))}
</div>

<button onClick={openAddModal}>
  + Buat Feedback Baru
</button>
```

---

#### **Step 3: Warga Submit Feedback**

**Frontend:**
```typescript
const handleSubmitFeedback = async (e: React.FormEvent) => {
  e.preventDefault();
  
  try {
    await feedbackService.create({
      title: 'Lampu Jalan Mati',
      content: 'Lampu jalan di Blok A sudah mati sejak 3 hari',
      rating: 3,  // Rating untuk kualitas layanan RT
      author: user.name || 'Warga'
    });
    
    await showSuccessAlert('Berhasil', 'Feedback berhasil dikirim');
    
    fetchFeedbacks();
    setModalOpen(false);
    
  } catch (error) {
    await showErrorAlert('Error', 'Gagal mengirim feedback');
  }
};
```

**API Call:**
```
POST /api/feedbacks/
Headers: Authorization: Bearer <access_token>
Body: {
  "title": "Lampu Jalan Mati",
  "content": "Lampu jalan di Blok A sudah mati sejak 3 hari",
  "rating": 3,
  "author": "John Doe"
}

Response: {
  "id": 1,
  "title": "Lampu Jalan Mati",
  "content": "...",
  "rating": 3,
  "author": "John Doe",
  "user_email": "john@example.com",
  "rt_name": "RT 01",
  "date": "2026-04-29",
  "reply": null
}
```

**Backend Process:**
1. Auto-set user dari token
2. Auto-set RT dari user's resident profile
3. Save feedback
4. Return feedback data

---

#### **Step 4: RT Lihat Feedback Baru**

**RT opens Feedback page:**
```typescript
// RT login
const response = await authService.login('rt01@example.com', 'passw0rd');

// Buka /feedback
const feedbacks = await feedbackService.getAll();

// Backend auto-filter: RT cuma lihat feedback di RT-nya
```

**UI RT:**
```jsx
<div className="feedback-list">
  {feedbacks.map(feedback => (
    <FeedbackCard 
      key={feedback.id}
      feedback={feedback}
      canReply={true}  // RT bisa reply
      onReply={() => openReplyModal(feedback)}
    />
  ))}
</div>
```

**Feedback Card:**
```jsx
<div className="feedback-card">
  <div className="feedback-header">
    <h3>{feedback.title}</h3>
    <span className="rating">⭐ {feedback.rating}/5</span>
  </div>
  
  <p className="feedback-content">{feedback.content}</p>
  
  <div className="feedback-meta">
    <span>👤 {feedback.author}</span>
    <span>📅 {feedback.date}</span>
  </div>
  
  {!feedback.reply && (
    <button onClick={() => onReply(feedback)}>
      💬 Balas Feedback
    </button>
  )}
  
  {feedback.reply && (
    <div className="reply-box">
      <p><strong>Balasan dari {feedback.replied_by}:</strong></p>
      <p>{feedback.reply}</p>
      <span className="text-sm">{feedback.replied_at}</span>
    </div>
  )}
</div>
```

---

#### **Step 5: RT Reply Feedback**

**Frontend:**
```typescript
const openReplyModal = (feedback: Feedback) => {
  setSelectedFeedback(feedback);
  setReplyText('');
  setReplyModalOpen(true);
};

const handleReplyFeedback = async (e: React.FormEvent) => {
  e.preventDefault();
  
  try {
    await feedbackService.reply(
      selectedFeedback.id,
      replyText,
      user.name || 'RT'
    );
    
    await showSuccessAlert('Berhasil', 'Balasan berhasil dikirim');
    
    fetchFeedbacks();
    setReplyModalOpen(false);
    
  } catch (error) {
    await showErrorAlert('Error', 'Gagal mengirim balasan');
  }
};
```

**Modal UI:**
```jsx
<Modal title="Balas Feedback">
  <div className="original-feedback">
    <h4>{selectedFeedback?.title}</h4>
    <p>{selectedFeedback?.content}</p>
    <small>Dari: {selectedFeedback?.author}</small>
  </div>
  
  <form onSubmit={handleReplyFeedback}>
    <textarea
      value={replyText}
      onChange={(e) => setReplyText(e.target.value)}
      placeholder="Tulis balasan Anda..."
      required
      rows={6}
    />
    <button type="submit">Kirim Balasan</button>
  </form>
</Modal>
```

**API Call:**
```
POST /api/feedbacks/1/reply/
Headers: Authorization: Bearer <access_token>
Body: {
  "reply": "Terima kasih atas laporannya. Kami akan segera perbaiki lampu tersebut.",
  "replied_by": "RT 01"
}

Response: {
  "id": 1,
  "title": "Lampu Jalan Mati",
  "reply": "Terima kasih atas laporannya...",
  "replied_by": "RT 01",
  "replied_at": "2026-04-29T14:30:00Z"
}
```

---

#### **Step 6: Warga Lihat Reply**

**Warga opens Feedback page:**
```typescript
// Refresh feedback list
const feedbacks = await feedbackService.getAll();

// Feedback dengan reply akan tampil di list
```

**UI:**
```jsx
<div className="feedback-card">
  <h3>Lampu Jalan Mati</h3>
  <p>Lampu jalan di Blok A sudah mati sejak 3 hari</p>
  <span>✅ Sudah Dibalas</span>
  
  <div className="reply-box bg-green-50">
    <p><strong>💬 Balasan dari RT 01:</strong></p>
    <p>Terima kasih atas laporannya. Kami akan segera perbaiki...</p>
    <small>2026-04-29 14:30</small>
  </div>
</div>
```

---

### ✅ Result

1. ✅ Warga berhasil submit feedback
2. ✅ RT ternotifikasi ada feedback baru
3. ✅ RT kasih respon cepat
4. ✅ Warga lihat balasan
5. ✅ Transparansi: semua warga bisa lihat feedback & reply

---

## 4. RT Membuat Pengumuman

### 🎯 Goal
RT ingin membuat pengumuman penting untuk warga di RT-nya.

### 📝 Step-by-Step

#### **Step 1: RT Buka Announcements Page**

```typescript
// RT sudah login
router.push('/announcements');
```

---

#### **Step 2: Click "Buat Pengumuman"**

**Frontend (`app/announcements/page.tsx`):**
```typescript
const openAddModal = () => {
  const permissions = getPermissions(userRole);
  
  if (!permissions.canCreateAnnouncement) {
    showErrorAlert('Akses Ditolak', 'Hanya RT/RW yang bisa buat pengumuman');
    return;
  }
  
  setForm Data({
    title: '',
    content: '',
    priority: 'medium'
  });
  setModalOpen(true);
};
```

---

#### **Step 3: Isi Form & Pilih Priority**

**UI:**
```jsx
<Modal title="Buat Pengumuman">
  <form onSubmit={handleCreateAnnouncement}>
    <input 
      name="title" 
      placeholder="Judul Pengumuman"
      required 
    />
    
    <textarea 
      name="content" 
      placeholder="Isi Pengumuman"
      rows={8}
      required 
    />
    
    <select name="priority">
      <option value="low">🟢 Info Biasa</option>
      <option value="medium">🟡 Penting</option>
      <option value="high">🔴 Urgent</option>
    </select>
    
    <button type="submit">Publikasikan</button>
  </form>
</Modal>
```

**Frontend:**
```typescript
const handleCreateAnnouncement = async (e: React.FormEvent) => {
  e.preventDefault();
  
  try {
    await announcementService.create({
      title: 'Iuran Bulanan April 2026',
      content: 'Mohon segera melakukan pembayaran iuran bulanan...',
      priority: 'high'
    });
    
    await showSuccessAlert('Berhasil', 'Pengumuman berhasil dipublikasikan');
    
    fetchAnnouncements();
    setModalOpen(false);
    
  } catch (error) {
    await showErrorAlert('Error', 'Gagal membuat pengumuman');
  }
};
```

**API Call:**
```
POST /api/announcements/
Headers: Authorization: Bearer <access_token>
Body: {
  "title": "Iuran Bulanan April 2026",
  "content": "Mohon segera melakukan pembayaran iuran bulanan...",
  "priority": "high"
}

Response: {
  "id": 1,
  "title": "Iuran Bulanan April 2026",
  "content": "...",
  "priority": "high",
  "author": "RT 01",
  "rt_name": "RT 01",
  "date": "2026-04-29"
}
```

**Backend Process:**
1. Auto-set user dari token
2. Auto-set RT dari user's rt_profile
3. Auto-set author dari user.name
4. Save announcement
5. Return announcement data

---

#### **Step 4: Warga Lihat Pengumuman**

**Warga opens app:**
```typescript
// Warga login → Auto-redirect ke /announcements
const announcements = await announcementService.getAll();

// Backend auto-filter: Warga cuma lihat announcements di RT-nya
```

**UI:**
```jsx
<div className="announcements-list">
  {announcements.map(announcement => (
    <AnnouncementCard key={announcement.id} data={announcement} />
  ))}
</div>

// Priority-based styling
const getPriorityStyle = (priority: string) => {
  switch (priority) {
    case 'high':
      return 'border-l-4 border-red-500 bg-red-50';
    case 'medium':
      return 'border-l-4 border-yellow-500 bg-yellow-50';
    case 'low':
      return 'border-l-4 border-green-500 bg-green-50';
  }
};

<div className={`announcement-card ${getPriorityStyle(priority)}`}>
  <div className="flex justify-between">
    <h3>{announcement.title}</h3>
    <span className={`priority-badge ${priority}`}>
      {priority === 'high' && '🔴 URGENT'}
      {priority === 'medium' && '🟡 Penting'}
      {priority === 'low' && '🟢 Info'}
    </span>
  </div>
  
  <p>{announcement.content}</p>
  
  <div className="meta">
    <span>📢 {announcement.author}</span>
    <span>📅 {announcement.date}</span>
  </div>
</div>
```

---

### ✅ Result

1. ✅ Pengumuman terpublikasi
2. ✅ Semua warga di RT bisa lihat
3. ✅ Priority clear (urgent/penting/info)
4. ✅ Real-time notification (kalau pakai websocket/polling)

---

## 5. RW Membuat Jadwal Keamanan

### 🎯 Goal
RW ingin membuat jadwal jaga keamanan untuk petugas security.

### 📝 Step-by-Step

#### **Step 1: RW Tambah Master Data Petugas Dulu**

**Frontend (`app/security-personnel/page.tsx`):**
```typescript
const handleCreatePersonnel = async (e: React.FormEvent) => {
  e.preventDefault();
  
  try {
    await securityPersonnelService.create({
      name: 'Budi Santoso',
      phone: '081234567890',
      email: 'budi@example.com',
      address: 'Jl. Merdeka No. 1',
      area: 'Blok A-C',
      status: 'aktif',
      notes: 'Tersedia shift malam'
    });
    
    await showSuccessAlert('Berhasil', 'Petugas berhasil ditambahkan');
    fetchPersonnel();
    
  } catch (error) {
    await showErrorAlert('Error', 'Gagal menambahkan petugas');
  }
};
```

---

#### **Step 2: Buat Jadwal Keamanan**

**Frontend (`app/security-schedule/page.tsx`):**
```typescript
const handleCreateSchedule = async (e: React.FormEvent) => {
  e.preventDefault();
  
  try {
    // Weekly Schedule (Setiap Senin bulan Mei 2026)
    await securityScheduleService.create({
      name: 'Budi Santoso',  // Nama petugas dari master data
      shift: 'Pagi',  // 'Pagi', 'Siang', 'Malam'
      schedule_type: 'weekly',
      start_date: '2026-05-01',
      end_date: '2026-05-31',
      weekday: 0,  // 0=Senin, 1=Selasa, ..., 6=Minggu
      time: '08:00 - 16:00',
      status: 'aktif',
      notes: 'Gerbang utama'
    });
    
    await showSuccessAlert('Berhasil', 'Jadwal berhasil dibuat');
    fetchSchedules();
    
  } catch (error) {
    await showErrorAlert('Error', error.error || 'Gagal membuat jadwal');
  }
};
```

**API Call:**
```
POST /api/security-schedules/
Headers: Authorization: Bearer <access_token>
Body: {
  "name": "Budi Santoso",
  "shift": "Pagi",
  "schedule_type": "weekly",
  "start_date": "2026-05-01",
  "end_date": "2026-05-31",
  "weekday": 0,
  "time": "08:00 - 16:00",
  "status": "aktif",
  "notes": "Gerbang utama"
}

Response: {
  "id": 1,
  "name": "Budi Santoso",
  "shift": "Pagi",
  "schedule_type": "weekly",
  "personnel_name": "Budi Santoso",
  "personnel_phone": "081234567890",
  "personnel_email": "budi@example.com",
  "weekday": 0,
  "start_date": "2026-05-01",
  "end_date": "2026-05-31",
  "time": "08:00 - 16:00",
  "status": "aktif"
}
```

**Backend Process:**
1. Validate ada petugas aktif
2. Link petugas by name (auto-match dari master data)
3. Validate date range
4. Save schedule
5. Return schedule dengan data petugas

---

#### **Step 3: Lihat Jadwal di Calendar View**

**Frontend (`app/jadwal-jaga/page.tsx`):**
```typescript
const fetchSchedules = async () => {
  const response = await securityScheduleService.getAll({
    shift: 'Pagi',  // Optional filter
    date: '2026-05-15'  // Optional filter
  });
  
  const schedules = response.results || [];
  
  // Group by date untuk calendar view
  const grouped = groupSchedulesByDate(schedules);
  setCalendarData(grouped);
};

// Calendar component
<Calendar 
  data={calendarData}
  renderDay={(date, schedules) => (
    <div className="day-cell">
      <div className="date">{date.getDate()}</div>
      {schedules.map(schedule => (
        <div key={schedule.id} className="schedule-item">
          <span className="shift">{schedule.shift}</span>
          <span className="name">{schedule.personnel_name}</span>
          <span className="time">{schedule.time}</span>
        </div>
      ))}
    </div>
  )}
/>
```

---

### ✅ Result

1. ✅ Master data petugas tersimpan
2. ✅ Jadwal keamanan terstruktur
3. ✅ Support daily/weekly/monthly
4. ✅ Calendar view untuk visualisasi
5. ✅ Auto-link ke data petugas

---

## 6. Reset Password User

### 🎯 Goal
RW ingin reset password RT yang lupa password.

### 📝 Step-by-Step

#### **Step 1: RT Lupa Password & Hubungi RW**

**RT:** "Pak RW, saya lupa password"

---

#### **Step 2: RW Login & Buka RT Management**

```typescript
const response = await authService.login('rw@example.com', 'password123');
router.push('/rt-management');
```

---

#### **Step 3: RW Click "Reset Password" di RT Card**

**Frontend:**
```jsx
<div className="rt-card">
  <h3>{rt.name}</h3>
  <p>{rt.user_email}</p>
  
  <div className="actions">
    <button onClick={() => handleEdit(rt)}>✏️ Edit</button>
    <button onClick={() => handleResetPassword(rt.id)}>🔑 Reset Password</button>
    <button onClick={() => handleDelete(rt.id)}>🗑️ Hapus</button>
  </div>
</div>
```

---

#### **Step 4: Confirm & Reset**

**Frontend:**
```typescript
const handleResetPassword = async (rtId: number) => {
  // Confirm dialog
  const confirmed = await showConfirmAlert(
    'Reset Password RT?',
    'Password akan direset ke default. RT harus login ulang.'
  );
  
  if (!confirmed) return;
  
  try {
    setIsLoading(true);
    
    const response = await rtService.resetPassword(rtId);
    
    // Show new password
    await Swal.fire({
      title: 'Password Berhasil Direset!',
      html: `
        <div>
          <p><strong>Email:</strong> ${response.data.user_email}</p>
          <p><strong>Password Baru:</strong>
            <code class="bg-gray-100 px-3 py-2 rounded">
              ${response.data.new_password}
            </code>
          </p>
          <p class="text-sm text-blue-600 mt-4">
            📱 Berikan password baru ini ke RT
          </p>
        </div>
      `,
      icon: 'success',
      confirmButtonText: 'OK, Saya Sudah Catat'
    });
    
  } catch (error) {
    await showErrorAlert('Error', 'Gagal reset password');
  } finally {
    setIsLoading(false);
  }
};
```

**API Call:**
```
POST /api/rw/1/reset_password/
Headers: Authorization: Bearer <access_token>

Response: {
  "success": true,
  "message": "Password RT berhasil direset",
  "data": {
    "rt_id": 1,
    "rt_name": "RT 01",
    "user_email": "rt01@example.com",
    "new_password": "passw0rd"
  }
}
```

---

#### **Step 5: RW Kasih Password Baru ke RT**

**RW → RT via WhatsApp:**
```
Password Anda sudah direset

Email: rt01@example.com
Password: passw0rd

Silakan login ulang
```

---

#### **Step 6: RT Login dengan Password Baru**

```typescript
const response = await authService.login('rt01@example.com', 'passw0rd');
// Success! RT bisa akses lagi
```

---

### ✅ Result

1. ✅ RT bisa akses kembali
2. ✅ Password direset ke default
3. ✅ RT bisa ganti password nanti (future feature)

---

## 7. Filter & Search Data

### 🎯 Goal
RT ingin cari data warga dengan multiple criteria.

### 📝 Step-by-Step

**Frontend (`app/warga-management/page.tsx`):**

#### **Search by Name/Email:**
```typescript
const handleSearch = (value: string) => {
  setSearchTerm(value);
  
  // Debounce untuk performance
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    fetchWarga({ search: value });
  }, 500);
};

<input 
  type="search"
  placeholder="Cari nama atau email..."
  onChange={(e) => handleSearch(e.target.value)}
/>
```

#### **Filter by Status:**
```typescript
const handleFilterStatus = (status: string) => {
  setStatusFilter(status);
  fetchWarga({ status });
};

<select onChange={(e) => handleFilterStatus(e.target.value)}>
  <option value="">Semua Status</option>
  <option value="aktif">Aktif</option>
  <option value="tidak aktif">Tidak Aktif</option>
</select>
```

#### **Combined Filters:**
```typescript
const fetchWarga = async (params?: any) => {
  try {
    setIsLoading(true);
    
    const response = await residentService.getAll({
      page: currentPage,
      limit: 20,
      search: searchTerm,
      status: statusFilter,
      ...params
    });
    
    const data = response.results || [];
    setWarga(data);
    
  } catch (error) {
    await showErrorAlert('Error', 'Gagal memuat data');
  } finally {
    setIsLoading(false);
  }
};
```

**API Call:**
```
GET /api/residents/?search=john&status=aktif&page=1&limit=20
Headers: Authorization: Bearer <access_token>

Response: {
  "results": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "status": "aktif"
      ...
    }
  ],
  "count": 1,
  "next": null,
  "previous": null
}
```

---

### ✅ Result

1. ✅ Search real-time dengan debounce
2. ✅ Filter by status
3. ✅ Multiple filters combined
4. ✅ Pagination support

---

## 8. View Dashboard Statistics

### 🎯 Goal
RW ingin lihat statistik lengkap di dashboard.

### 📝 Step-by-Step

**Frontend (`app/dashboard/page.tsx`):**
```typescript
useEffect(() => {
  const fetchStats = async () => {
    try {
      const [residentStats, feedbackStats, rtList] = await Promise.all([
        residentService.getStats(),
        feedbackService.getStats(),
        rtService.getAll()
      ]);
      
      setStats({
        totalWarga: residentStats.total,
        wargaAktif: residentStats.active,
        totalRT: rtList.length,
        totalFeedback: feedbackStats.total,
        averageRating: feedbackStats.average_rating,
        unrepliedFeedback: feedbackStats.unreplied
      });
      
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };
  
  fetchStats();
}, []);
```

**UI:**
```jsx
<div className="dashboard-grid">
  {/* Warga Stats */}
  <StatCard 
    icon="👥"
    title="Total Warga"
    value={stats.totalWarga}
    subtitle={`${stats.wargaAktif} aktif`}
    color="blue"
  />
  
  {/* RT Stats */}
  <StatCard 
    icon="🏘️"
    title="Total RT"
    value={stats.totalRT}
    subtitle="Rukun Tetangga"
    color="green"
  />
  
  {/* Feedback Stats */}
  <StatCard 
    icon="💬"
    title="Total Feedback"
    value={stats.totalFeedback}
    subtitle={`${stats.unrepliedFeedback} belum dibalas`}
    color="yellow"
  />
  
  {/* Rating Stats */}
  <StatCard 
    icon="⭐"
    title="Rating Rata-rata"
    value={stats.averageRating.toFixed(1)}
    subtitle="dari 5.0"
    color="purple"
  />
</div>

{/* Recent Activity */}
<div className="recent-activity">
  <h2>Aktivitas Terbaru</h2>
  {/* List recent feedbacks, announcements, etc */}
</div>
```

**API Calls:**
```
GET /api/residents/stats/
GET /api/feedbacks/stats/
GET /api/rt/
```

---

### ✅ Result

1. ✅ Overview dashboard dengan stats
2. ✅ Real-time data
3. ✅ Quick insights
4. ✅ Easy monitoring

---

## 🎯 Summary

Semua use case di atas menunjukkan **complete flow** dari:
- Login & Authentication
- CRUD Operations
- Role-Based Access Control
- Error Handling
- UI/UX Best Practices

**Key Points:**
✅ **Backend handle complex logic** - Frontend simple  
✅ **Auto-filtering by role** - Secure & efficient  
✅ **Clear error messages** - Better UX  
✅ **Credentials management** - Secure onboarding  
✅ **Real-time updates** - Refresh after action  

---

**Lihat juga:**
- [DOKUMENTASI_KODE.md](./DOKUMENTASI_KODE.md) - Dokumentasi lengkap
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - API quick reference

**Last Updated**: April 29, 2026
