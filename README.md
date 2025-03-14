# Simple Weather Forecast BMKG

Aplikasi sederhana untuk mendapatkan prakiraan cuaca harian dari BMKG (Badan Meteorologi, Klimatologi, dan Geofisika) Indonesia dengan tampilan jam per jam yang mudah disalin.

## Fitur

- Mengambil data cuaca real-time dari sumber data resmi BMKG
- Menampilkan prakiraan cuaca per jam untuk hari ini
- Menampilkan informasi suhu dalam derajat Celsius
- Format yang mudah disalin untuk dikirim melalui WhatsApp, Telegram, atau aplikasi pesan lainnya
- Tidak memerlukan login atau otorisasi khusus
- Dapat dikustomisasi untuk lokasi yang berbeda di Indonesia

## Prasyarat

- Python 3.7+
- Koneksi internet
- Beberapa pustaka Python (diinstal melalui pip)

## Instalasi

1. Clone repositori ini atau download file ke komputer Anda

2. Install dependensi yang diperlukan:
   ```
   pip install pybmkg python-dotenv
   ```

3. Buat file environment:
   ```
   copy .env.example .env
   ```

4. Edit file `.env` dengan konfigurasi spesifik Anda:
   - `AREA_CODE`: Kode area BMKG untuk lokasi yang diinginkan (default adalah Palangkaraya)

## Cara Mencari Kode Area BMKG

Kode area default adalah untuk Palangkaraya. Untuk mencari kode area lain:

1. Kunjungi situs web BMKG
2. Cari region spesifik Anda
3. Perbarui `AREA_CODE` di file `.env` Anda

## Penggunaan

### Menjalankan aplikasi:

```
python simple_weather_forecast.py
```

Saat aplikasi berjalan, Anda akan melihat:

1. Aplikasi akan mengambil data cuaca dari BMKG untuk lokasi yang ditentukan
2. Menampilkan prakiraan cuaca per jam untuk hari ini
3. Menampilkan output dalam format yang siap disalin untuk dibagikan

### Contoh Output:

```
*Info Cuaca BMKG* 🌤️

*Tanggal:* Jumat, 14 Maret 2025
*Lokasi:* Bukit Tunggal, Palangkaraya

*Prakiraan Cuaca Hari Ini:*
• 10:00 WIB: Cerah Berawan 🌤️ 24°C
• 11:00 WIB: Cerah Berawan 🌤️ 28°C
• 12:00 WIB: Hujan Sedang 🌧️ 31°C
• 13:00 WIB: Cerah Berawan 🌤️ 28°C
• 14:00 WIB: Hujan Sedang 🌧️ 25°C
• 15:00 WIB: Hujan Sedang 🌧️ 23°C
• 16:00 WIB: Cerah Berawan 🌤️ 22°C
• 17:00 WIB: Hujan Sedang 🌧️ 23°C

Sumber data: BMKG Indonesia
```

## Kustomisasi

Anda dapat mengubah kode area BMKG di file `.env` untuk mendapatkan prakiraan cuaca dari lokasi yang berbeda di Indonesia.

Untuk contoh, beberapa kode area BMKG yang umum:
- Jakarta: `11.01.01.2001`
- Bandung: `33.01.04.1000`
- Surabaya: `73.01.01.1000`
- Yogyakarta: `50.02.02.1000`
- Palangkaraya: `62.71.03.1003`

## Troubleshooting

Jika Anda mengalami masalah:

1. Pastikan koneksi internet Anda stabil
2. Verifikasi kode area BMKG yang Anda gunakan valid
3. Periksa apakah semua dependensi terinstal dengan benar
4. Periksa file log untuk informasi error lebih detail

## Kontribusi

Kontribusi untuk pengembangan aplikasi ini sangat disambut! Silakan membuat pull request atau melaporkan masalah melalui issues.

## Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE).
