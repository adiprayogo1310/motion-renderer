# QA Report — vision

Model: or/inclusionai/ling-3.0-flash-vl:free
Frames: 15
Issues: 13

Verdict: **FAIL**

## qa/frame_1.5.png
OK

## qa/frame_10.5.png
ISSUE: Teks "SEMERU 3.676 m" bertabrakan dengan logo "FAKTAGEO" di pojok kiri atas.
ISSUE: Label "-6.000 m" di sisi kanan tertutup garis merah ilustrasi palung.

## qa/frame_14.png
ISSUE: Teks "FAKTAGEO" tabrak "SEMERU 3.676 m" di kiri atas.
ISSUE: Label "6.000 m" overlap garis merah dan teks bawah.

## qa/frame_18.png
OK

## qa/frame_20.5.png
ISSUE: Teks "Enam koma lima sentimeter per tahun" tumpang tindih ilustrasi pelat Indo-Australia dan dekat label "-7.192 m", kurang legibel.
ISSUE: Garis putus-putus merah (zona subduksi) terletak di dalam pelat Indo-Australia, bukan di batas antar pelat — secara geografis salah.

## qa/frame_24.5.png
ISSUE: Teks "tumbuh" tumpang tindih dengan teks ghost "kukum/th" di bagian bawah — animasi teks tidak membersihkan frame sebelumnya.
ISSUE: Marker segitiga oranye melayang tanpa label/penjelasan di atas progress bar, tidak jelas fungsinya.

## qa/frame_28.png
ISSUE: Batang horizontal 0 TH–100 TH sejajar sumbu kedalaman vertikal, akumulasi 6,5 m tidak tergambar, hubungan skala tidak jelas.
ISSUE: Ikon palu di bawah "Tekanan menumpuk bertahun-tahun" tidak jelas mewakili tekanan, ilustrasi ngasal.

## qa/frame_3.4.png
ISSUE: Ilustrasi perahu layar di atas permukaan air tidak jelas dan tidak sesuai tema Palung Jawa (trench laut dalam).

## qa/frame_30.5.png
OK

## qa/frame_33.5.png
OK

## qa/frame_36.2.png
OK

## qa/frame_38.8.png
OK

## qa/frame_41.png
ISSUE: Garis merah tengah frame tidak jelas - ilustrasi ambigu, tidak ada label atau konteks visual yang menunjukkan apa yang direpresentasikan.

## qa/frame_5.2.png
OK

## qa/frame_7.5.png
ISSUE: Ilustrasi hampir kosong total, hanya garis skala kedalaman tanpa visual dasar laut, kolam dalam, atau elemen gerakan jatuh; area tengah-frame polos tidak menyampaikan konten edukasi.
