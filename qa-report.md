# QA Report — vision

Model: or/inclusionai/ling-3.0-flash-vl:free
Frames: 15
Issues: 14

Verdict: **FAIL**

## qa/frame_1.5.png
OK

## qa/frame_10.5.png
ISSUE: Teks "6.000 m" terpotong/tersembunyi oleh garis merah horizontal yang melewatinya.
ISSUE: Teks putih "lebih dalam dari Gunung Semeru" tumpang tindih garis merah palung, bacaan terganggu.

## qa/frame_14.png
ISSUE: Teks "Di situlah Lempeng INDO-AUSTRALIA" tumpang tindih dengan garis merah cross-section Palung Jawa, kurangi keterbacaan.
ISSUE: Label kedalaman "–6.000 m" di sisi kanan tertutup/terpotong garis merah.

## qa/frame_18.png
OK

## qa/frame_20.5.png
OK

## qa/frame_24.5.png
ISSUE: Teks "Secepat kukumu", "kuku tumbuh 6,5 cm/th", dan "tumbuh" saling bertabrakan di bagian bawah (baris terlalu rapat, subteks abu-abut overlap kedua baris putih).
ISSUE: Teks abu-abu "kuku tumbuh 6,5 cm/th" terbaca buram/ngasal di atas latar gelap (kontras rendah).

## qa/frame_28.png
ISSUE: Teks "kuku tumbuh 6,5 cm/th" tertutup bar "Tekanan menumpuk"/"bertahun-tahun".
ISSUE: Label skala kanan "m" terpotong di tepi frame.
ISSUE: Ikon tekanan (ring) ambigu, tidak jelas ilustrasinya.

## qa/frame_3.4.png
OK

## qa/frame_30.5.png
OK

## qa/frame_33.5.png
ISSUE: Teks "Gempa = gerakan tertahan" bertabrakan dengan label kedalaman "-7.192 m" di baris yang sama, saling berdekatan hingga berpotensi tumpang tindih.
OK
OK

## qa/frame_36.2.png
OK.

## qa/frame_38.8.png
OK

## qa/frame_41.png
ISSUE: Garis merah tipis di tengah frame (~y680) tidak jelas — ilustrasi ngasal, tidak ada label/konteks makna.
ISSUE: Skala kedalaman `-7.192 m` di kanan bawah ambigu — untuk Palung Jawa (~7.192 m) format angka Indonesia pakai titik sebagai ribuan, bukan desimal, berpotensi salah baca.

OK untuk: tidak ada tabrakan teks, tidak ada elemen terpotong tepi.

## qa/frame_5.2.png
OK

## qa/frame_7.5.png
ISSUE: Skala vertikal berakhir di -6.000 m, marker -7.192 m terputus dari garis skala.
ISSUE: Frame kosong, tidak ada ilustrasi palung/laut—hanya teks dan skala.
