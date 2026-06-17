from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count, Q  # TAMBAHKAN Count dan Q di sini
from .models import Buku, Siswa, Peminjaman

# ==================== 📊 DASHBOARD ====================
def dashboard(request):
    # Mengambil ringkasan data langsung dari database lewat ORM
    total_buku = Buku.objects.aggregate(total=Sum('stok'))['total'] or 0
    total_judul = Buku.objects.count()
    sedang_dipinjam = Peminjaman.objects.filter(status='Dipinjam').count()
    sudah_dikembalikan = Peminjaman.objects.filter(status='Dikembalikan').count()
    
    # Ambil 5 buku dengan stok terbanyak untuk chart analisis stok
    distribusi_stok = Buku.objects.order_by('-stok')[:5]
    
    # PERBAIKAN: Ambil data distribusi peminjaman per buku
    # Query ini akan menghitung relasi peminjaman pada model Buku yang berstatus 'Dipinjam'
    # PERBAIKAN: Ambil buku yang sedang dipinjam > 0 ATAU sudah dikembalikan > 0
    distribusi_peminjaman = Buku.objects.annotate(
        sedang_dipinjam=Count('peminjaman', filter=Q(peminjaman__status='Dipinjam')),
        sudah_dikembalikan=Count('peminjaman', filter=Q(peminjaman__status='Dikembalikan'))
    ).filter(
        Q(sedang_dipinjam__gt=0) | Q(sudah_dikembalikan__gt=0)
    ).distinct()[:5]
    
    context = {
        'total_buku': total_buku,
        'total_judul': total_judul,
        'sedang_dipinjam': sedang_dipinjam,
        'sudah_dikembalikan': sudah_dikembalikan,
        'distribusi_stok': distribusi_stok,
        'distribusi_peminjaman': distribusi_peminjaman,  # TAMBAHKAN ini ke context
        'segment': 'dashboard'
    }
    return render(request, 'dashboard.html', context)


# ==================== 📚 MODUL BUKU ====================
def list_buku(request):
    buku_list = Buku.objects.all().order_by('-id')
    return render(request, 'buku/list.html', {'buku_list': buku_list, 'segment': 'buku'})

def tambah_buku(request):
    if request.method == 'POST':
        Buku.objects.create(
            judul=request.POST.get('judul'),
            pengarang=request.POST.get('pengarang'),
            kategori=request.POST.get('kategori'),
            penerbit=request.POST.get('penerbit'),
            tahun_terbit=request.POST.get('tahun_terbit'),
            rak=request.POST.get('rak'),
            stok=request.POST.get('stok'),
            isbn=request.POST.get('isbn'),
            deskripsi=request.POST.get('deskripsi')
        )
        return redirect('list_buku')
    return render(request, 'buku/form.html', {'segment': 'buku'})

def detail_buku(request, pk):
    buku = get_object_or_404(Buku, pk=pk)
    return render(request, 'buku/detail.html', {'buku': buku, 'segment': 'buku'})

def edit_buku(request, pk):
    buku = get_object_or_404(Buku, pk=pk)
    if request.method == 'POST':
        buku.judul = request.POST.get('judul')
        buku.pengarang = request.POST.get('pengarang')
        buku.kategori = request.POST.get('kategori')
        buku.penerbit = request.POST.get('penerbit')
        buku.tahun_terbit = request.POST.get('tahun_terbit')
        buku.rak = request.POST.get('rak')
        buku.stok = request.POST.get('stok')
        buku.isbn = request.POST.get('isbn')
        buku.deskripsi = request.POST.get('deskripsi')
        buku.save()
        return redirect('list_buku')
    return render(request, 'buku/form.html', {'buku': buku, 'segment': 'buku'})

def hapus_buku(request, pk):
    buku = get_object_or_404(Buku, pk=pk)
    if request.method == 'POST':
        buku.delete()
        return redirect('list_buku')
    return render(request, 'buku/hapus_konfirmasi.html', {'buku': buku, 'segment': 'buku'})


# ==================== 👥 MODUL SISWA (USER) ====================
def list_user(request):
    user_list = Siswa.objects.all().order_by('-id')
    return render(request, 'user/list.html', {'user_list': user_list, 'segment': 'user'})

def tambah_user(request):
    if request.method == 'POST':
        is_active = True if request.POST.get('status') == 'Aktif' else False
        Siswa.objects.create(
            nama=request.POST.get('nama'),
            kelas=request.POST.get('kelas'),
            nis=request.POST.get('nis'),
            is_active=is_active
        )
        return redirect('list_user')
    return render(request, 'user/form.html', {'segment': 'user'})

def detail_user(request, pk):
    user = get_object_or_404(Siswa, pk=pk)
    total_pinjam = Peminjaman.objects.filter(siswa=user).count()
    pinjam_aktif = Peminjaman.objects.filter(siswa=user, status='Dipinjam').count()
    
    context = {'user': user, 'total_pinjam': total_pinjam, 'pinjam_aktif': pinjam_aktif, 'segment': 'user'}
    return render(request, 'user/detail.html', context)

def edit_user(request, pk):
    user = get_object_or_404(Siswa, pk=pk)
    if request.method == 'POST':
        user.nama = request.POST.get('nama')
        user.kelas = request.POST.get('kelas')
        user.nis = request.POST.get('nis')
        user.is_active = True if request.POST.get('status') == 'Aktif' else False
        user.save()
        return redirect('list_user')
    return render(request, 'user/form.html', {'user': user, 'segment': 'user'})

def hapus_user(request, pk):
    user = get_object_or_404(Siswa, pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('list_user')
    return render(request, 'user/hapus_konfirmasi.html', {'user': user, 'segment': 'user'})


# ==================== 📑 MODUL PEMINJAMAN ====================
def list_peminjaman(request):
    peminjaman_list = Peminjaman.objects.all().select_related('siswa', 'buku').order_by('-id')
    return render(request, 'peminjaman/list.html', {'peminjaman_list': peminjaman_list, 'segment': 'peminjaman'})

def tambah_peminjaman(request):
    if request.method == 'POST':
        siswa_id = request.POST.get('siswa_id')
        buku_id = request.POST.get('buku_id')
        
        siswa = get_object_or_404(Siswa, id=siswa_id)
        buku = get_object_or_404(Buku, id=buku_id)
        
        Peminjaman.objects.create(
            siswa=siswa,
            buku=buku,
            tanggal_pinjam=request.POST.get('tanggal_pinjam'),
            jatuh_tempo=request.POST.get('jatuh_tempo'),
            keperluan=request.POST.get('keperluan'),
            status='Dipinjam'
        )
        buku.stok -= 1
        buku.save()
        return redirect('list_peminjaman')
        
    siswa_choices = Siswa.objects.filter(is_active=True)
    buku_choices = Buku.objects.filter(stok__gt=0)
    return render(request, 'peminjaman/form.html', {
        'siswa_choices': siswa_choices,
        'buku_choices': buku_choices,
        'segment': 'peminjaman'
    })

def kembalikan_buku(request, pk):
    if request.method == 'POST':
        peminjaman = get_object_or_404(Peminjaman, pk=pk)
        if peminjaman.status == 'Dipinjam':
            peminjaman.status = 'Dikembalikan'
            peminjaman.save()
            
            peminjaman.buku.stok += 1
            peminjaman.buku.save()
            
    return redirect('list_peminjaman')