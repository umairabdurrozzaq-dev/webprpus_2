from django.views.generic import RedirectView
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard Utama
    path('', views.dashboard, name='dashboard'),
    # Redirect dari root ke dashboard
    path('', RedirectView.as_view(pattern_name='dashboard', permanent=False)),
    # Cari baris ini di perpus/urls.py dan ubah menjadi seperti ini:
    path('dashboard/', views.dashboard, name='dashboard'),

    
    # URL Modul Buku
    path('buku/', views.list_buku, name='list_buku'),
    path('buku/tambah/', views.tambah_buku, name='tambah_buku'),
    path('buku/detail/<int:pk>/', views.detail_buku, name='detail_buku'),
    path('buku/edit/<int:pk>/', views.edit_buku, name='edit_buku'),
    path('buku/hapus/<int:pk>/', views.hapus_buku, name='hapus_buku'),
    
    # URL Modul User (Siswa)
    path('user/', views.list_user, name='list_user'),
    path('user/tambah/', views.tambah_user, name='tambah_user'),
    path('user/detail/<int:pk>/', views.detail_user, name='detail_user'),
    path('user/edit/<int:pk>/', views.edit_user, name='edit_user'),
    path('user/hapus/<int:pk>/', views.hapus_user, name='hapus_user'),
    
    # URL Modul Peminjaman
    path('peminjaman/', views.list_peminjaman, name='list_peminjaman'),
    path('peminjaman/tambah/', views.tambah_peminjaman, name='tambah_peminjaman'),
    path('peminjaman/kembalikan/<int:pk>/', views.kembalikan_buku, name='kembalikan_buku'),
]