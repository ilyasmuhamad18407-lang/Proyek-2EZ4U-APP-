

def ambil_nilai_kunci(baris, kunci):

    if hasattr(baris, "get"):
        if kunci == "oid":
            return str(baris.get("oid", ""))
        elif kunci == "harga":
            val = str(baris.get("harga", "0")).strip()
            return int(val) if val.isdigit() else 0
        elif kunci == "selesai":
            val = str(baris.get("t_selesai_detik", "")).strip()
            #
            return int(val) if val.isdigit() else 999999999
        return str(baris.get("oid", ""))
    else:
        
        if kunci == "oid":
            return str(baris[0])
        elif kunci == "harga":
            val = str(baris[4]).strip()
            return int(val) if val.isdigit() else 0
        elif kunci == "selesai":
            val = str(baris[7]).strip() if len(baris) > 7 else ""
            return int(val) if val.isdigit() else 999999999
        return str(baris[0])


def insertion_sort(A, kunci):
    
    n = len(A)
    if n > 20000:
        return False, "DITOLAK: batasnya 20.000 baris, pakai merge sort untuk data penuh", 0, 0

    perbandingan = 0
    pemindahan = 0

    for i in range(1, n):
        item_sekarang = A[i]
        kunci_sekarang = ambil_nilai_kunci(item_sekarang, kunci)
        j = i - 1

        while j >= 0:
            perbandingan += 1
            
            if ambil_nilai_kunci(A[j], kunci) > kunci_sekarang:
                A[j + 1] = A[j]
                pemindahan += 1
                j -= 1
            else:
                break

        A[j + 1] = item_sekarang
        pemindahan += 1

    return True, "", perbandingan, pemindahan


def merge_sort(A, kunci):

    pencacah = [0, 0] 

    def _urutkan(larik):
        if len(larik) <= 1:
            return larik

        tengah = len(larik) // 2
        kiri = _urutkan(larik[:tengah])
        kanan = _urutkan(larik[tengah:])

        return _gabung(kiri, kanan)

    def _gabung(kiri, kanan):
        hasil = [None] * (len(kiri) + len(kanan))
        i = 0
        j = 0
        k = 0

        while i < len(kiri) and j < len(kanan):
            pencacah[0] += 1
           
            if ambil_nilai_kunci(kiri[i], kunci) <= ambil_nilai_kunci(kanan[j], kunci):
                hasil[k] = kiri[i]
                i += 1
            else:
                hasil[k] = kanan[j]
                j += 1
            pencacah[1] += 1
            k += 1

 
        while i < len(kiri):
            hasil[k] = kiri[i]
            i += 1
            k += 1
            pencacah[1] += 1


        while j < len(kanan):
            hasil[k] = kanan[j]
            j += 1
            k += 1
            pencacah[1] += 1

        return hasil

    terurut = _urutkan(A)
    for idx in range(len(A)):
        A[idx] = terurut[idx]

    return A, pencacah[0], pencacah[1]


def linear_search(A, target_oid):
   
    perbandingan = 0
    for i in range(len(A)):
        perbandingan += 1
        oid_sekarang = A[i].get("oid") if hasattr(A[i], "get") else A[i][0]
        if oid_sekarang == target_oid:
            return i, A[i], perbandingan
    return -1, None, perbandingan


def binary_search(A, target_oid):

    lo = 0
    hi = len(A) - 1
    perbandingan = 0

    while lo <= hi:
        mid = (lo + hi) // 2
        oid_mid = A[mid].get("oid") if hasattr(A[mid], "get") else A[mid][0]

        perbandingan += 1
        if oid_mid == target_oid:
            return mid, A[mid], perbandingan

        perbandingan += 1
        if oid_mid < target_oid:
            lo = mid + 1
        else:
            hi = mid - 1

    return -1, None, perbandingan