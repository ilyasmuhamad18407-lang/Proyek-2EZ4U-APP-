# frontend/ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import time
import os
import csv
from backend.m1_pesanan import Array, LinkList
from backend.m2_antrean import Stack, AntreanNaif, AntreanMelingkar, infix_ke_postfix, evaluasi_postfix
from backend.m3_laporan import insertion_sort, merge_sort, linear_search, binary_search


def format_detik_ke_jam(detik_str):
    """Mengubah detik (misal '59780') menjadi format jam 'HH:MM:SS'."""
    val = str(detik_str).strip()
    if not val.isdigit():
        return "-"
    total_detik = int(val)
    jam = (total_detik // 3600) % 24
    menit = (total_detik % 3600) // 60
    detik = total_detik % 60
    return f"{jam:02d}:{menit:02d}:{detik:02d}"


class App2EZ4U:
    def __init__(self, root):
        self.root = root
        self.root.title("2EZ4U Food Delivery - M1, M2 & M3")
        self.root.geometry("1150x720")
        
        # Struktur Data M1
        self.array_pesanan = Array()
        self.ll_pesanan = LinkList()
        
        # Struktur Data M2
        self.queue_naif = AntreanNaif()
        self.queue_circular = AntreanMelingkar()
        self.undo_stack = Stack()
        self.redo_stack = Stack()

        # Struktur Data & Cache M3
        self.semua_data_m3 = []
        self.data_terurut_oid = None
        self.waktu_bangun_oid_ms = 0.0
        
        self.setup_ui()

    def setup_ui(self):
        # PANEL KIRI (MENU)
        self.panel_kiri = tk.Frame(self.root, width=300, bg="#f0f0f0", relief=tk.SUNKEN, bd=1)
        self.panel_kiri.pack(side=tk.LEFT, fill=tk.Y)
        self.panel_kiri.pack_propagate(False)
        
        tk.Label(self.panel_kiri, text="DATA", bg="#d9d9d9", anchor="w", font=("Arial", 9, "bold")).pack(fill=tk.X)
        tk.Button(self.panel_kiri, text="Load Data", command=self.load_data).pack(fill=tk.X, padx=5, pady=2)
        
        # Menu M1
        tk.Label(self.panel_kiri, text="M1 - DATA PESANAN", bg="#d9d9d9", anchor="w", font=("Arial", 9, "bold")).pack(fill=tk.X, pady=(8,0))
        menu_m1 = [
            ("ARRAY - LIHAT PESANAN", "lihat", "array"),
            ("ARRAY - TAMBAH PESANAN REGULER", "tambah_reguler", "array"),
            ("ARRAY - TAMBAH PESANAN PRIORITAS", "tambah_prioritas", "array"),
            ("ARRAY - TAMBAH PESANAN VIP", "tambah_vip", "array"),
            ("ARRAY - HAPUS PESANAN", "hapus", "array"),
            ("LINKEDLIST - LIHAT PESANAN", "lihat", "ll"),
            ("LINKEDLIST - TAMBAH PESANAN REGULER", "tambah_reguler", "ll"),
            ("LINKEDLIST - TAMBAH PESANAN PRIORITAS", "tambah_prioritas", "ll"),
            ("LINKEDLIST - TAMBAH PESANAN VIP", "tambah_vip", "ll"),
            ("LINKEDLIST - HAPUS PESANAN", "hapus", "ll")
        ]
        for text, mode, struktur in menu_m1:
            pad_top = 6 if "LINKEDLIST" in text and "LIHAT" in text else 1
            tk.Button(self.panel_kiri, text=text, anchor="w", font=("Courier", 8),
                      command=lambda m=mode, s=struktur: self.tampilkan_form(m, s)).pack(fill=tk.X, padx=5, pady=(pad_top, 1))

        # Menu M2
        tk.Label(self.panel_kiri, text="M2 - STACK & QUEUE", bg="#d9d9d9", anchor="w", font=("Arial", 9, "bold")).pack(fill=tk.X, pady=(8,0))
        menu_m2 = [
            ("STACK - POSTFIX (MESIN KASIR)", "m2_postfix"),
            ("STACK - UNDO", "m2_undo"),
            ("STACK - REDO", "m2_redo"),
            ("QUEUE - ENQUEUE", "m2_enqueue"),
            ("QUEUE - DEQUEUE NAIF", "m2_deq_naif"),
            ("QUEUE - DEQUEUE CIRCULAR", "m2_deq_circular"),
        ]
        for text, mode in menu_m2:
            tk.Button(self.panel_kiri, text=text, anchor="w", font=("Courier", 8),
                      command=lambda m=mode: self.tampilkan_form_m2(m)).pack(fill=tk.X, padx=5, pady=1)

        # Menu M3
        tk.Label(self.panel_kiri, text="M3 - SORT DAN SEARCH", bg="#d9d9d9", anchor="w", font=("Arial", 9, "bold")).pack(fill=tk.X, pady=(8,0))
        menu_m3 = [
            ("SORT - INSERTION SORT", "insertion_sort"),
            ("SORT - MERGE SORT", "merge_sort"),
            ("SEARCH - LINEAR SEARCH", "linear_search"),
            ("SEARCH - BINARY SEARCH", "binary_search"),
        ]
        for text, mode in menu_m3:
            tk.Button(self.panel_kiri, text=text, anchor="w", font=("Courier", 8),
                      command=lambda m=mode: self.tampilkan_form_m3(m)).pack(fill=tk.X, padx=5, pady=1)

        # PANEL KANAN (Tabel & Command)
        self.panel_kanan = tk.Frame(self.root)
        self.panel_kanan.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.panel_hasil = tk.Frame(self.panel_kanan, bg="white")
        self.panel_hasil.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.judul_menu = tk.Label(self.panel_hasil, text="Silakan pilih menu di samping", font=("Arial", 12, "bold"), bg="white")
        self.judul_menu.pack(anchor="w")
        
        self.frame_input = tk.Frame(self.panel_hasil, bg="white")
        self.frame_input.pack(anchor="w", pady=8, fill=tk.X)

        # Label info tambahan untuk menampilkan jumlah perbandingan & pemindahan M3
        self.label_info_m3 = tk.Label(self.panel_hasil, text="", font=("Arial", 10), bg="white", justify=tk.LEFT)
        self.label_info_m3.pack(anchor="w", pady=(0, 5))
        
        kolom = ("oid", "pelanggan", "resto", "menu", "harga", "prioritas")
        self.tabel = ttk.Treeview(self.panel_hasil, columns=kolom, show="headings", height=13)
        for col in kolom:
            self.tabel.heading(col, text=col.capitalize())
            self.tabel.column(col, width=100)
        self.tabel.pack(fill=tk.BOTH, expand=True)

        self.panel_command = tk.Frame(self.panel_kanan, height=120, bg="#e8e8e8")
        self.panel_command.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))
        self.panel_command.pack_propagate(False)
        
        tk.Label(self.panel_command, text="COMMAND", font=("Courier", 9, "bold"), bg="#e8e8e8").pack(anchor="w")
        self.log_command = tk.Text(self.panel_command, font=("Courier", 10))
        self.log_command.pack(fill=tk.BOTH, expand=True)
        
        self.mode_aktif = None
        self.struktur_aktif = None

    def set_kolom_tabel(self, kolom_baru):
        self.tabel.delete(*self.tabel.get_children())
        self.tabel["columns"] = kolom_baru
        for col in kolom_baru:
            self.tabel.heading(col, text=col)
            self.tabel.column(col, width=110)

    # ================= M1 FORM & EKSEKUSI =================
    def tampilkan_form(self, mode, struktur):
        for widget in self.frame_input.winfo_children(): widget.destroy()
        self.label_info_m3.config(text="")
        self.mode_aktif = mode
        self.struktur_aktif = struktur
        nama_struktur = "Array" if struktur == "array" else "Linked List"
        
        if mode in ["lihat", "hapus"]:
            self.judul_menu.config(text=f"{nama_struktur}: {mode.upper()} PESANAN")
            tk.Label(self.frame_input, text="Indeks:", bg="white").pack(side=tk.LEFT)
            self.entry_param = tk.Entry(self.frame_input, width=15)
            self.entry_param.pack(side=tk.LEFT, padx=5)
            tk.Button(self.frame_input, text=mode.upper(), command=self.eksekusi_perintah).pack(side=tk.LEFT)
        else:
            jenis = mode.split("_")[1].upper()
            self.judul_menu.config(text=f"{nama_struktur}: TAMBAH PESANAN {jenis}")
            tk.Label(self.frame_input, text="Nama Pelanggan:", bg="white").pack(side=tk.LEFT)
            self.entry_param = tk.Entry(self.frame_input, width=30)
            self.entry_param.pack(side=tk.LEFT, padx=5)
            tk.Button(self.frame_input, text="TAMBAH", command=self.eksekusi_perintah).pack(side=tk.LEFT)

    def eksekusi_perintah(self):
        target = self.array_pesanan if self.struktur_aktif == "array" else self.ll_pesanan
        param = self.entry_param.get()
        start = time.perf_counter()
        
        if self.mode_aktif in ["lihat", "hapus"]:
            try:
                idx = int(param)
                if self.mode_aktif == "lihat":
                    hasil = target.get(idx)
                    messagebox.showinfo("Lihat Pesanan", str(hasil) if hasil else "Tidak ditemukan")
                else:
                    hasil = target.hapus(idx)
                    if hasil:
                        self.tabel.delete(self.tabel.get_children()[idx])
                        messagebox.showinfo("Sukses", "Pesanan dihapus")
            except Exception:
                messagebox.showerror("Error", "Indeks salah/tidak ada")
        else:
            pelanggan = param or "Pelanggan Baru"
            prioritas = 1 if "vip" in self.mode_aktif else (2 if "prioritas" in self.mode_aktif else 3)
            pesanan = {"oid": f"O-{len(self.semua_data_m3)+1:06d}", "pelanggan": pelanggan, "resto": "-", "menu": "-", "harga": "0", "prioritas": str(prioritas), "t_masuk_detik": "36000", "t_selesai_detik": "", "status": "ANTRE"}
            
            if "reguler" in self.mode_aktif:
                target.tambah_reguler(pesanan)
                self.tabel.insert("", tk.END, values=(pesanan['oid'], pesanan['pelanggan'], pesanan['resto'], pesanan['menu'], pesanan['harga'], pesanan['prioritas']))
                self.tabel.yview_moveto(1)
            elif "prioritas" in self.mode_aktif:
                target.tambah_prioritas(pesanan)
                tengah = target.size // 2
                self.tabel.insert("", tengah, values=(pesanan['oid'], pesanan['pelanggan'], pesanan['resto'], pesanan['menu'], pesanan['harga'], pesanan['prioritas']))
                self.tabel.see(self.tabel.get_children()[tengah])
            elif "vip" in self.mode_aktif:
                target.tambah_vip(pesanan)
                self.tabel.insert("", 0, values=(pesanan['oid'], pesanan['pelanggan'], pesanan['resto'], pesanan['menu'], pesanan['harga'], pesanan['prioritas']))
                self.tabel.yview_moveto(0)

            self.semua_data_m3.append(pesanan)
            self.data_terurut_oid = None

        waktu_ms = (time.perf_counter() - start) * 1000
        modul = "M1 - array" if self.struktur_aktif == "array" else "M1 - linkedlist"
        self.log_command.insert(tk.END, f"{self.struktur_aktif}_{self.mode_aktif:<15} -> {modul:<15} {waktu_ms:.2f} ms\n")
        self.log_command.see(tk.END)

    # ================= M2 FORM & EKSEKUSI =================
    def tampilkan_form_m2(self, mode):
        for widget in self.frame_input.winfo_children(): widget.destroy()
        self.label_info_m3.config(text="")
        self.mode_aktif = mode
        self.struktur_aktif = "m2"
        
        if mode == "m2_postfix":
            self.judul_menu.config(text="Stack Postfix: Mesin Kasir Struk Belanja")
            tk.Label(self.frame_input, text="Ekspresi Infix:", bg="white").pack(side=tk.LEFT)
            self.entry_param = tk.Entry(self.frame_input, width=35)
            self.entry_param.insert(0, "(3*12000)+(2*8500)-5000")
            self.entry_param.pack(side=tk.LEFT, padx=5)
            tk.Button(self.frame_input, text="HITUNG", command=self.eksekusi_perintah_m2).pack(side=tk.LEFT)
        elif mode in ["m2_undo", "m2_redo"]:
            aksi_str = "UNDO" if mode == "m2_undo" else "REDO"
            self.judul_menu.config(text=f"Stack {aksi_str}: Batalkan/Ulangi Aksi")
            tk.Label(self.frame_input, text="Tekan tombol untuk mengeksekusi", bg="white").pack(side=tk.LEFT)
            tk.Button(self.frame_input, text=aksi_str, command=self.eksekusi_perintah_m2).pack(side=tk.LEFT, padx=5)
        elif mode == "m2_enqueue":
            self.judul_menu.config(text="Queue Enqueue: Tambah ke Kedua Antrean")
            tk.Label(self.frame_input, text="Nama Pelanggan:", bg="white").pack(side=tk.LEFT)
            self.entry_param = tk.Entry(self.frame_input, width=25)
            self.entry_param.pack(side=tk.LEFT, padx=5)
            tk.Button(self.frame_input, text="ENQUEUE", command=self.eksekusi_perintah_m2).pack(side=tk.LEFT)
        elif mode in ["m2_deq_naif", "m2_deq_circular"]:
            jenis_q = "Naif" if "naif" in mode else "Circular"
            self.judul_menu.config(text=f"Queue Dequeue {jenis_q}: Ambil dari Depan")
            tk.Label(self.frame_input, text="Berapa kali:", bg="white").pack(side=tk.LEFT)
            self.entry_param = tk.Entry(self.frame_input, width=10)
            self.entry_param.insert(0, "1")
            self.entry_param.pack(side=tk.LEFT, padx=5)
            tk.Button(self.frame_input, text="DEQUEUE", command=self.eksekusi_perintah_m2).pack(side=tk.LEFT)

    def eksekusi_perintah_m2(self):
        start = time.perf_counter()
        
        if self.mode_aktif == "m2_postfix":
            ekspresi = self.entry_param.get().strip() or "(3*12000)+(2*8500)-5000"
            postfix = infix_ke_postfix(ekspresi)
            total = evaluasi_postfix(postfix)
            waktu_ms = (time.perf_counter() - start) * 1000
            
            info = f"Postfix: {' '.join(str(x) for x in postfix)} | TOTAL: Rp {total:,}"
            self.judul_menu.config(text=info)
            self.log_command.insert(tk.END, f"stack_postfix                    -> M2 - stack       {waktu_ms:.2f} ms\n")
            
        elif self.mode_aktif == "m2_enqueue":
            nama = self.entry_param.get().strip() or "Pelanggan Baru"
            pesanan_dict = {"oid": "O-QNEW", "pelanggan": nama, "resto": "kafe-teknik", "menu": "roti-bakar", "harga": 12000, "prioritas": 2}
            
            self.queue_naif.enqueue(pesanan_dict)
            self.queue_circular.enqueue(pesanan_dict)
            
            self.undo_stack.push(("ENQUEUE", pesanan_dict))
            self.redo_stack = Stack()
            
            waktu_ms = (time.perf_counter() - start) * 1000
            self.tabel.insert("", tk.END, values=list(pesanan_dict.values()))
            self.log_command.insert(tk.END, f"queue_enqueue                    -> M2 - queue       {waktu_ms:.2f} ms\n")
            
        elif self.mode_aktif == "m2_deq_naif":
            try:
                kali = int(self.entry_param.get().strip() or "1")
                dikeluarkan = []
                total_geser = 0
                for _ in range(kali):
                    res = self.queue_naif.dequeue()
                    if res:
                        item, geser = res
                        dikeluarkan.append(item)
                        total_geser += geser
                waktu_ms = (time.perf_counter() - start) * 1000
                
                self.undo_stack.push(("DEQUEUE_NAIF", dikeluarkan))
                self.redo_stack = Stack()
                
                for it in dikeluarkan:
                    self.tabel.insert("", tk.END, values=(it['oid'], it['pelanggan'], it['resto'], it['menu'], it['harga'], it['prioritas']))
                self.log_command.insert(tk.END, f"queue_dequeue_naive              -> M2 - queue naif  {waktu_ms:.2f} ms ({total_geser} geser)\n")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        elif self.mode_aktif == "m2_deq_circular":
            try:
                kali = int(self.entry_param.get().strip() or "1")
                dikeluarkan = []
                for _ in range(kali):
                    res = self.queue_circular.dequeue()
                    if res:
                        item, _ = res
                        dikeluarkan.append(item)
                waktu_ms = (time.perf_counter() - start) * 1000
                
                self.undo_stack.push(("DEQUEUE_CIRCULAR", dikeluarkan))
                self.redo_stack = Stack()
                
                for it in dikeluarkan:
                    self.tabel.insert("", tk.END, values=(it['oid'], it['pelanggan'], it['resto'], it['menu'], it['harga'], it['prioritas']))
                self.log_command.insert(tk.END, f"queue_dequeue_circular           -> M2 - circular    {waktu_ms:.2f} ms (0 geser)\n")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        elif self.mode_aktif == "m2_undo":
            if self.undo_stack.is_empty():
                messagebox.showinfo("Undo", "Tidak ada aksi untuk dibatalkan.")
                return
            aksi, data = self.undo_stack.pop()
            if aksi == "ENQUEUE":
                if len(self.queue_naif._data) > 0:
                    self.queue_naif._data.pop()
                self.queue_circular.rear = (self.queue_circular.rear - 1) % self.queue_circular._kapasitas
                self.queue_circular.count -= 1
            self.redo_stack.push((aksi, data))
            waktu_ms = (time.perf_counter() - start) * 1000
            self.log_command.insert(tk.END, f"stack_undo                       -> M2 - stack       {waktu_ms:.2f} ms\n")
            messagebox.showinfo("Undo Berjaya", f"Aksi {aksi} dibatalkan.")
            
        elif self.mode_aktif == "m2_redo":
            if self.redo_stack.is_empty():
                messagebox.showinfo("Redo", "Tidak ada aksi untuk diulang.")
                return
            aksi, data = self.redo_stack.pop()
            if aksi == "ENQUEUE":
                self.queue_naif.enqueue(data)
                self.queue_circular.enqueue(data)
            self.undo_stack.push((aksi, data))
            waktu_ms = (time.perf_counter() - start) * 1000
            self.log_command.insert(tk.END, f"stack_redo                       -> M2 - stack       {waktu_ms:.2f} ms\n")
            messagebox.showinfo("Redo Berjaya", f"Aksi {aksi} dikerjakan ulang.")

        self.log_command.see(tk.END)

    # ================= M3 FORM & EKSEKUSI =================
    def tampilkan_form_m3(self, mode):
        for widget in self.frame_input.winfo_children(): widget.destroy()
        self.label_info_m3.config(text="")
        self.mode_aktif = mode
        self.struktur_aktif = "m3"

        if mode in ["insertion_sort", "merge_sort"]:
            judul = "Sort: insertion sort, O(n²)" if mode == "insertion_sort" else "Sort: merge sort, O(n log n)"
            self.judul_menu.config(text=judul)

            tk.Label(self.frame_input, text="Jumlah baris diurutkan:", bg="white").pack(side=tk.LEFT)
            self.entry_jumlah_m3 = tk.Entry(self.frame_input, width=10)
            self.entry_jumlah_m3.insert(0, "10" if mode == "insertion_sort" else "4000")
            self.entry_jumlah_m3.pack(side=tk.LEFT, padx=(5, 15))

            tk.Label(self.frame_input, text="Diurutkan menurut:", bg="white").pack(side=tk.LEFT)
            self.combo_kunci_m3 = ttk.Combobox(self.frame_input, values=["oid", "harga", "selesai"], state="readonly", width=12)
            self.combo_kunci_m3.set("harga" if mode == "insertion_sort" else "oid")
            self.combo_kunci_m3.pack(side=tk.LEFT, padx=(5, 15))

            tk.Button(self.frame_input, text="URUTKAN", command=self.eksekusi_sort_m3).pack(side=tk.LEFT)

        elif mode in ["linear_search", "binary_search"]:
            judul = "Search: linear search, O(n)" if mode == "linear_search" else "Search: binary search, O(log n)"
            self.judul_menu.config(text=judul)

            tk.Label(self.frame_input, text="Nomor pesanan (oid):", bg="white").pack(side=tk.LEFT)
            self.entry_oid_m3 = tk.Entry(self.frame_input, width=18)
            self.entry_oid_m3.insert(0, "O-000010")
            self.entry_oid_m3.pack(side=tk.LEFT, padx=(5, 15))

            tk.Button(self.frame_input, text="CARI", command=self.eksekusi_search_m3).pack(side=tk.LEFT)

    def eksekusi_sort_m3(self):
        if len(self.semua_data_m3) == 0:
            messagebox.showwarning("Peringatan", "Silakan klik 'Load Data' terlebih dahulu!")
            return

        try:
            jumlah = int(self.entry_jumlah_m3.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Jumlah baris harus berupa angka!")
            return

        jumlah = min(jumlah, len(self.semua_data_m3))
        kunci = self.combo_kunci_m3.get()
        potongan = [self.semua_data_m3[i] for i in range(jumlah)]

        start = time.perf_counter()
        if self.mode_aktif == "insertion_sort":
            sukses, pesan, banding, pindah = insertion_sort(potongan, kunci)
            waktu_ms = (time.perf_counter() - start) * 1000
            if not sukses:
                self.label_info_m3.config(text=pesan, fg="red")
                return
            modul = "M3 - insertion sort"
        else:
            potongan, banding, pindah = merge_sort(potongan, kunci)
            waktu_ms = (time.perf_counter() - start) * 1000
            modul = "M3 - merge sort"

        self.label_info_m3.config(
            text=f"{jumlah:,} pesanan diurutkan menurut {kunci}.\n{banding:,} perbandingan, {pindah:,} pemindahan.",
            fg="black"
        )

        self.set_kolom_tabel(("#", "oid", "harga", "selesai", "resto", "menu"))
        for i in range(min(len(potongan), 100)):
            d = potongan[i]
            harga_fmt = f"{int(d['harga']):,}" if str(d.get('harga', '')).isdigit() else d.get('harga', '-')
            selesai_fmt = format_detik_ke_jam(d.get('t_selesai_detik', ''))
            self.tabel.insert("", tk.END, values=(i + 1, d.get('oid', ''), harga_fmt, selesai_fmt, d.get('resto', ''), d.get('menu', '')))

        self.log_command.insert(tk.END, f"{self.mode_aktif:<32} -> {modul:<16} {waktu_ms:.2f} ms\n")
        self.log_command.see(tk.END)

    def eksekusi_search_m3(self):
        if len(self.semua_data_m3) == 0:
            messagebox.showwarning("Peringatan", "Silakan klik 'Load Data' terlebih dahulu!")
            return

        target_oid = self.entry_oid_m3.get().strip()
        info_awal = ""

        if self.mode_aktif == "linear_search":
            start = time.perf_counter()
            idx, hasil, banding = linear_search(self.semua_data_m3, target_oid)
            waktu_ms = (time.perf_counter() - start) * 1000
            modul = "M3 - linear search"
        else:
            if self.data_terurut_oid is None:
                salinan = [x for x in self.semua_data_m3]
                t0 = time.perf_counter()
                self.data_terurut_oid, _, _ = merge_sort(salinan, "oid")
                self.waktu_bangun_oid_ms = (time.perf_counter() - t0) * 1000

            info_awal = f"Daftar terurut oid dibangun sekali dengan merge sort, {self.waktu_bangun_oid_ms:.2f} ms.\n"
            start = time.perf_counter()
            idx, hasil, banding = binary_search(self.data_terurut_oid, target_oid)
            waktu_ms = (time.perf_counter() - start) * 1000
            modul = "M3 - binary search"

        self.set_kolom_tabel(("kolom", "isi"))
        if idx != -1 and hasil is not None:
            if self.mode_aktif == "linear_search":
                teks = f"Ditemukan pada indeks {idx:,}.\n{banding:,} perbandingan."
            else:
                teks = f"{info_awal}Ditemukan pada baris ke-{idx + 1:,} dari {len(self.semua_data_m3):,} baris.\n{banding:,} perbandingan, bandingkan dengan linear search."
            self.label_info_m3.config(text=teks, fg="black")

            rincian = [
                ("oid", hasil.get("oid", "-")),
                ("pelanggan", hasil.get("pelanggan", "-")),
                ("resto", hasil.get("resto", "-")),
                ("menu", hasil.get("menu", "-")),
                ("harga", f"{int(hasil['harga']):,}" if str(hasil.get('harga', '')).isdigit() else hasil.get('harga', '-')),
                ("prioritas", hasil.get("prioritas", "-")),
                ("masuk", format_detik_ke_jam(hasil.get("t_masuk_detik", ""))),
                ("selesai", format_detik_ke_jam(hasil.get("t_selesai_detik", ""))),
                ("status", hasil.get("status", "-")),
            ]
            for k, v in rincian:
                self.tabel.insert("", tk.END, values=(k, v))
        else:
            self.label_info_m3.config(text=f"{info_awal}Pesanan '{target_oid}' tidak ditemukan ({banding:,} perbandingan).", fg="red")

        self.log_command.insert(tk.END, f"{self.mode_aktif:<32} -> {modul:<16} {waktu_ms:.2f} ms\n")
        self.log_command.see(tk.END)

    # ================= LOAD DATA =================
    def load_data(self):
        file_path = os.path.join("data", "pesanan.csv")
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "File data/pesanan.csv tidak ditemukan")
            return
        
        self.set_kolom_tabel(("oid", "pelanggan", "resto", "menu", "harga", "prioritas"))
        self.semua_data_m3 = []
        self.data_terurut_oid = None
        
        try:
            start = time.perf_counter()
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    # Memuat seluruh data ke M3 agar search dan merge sort 200.000 baris bisa diuji
                    self.semua_data_m3.append(row)
                    
                    # Untuk M1, M2, dan tampilan awal tabel dibatasi 1000 baris pertama agar responsif
                    if count < 1000:
                        self.array_pesanan.tambah_reguler(row)
                        self.ll_pesanan.tambah_reguler(row)
                        self.queue_naif.enqueue(row)
                        self.queue_circular.enqueue(row)
                        self.tabel.insert("", tk.END, values=(row['oid'], row['pelanggan'], row['resto'], row['menu'], row['harga'], row['prioritas']))
                    count += 1
            waktu_ms = (time.perf_counter() - start) * 1000
            self.log_command.insert(tk.END, f"load_data -> M1_M2_M3_init \t{waktu_ms:.2f} ms ({count:,} baris)\n")
            messagebox.showinfo("Sukses", f"Memuat {count:,} baris data")
        except Exception as e:
            messagebox.showerror("Error", str(e))