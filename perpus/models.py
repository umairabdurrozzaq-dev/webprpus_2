from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.db import models

class Buku(models.Model):
    judul = models.CharField(max_length=255)
    pengarang = models.CharField(max_length=255)
    kategori = models.CharField(max_length=100)
    penerbit = models.CharField(max_length=255)
    tahun_terbit = models.IntegerField()
    rak = models.CharField(max_length=50)
    stok = models.IntegerField(default=0)
    isbn = models.CharField(max_length=50, blank=True, null=True)
    deskripsi = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.judul

class Siswa(models.Model):
    nama = models.CharField(max_length=255)
    kelas = models.CharField(max_length=50)
    nis = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.nama

class Peminjaman(models.Model):
    STATUS_CHOICES = [
        ('Dipinjam', 'Dipinjam'),
        ('Dikembalikan', 'Dikembalikan'),
    ]
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE)
    buku = models.ForeignKey(Buku, on_delete=models.CASCADE)
    tanggal_pinjam = models.DateField()
    jatuh_tempo = models.DateField()
    keperluan = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Dipinjam')

    def __str__(self):
        return f"{self.siswa.nama} - {self.buku.judul}"