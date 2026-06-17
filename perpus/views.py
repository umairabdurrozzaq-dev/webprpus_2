from django.shortcuts import render, redirect
from django.db import connection
from .models import Buku, Siswa, Peminjaman

# ==================== 📊 DASHBOARD ====================
def dashboard(request):
    # Mengambil ringkasan data langsung dari database dengan raw SQL
    with connection.cursor() as cursor:
        # Total stok buku
        cursor.execute("SELECT COALESCE(SUM(stok), 0) FROM perpus_buku")
        total_buku = cursor.fetchone()[0]
        
        # Total judul buku
        cursor.execute("SELECT COUNT(*) FROM perpus_buku")
        total_judul = cursor.fetchone()[0]
        
        # Peminjaman sedang dipinjam
        cursor.execute("SELECT COUNT(*) FROM perpus_peminjaman WHERE status = 'Dipinjam'")
        sedang_dipinjam = cursor.fetchone()[0]
        
        # Peminjaman sudah dikembalikan
        cursor.execute("SELECT COUNT(*) FROM perpus_peminjaman WHERE status = 'Dikembalikan'")
        sudah_dikembalikan = cursor.fetchone()[0]
        
        # 5 buku dengan stok terbanyak
        cursor.execute("""
            SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, isbn, deskripsi
            FROM perpus_buku
            ORDER BY stok DESC
            LIMIT 5
        """)
        distribusi_stok = [
            type('obj', (object,), {
                'id': row[0], 'judul': row[1], 'pengarang': row[2], 'kategori': row[3],
                'penerbit': row[4], 'tahun_terbit': row[5], 'rak': row[6], 'stok': row[7],
                'isbn': row[8], 'deskripsi': row[9]
            })() for row in cursor.fetchall()
        ]
        
        # Distribusi peminjaman per buku
        cursor.execute("""
            SELECT 
                b.id, b.judul, b.pengarang, b.kategori, b.penerbit, b.tahun_terbit, b.rak, b.stok, b.isbn, b.deskripsi,
                COUNT(CASE WHEN p.status = 'Dipinjam' THEN 1 END) as sedang_dipinjam,
                COUNT(CASE WHEN p.status = 'Dikembalikan' THEN 1 END) as sudah_dikembalikan
            FROM perpus_buku b
            LEFT JOIN perpus_peminjaman p ON b.id = p.buku_id
            GROUP BY b.id
            HAVING COUNT(CASE WHEN p.status = 'Dipinjam' THEN 1 END) > 0 
                OR COUNT(CASE WHEN p.status = 'Dikembalikan' THEN 1 END) > 0
            LIMIT 5
        """)
        distribusi_peminjaman = [
            type('obj', (object,), {
                'id': row[0], 'judul': row[1], 'pengarang': row[2], 'kategori': row[3],
                'penerbit': row[4], 'tahun_terbit': row[5], 'rak': row[6], 'stok': row[7],
                'isbn': row[8], 'deskripsi': row[9], 'sedang_dipinjam': row[10],
                'sudah_dikembalikan': row[11]
            })() for row in cursor.fetchall()
        ]
    
    context = {
        'total_buku': total_buku,
        'total_judul': total_judul,
        'sedang_dipinjam': sedang_dipinjam,
        'sudah_dikembalikan': sudah_dikembalikan,
        'distribusi_stok': distribusi_stok,
        'distribusi_peminjaman': distribusi_peminjaman,
        'segment': 'dashboard'
    }
    return render(request, 'dashboard.html', context)


# ==================== 📚 MODUL BUKU ====================
def list_buku(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, isbn, deskripsi
            FROM perpus_buku
            ORDER BY id DESC
        """)
        buku_list = [
            type('obj', (object,), {
                'id': row[0], 'judul': row[1], 'pengarang': row[2], 'kategori': row[3],
                'penerbit': row[4], 'tahun_terbit': row[5], 'rak': row[6], 'stok': row[7],
                'isbn': row[8], 'deskripsi': row[9]
            })() for row in cursor.fetchall()
        ]
    return render(request, 'buku/list.html', {'buku_list': buku_list, 'segment': 'buku'})

def tambah_buku(request):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO perpus_buku (judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, isbn, deskripsi)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                request.POST.get('judul'),
                request.POST.get('pengarang'),
                request.POST.get('kategori'),
                request.POST.get('penerbit'),
                request.POST.get('tahun_terbit'),
                request.POST.get('rak'),
                request.POST.get('stok'),
                request.POST.get('isbn'),
                request.POST.get('deskripsi')
            ])
        return redirect('list_buku')
    return render(request, 'buku/form.html', {'segment': 'buku'})

def detail_buku(request, pk):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, isbn, deskripsi
            FROM perpus_buku
            WHERE id = %s
        """, [pk])
        row = cursor.fetchone()
        if not row:
            return render(request, '404.html', status=404)
        buku = type('obj', (object,), {
            'id': row[0], 'judul': row[1], 'pengarang': row[2], 'kategori': row[3],
            'penerbit': row[4], 'tahun_terbit': row[5], 'rak': row[6], 'stok': row[7],
            'isbn': row[8], 'deskripsi': row[9]
        })()
    return render(request, 'buku/detail.html', {'buku': buku, 'segment': 'buku'})

def edit_buku(request, pk):
    with connection.cursor() as cursor:
        # Check if buku exists
        cursor.execute("SELECT id FROM perpus_buku WHERE id = %s", [pk])
        if not cursor.fetchone():
            return render(request, '404.html', status=404)
        
        if request.method == 'POST':
            cursor.execute("""
                UPDATE perpus_buku
                SET judul = %s, pengarang = %s, kategori = %s, penerbit = %s, 
                    tahun_terbit = %s, rak = %s, stok = %s, isbn = %s, deskripsi = %s
                WHERE id = %s
            """, [
                request.POST.get('judul'),
                request.POST.get('pengarang'),
                request.POST.get('kategori'),
                request.POST.get('penerbit'),
                request.POST.get('tahun_terbit'),
                request.POST.get('rak'),
                request.POST.get('stok'),
                request.POST.get('isbn'),
                request.POST.get('deskripsi'),
                pk
            ])
            return redirect('list_buku')
        
        # Get existing data for form
        cursor.execute("""
            SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, isbn, deskripsi
            FROM perpus_buku
            WHERE id = %s
        """, [pk])
        row = cursor.fetchone()
        buku = type('obj', (object,), {
            'id': row[0], 'judul': row[1], 'pengarang': row[2], 'kategori': row[3],
            'penerbit': row[4], 'tahun_terbit': row[5], 'rak': row[6], 'stok': row[7],
            'isbn': row[8], 'deskripsi': row[9]
        })()
    
    return render(request, 'buku/form.html', {'buku': buku, 'segment': 'buku'})

def hapus_buku(request, pk):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM perpus_buku WHERE id = %s", [pk])
        buku_row = cursor.fetchone()
        if not buku_row:
            return render(request, '404.html', status=404)
        
        if request.method == 'POST':
            cursor.execute("DELETE FROM perpus_buku WHERE id = %s", [pk])
            return redirect('list_buku')
        
        cursor.execute("""
            SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, isbn, deskripsi
            FROM perpus_buku
            WHERE id = %s
        """, [pk])
        row = cursor.fetchone()
        buku = type('obj', (object,), {
            'id': row[0], 'judul': row[1], 'pengarang': row[2], 'kategori': row[3],
            'penerbit': row[4], 'tahun_terbit': row[5], 'rak': row[6], 'stok': row[7],
            'isbn': row[8], 'deskripsi': row[9]
        })()
    
    return render(request, 'buku/hapus_konfirmasi.html', {'buku': buku, 'segment': 'buku'})


# ==================== 👥 MODUL SISWA (USER) ====================
def list_user(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, nama, kelas, nis, is_active
            FROM perpus_siswa
            ORDER BY id DESC
        """)
        user_list = [
            type('obj', (object,), {
                'id': row[0], 'nama': row[1], 'kelas': row[2], 'nis': row[3], 'is_active': row[4]
            })() for row in cursor.fetchall()
        ]
    return render(request, 'user/list.html', {'user_list': user_list, 'segment': 'user'})

def tambah_user(request):
    if request.method == 'POST':
        is_active = True if request.POST.get('status') == 'Aktif' else False
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO perpus_siswa (nama, kelas, nis, is_active)
                VALUES (%s, %s, %s, %s)
            """, [
                request.POST.get('nama'),
                request.POST.get('kelas'),
                request.POST.get('nis'),
                is_active
            ])
        return redirect('list_user')
    return render(request, 'user/form.html', {'segment': 'user'})

def detail_user(request, pk):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, nama, kelas, nis, is_active
            FROM perpus_siswa
            WHERE id = %s
        """, [pk])
        row = cursor.fetchone()
        if not row:
            return render(request, '404.html', status=404)
        user = type('obj', (object,), {
            'id': row[0], 'nama': row[1], 'kelas': row[2], 'nis': row[3], 'is_active': row[4]
        })()
        
        # Total peminjaman user
        cursor.execute("SELECT COUNT(*) FROM perpus_peminjaman WHERE siswa_id = %s", [pk])
        total_pinjam = cursor.fetchone()[0]
        
        # Peminjaman aktif (sedang dipinjam)
        cursor.execute("SELECT COUNT(*) FROM perpus_peminjaman WHERE siswa_id = %s AND status = 'Dipinjam'", [pk])
        pinjam_aktif = cursor.fetchone()[0]
    
    context = {'user': user, 'total_pinjam': total_pinjam, 'pinjam_aktif': pinjam_aktif, 'segment': 'user'}
    return render(request, 'user/detail.html', context)

def edit_user(request, pk):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM perpus_siswa WHERE id = %s", [pk])
        if not cursor.fetchone():
            return render(request, '404.html', status=404)
        
        if request.method == 'POST':
            is_active = True if request.POST.get('status') == 'Aktif' else False
            cursor.execute("""
                UPDATE perpus_siswa
                SET nama = %s, kelas = %s, nis = %s, is_active = %s
                WHERE id = %s
            """, [
                request.POST.get('nama'),
                request.POST.get('kelas'),
                request.POST.get('nis'),
                is_active,
                pk
            ])
            return redirect('list_user')
        
        cursor.execute("""
            SELECT id, nama, kelas, nis, is_active
            FROM perpus_siswa
            WHERE id = %s
        """, [pk])
        row = cursor.fetchone()
        user = type('obj', (object,), {
            'id': row[0], 'nama': row[1], 'kelas': row[2], 'nis': row[3], 'is_active': row[4]
        })()
    
    return render(request, 'user/form.html', {'user': user, 'segment': 'user'})

def hapus_user(request, pk):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM perpus_siswa WHERE id = %s", [pk])
        if not cursor.fetchone():
            return render(request, '404.html', status=404)
        
        if request.method == 'POST':
            cursor.execute("DELETE FROM perpus_siswa WHERE id = %s", [pk])
            return redirect('list_user')
        
        cursor.execute("""
            SELECT id, nama, kelas, nis, is_active
            FROM perpus_siswa
            WHERE id = %s
        """, [pk])
        row = cursor.fetchone()
        user = type('obj', (object,), {
            'id': row[0], 'nama': row[1], 'kelas': row[2], 'nis': row[3], 'is_active': row[4]
        })()
    
    return render(request, 'user/hapus_konfirmasi.html', {'user': user, 'segment': 'user'})


# ==================== 📑 MODUL PEMINJAMAN ====================
def list_peminjaman(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                p.id, p.siswa_id, p.buku_id, p.tanggal_pinjam, p.jatuh_tempo, 
                p.keperluan, p.status, s.nama, b.judul
            FROM perpus_peminjaman p
            JOIN perpus_siswa s ON p.siswa_id = s.id
            JOIN perpus_buku b ON p.buku_id = b.id
            ORDER BY p.id DESC
        """)
        peminjaman_list = [
            type('obj', (object,), {
                'id': row[0], 'siswa_id': row[1], 'buku_id': row[2], 'tanggal_pinjam': row[3],
                'jatuh_tempo': row[4], 'keperluan': row[5], 'status': row[6],
                'siswa': type('obj', (object,), {'nama': row[7]})(),
                'buku': type('obj', (object,), {'judul': row[8]})()
            })() for row in cursor.fetchall()
        ]
    return render(request, 'peminjaman/list.html', {'peminjaman_list': peminjaman_list, 'segment': 'peminjaman'})

def tambah_peminjaman(request):
    if request.method == 'POST':
        siswa_id = request.POST.get('siswa_id')
        buku_id = request.POST.get('buku_id')
        
        with connection.cursor() as cursor:
            # Check if siswa exists
            cursor.execute("SELECT id FROM perpus_siswa WHERE id = %s AND is_active = 1", [siswa_id])
            if not cursor.fetchone():
                return render(request, '404.html', status=404)
            
            # Check if buku exists and has stok
            cursor.execute("SELECT stok FROM perpus_buku WHERE id = %s AND stok > 0", [buku_id])
            if not cursor.fetchone():
                return render(request, '404.html', status=404)
            
            # Create peminjaman
            cursor.execute("""
                INSERT INTO perpus_peminjaman (siswa_id, buku_id, tanggal_pinjam, jatuh_tempo, keperluan, status)
                VALUES (%s, %s, %s, %s, %s, 'Dipinjam')
            """, [
                siswa_id,
                buku_id,
                request.POST.get('tanggal_pinjam'),
                request.POST.get('jatuh_tempo'),
                request.POST.get('keperluan')
            ])
            
            # Decrease stok
            cursor.execute("""
                UPDATE perpus_buku
                SET stok = stok - 1
                WHERE id = %s
            """, [buku_id])
        
        return redirect('list_peminjaman')
    
    with connection.cursor() as cursor:
        # Get active students
        cursor.execute("""
            SELECT id, nama, kelas, nis
            FROM perpus_siswa
            WHERE is_active = 1
            ORDER BY nama
        """)
        siswa_choices = [
            type('obj', (object,), {
                'id': row[0], 'nama': row[1], 'kelas': row[2], 'nis': row[3]
            })() for row in cursor.fetchall()
        ]
        
        # Get books with stok > 0
        cursor.execute("""
            SELECT id, judul, pengarang, stok
            FROM perpus_buku
            WHERE stok > 0
            ORDER BY judul
        """)
        buku_choices = [
            type('obj', (object,), {
                'id': row[0], 'judul': row[1], 'pengarang': row[2], 'stok': row[3]
            })() for row in cursor.fetchall()
        ]
    
    return render(request, 'peminjaman/form.html', {
        'siswa_choices': siswa_choices,
        'buku_choices': buku_choices,
        'segment': 'peminjaman'
    })

def kembalikan_buku(request, pk):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            # Check if peminjaman exists and status is 'Dipinjam'
            cursor.execute("SELECT buku_id FROM perpus_peminjaman WHERE id = %s AND status = 'Dipinjam'", [pk])
            row = cursor.fetchone()
            if row:
                buku_id = row[0]
                
                # Update peminjaman status
                cursor.execute("""
                    UPDATE perpus_peminjaman
                    SET status = 'Dikembalikan'
                    WHERE id = %s
                """, [pk])
                
                # Increase stok
                cursor.execute("""
                    UPDATE perpus_buku
                    SET stok = stok + 1
                    WHERE id = %s
                """, [buku_id])
    
    return redirect('list_peminjaman')