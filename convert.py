import json
import os

def json_to_toml():
    try:
        # =========================
        # SET PATH ABSOLUT
        # =========================
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        cred_path = os.path.join(BASE_DIR, 'credentials.json')
        streamlit_dir = os.path.join(BASE_DIR, '.streamlit')
        secrets_path = os.path.join(streamlit_dir, 'secrets.toml')

        # =========================
        # DEBUG (WAJIB)
        # =========================
        print("📁 BASE_DIR:", BASE_DIR)
        print("📄 CRED_PATH:", cred_path)
        print("📂 FILES DI FOLDER:", os.listdir(BASE_DIR))
        print("📌 FILE EXISTS:", os.path.exists(cred_path))
        print("-" * 50)

        # =========================
        # VALIDASI FILE
        # =========================
        if not os.path.exists(cred_path):
            raise FileNotFoundError("credentials.json TIDAK ditemukan di folder project!")

        # =========================
        # LOAD JSON
        # =========================
        with open(cred_path, 'r', encoding='utf-8') as f:
            creds = json.load(f)

        # =========================
        # BUAT FOLDER .streamlit (kalau belum ada)
        # =========================
        os.makedirs(streamlit_dir, exist_ok=True)

        # =========================
        # TULIS FILE TOML
        # =========================
        with open(secrets_path, 'w', encoding='utf-8') as f:
            f.write('[GOOGLE_CREDENTIALS]\n')

            for key, value in creds.items():
                if key == 'private_key':
                    value = value.replace('\n', '\\n')
                    f.write(f'{key} = "{value}"\n')
                elif isinstance(value, str):
                    f.write(f'{key} = "{value}"\n')
                elif isinstance(value, (int, float, bool)):
                    f.write(f'{key} = {value}\n')
                else:
                    f.write(f'{key} = "{value}"\n')

        # =========================
        # OUTPUT
        # =========================
        print("✅ File secrets.toml berhasil dibuat!")
        print("\n📋 Isi file:")
        print("=" * 50)

        with open(secrets_path, 'r', encoding='utf-8') as f:
            print(f.read())

        print("=" * 50)

    except FileNotFoundError as e:
        print("❌ ERROR:", e)
        print("\n⚠️ Kemungkinan penyebab:")
        print("- Nama file salah (misal: credentials.json.txt)")
        print("- File belum di-save")
        print("- File ada di folder lain")
    except Exception as e:
        print(f"❌ ERROR LAIN: {e}")


if __name__ == "__main__":
    json_to_toml()