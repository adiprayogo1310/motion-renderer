# QA Report — vision

Model: bai/glm-5.3-flash
Frames: 15
Issues: 22

Verdict: **FAIL**

## qa/frame_1.5.png
ISSUE: Garis sumbu vertikal berhenti sebelum label -7.192 m; label menggantung tanpa garis/tick penandas.

## qa/frame_10.5.png
ISSUE: garis merah palung menabrak teks caption "lebih dalam dari Gunung Semeru / PALUNG JAWA −7.192 m".
ISSUE: garis merah menimpa label sumbu "−6.000 m", angka sulit terbaca.

## qa/frame_14.png
ISSUE: Label sumbu "−6.000 m" tertimpa garis dasar laut merah.
ISSUE: Blok teks caption ("Di situlah Lempeng INDO-AUSTRALIA") bertabrakan dengan garis palung merah yang memotongnya.
ISSUE: Semeru (gunung darat) digambar berdiri di dasar laut palung — penempatan ilustrasi tidak sesuai konteks.

## qa/frame_18.png
ISSUE: ilustrasi palung tidak terlihat, area tengah frame kosong hanya ada garis skala
ISSUE: garis skala berhenti di ~ -6.000 m, tidak mencapai label -7.192 m

## qa/frame_20.5.png
ISSUE: Label "-2.000 m" tertimpa tepi kanan kotak Lempeng Eurasia.
ISSUE: Ujung bawah poligon oranye menabrak teks "Enam koma lima sentimeter".

## qa/frame_24.5.png
ISSUE: teks kecil "kuku tumbuh 6,5 cm/th" tertimpa teks "Secepat kukumu" — tabrakan teks.

## qa/frame_28.png
ISSUE: Teks kecil "kuku tumbuh 6,5 cm/th" bertabrakan/tumpang tindih dengan teks "Tekanan menumpuk".

## qa/frame_3.4.png
OK

## qa/frame_30.5.png
OK

## qa/frame_33.5.png
ISSUE: Teks caption "Gempa bukan kejadian" tampak terpotong / kalimat tidak lengkap.

## qa/frame_36.2.png
ISSUE: subteks "yang tertahan bertahun-tahun" kontras terlalu rendah, hampir tak terbaca di atas kotak gelap.

## qa/frame_38.8.png
ISSUE: subjudul "yang tertahan bertahun-tahun" kontras terlalu rendah di box gelap, susah dibaca.
ISSUE: garis skala kedalaman berhenti di ~-6.000 m, label "-7.192 m" menggantung tanpa garis.
ISSUE: jarak tepi kanan kartu ke label "-2.000 m" cuma ~10px, terlalu rapat.

## qa/frame_41.png
ISSUE: garis merah di tengah mengambang tanpa label/konteks — tidak jelas mewakili apa (sesar/trench).
ISSUE: garis sumbu kedalaman berakhir di ~−6.000 m, label −7.192 m di bawahnya tanpa garis/tick.

## qa/frame_5.2.png
ISSUE: Label "DASAR LAUT −7.192 m" salah posisi — berada di antara skala −4.000 dan −6.000, bukan di −7.192 m.
ISSUE: Garis putus-putus berhenti di ~−2.300 m, tidak menyambung ke dasar laut.
ISSUE: Pill label menabrak garis sumbu vertikal di kanan.

## qa/frame_7.5.png
OK
