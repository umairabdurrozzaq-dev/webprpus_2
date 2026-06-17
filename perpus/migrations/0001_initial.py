from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Buku',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('judul', models.CharField(max_length=150)),
                ('pengarang', models.CharField(max_length=150)),
                ('kategori', models.CharField(max_length=50)),
                ('penerbit', models.CharField(max_length=100)),
                ('tahun', models.IntegerField(blank=True, null=True)),
                ('rak', models.CharField(max_length=20)),
                ('stok', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'buku',
            },
        ),

        migrations.CreateModel(
            name='Peminjaman',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nama_peminjam', models.CharField(max_length=100)),
                ('buku', models.CharField(max_length=255)),
                ('tanggal_pinjam', models.DateField()),
                ('jatuh_tempo', models.DateField()),
                ('keperluan', models.TextField(blank=True, null=True)),
                ('petugas', models.CharField(max_length=100, blank=True, null=True)),
                ('status', models.CharField(max_length=20, default='Dipinjam')),
            ],
            options={
                'db_table': 'peminjaman',
            },
        ),

        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nama', models.CharField(max_length=100)),
                ('kelas', models.CharField(max_length=20)),
                ('nis', models.CharField(max_length=20)),
                ('status', models.CharField(max_length=20, default='Aktif')),
            ],
            options={
                'db_table': 'users',
            },
        ),
    ]