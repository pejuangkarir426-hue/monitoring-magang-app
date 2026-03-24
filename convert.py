import json

def json_to_toml():
    try:
        # Baca file credentials.json
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
        
        # Buat file .streamlit/secrets.toml
        with open('.streamlit/secrets.toml', 'w') as f:
            f.write('[GOOGLE_CREDENTIALS]\n')
            
            for key, value in creds.items():
                if key == 'private_key':
                    # Private_key perlu penanganan khusus
                    # Ganti newline dengan \n dan bungus dengan kutip
                    value = value.replace('\n', '\\n')
                    f.write(f'{key} = "{value}"\n')
                elif isinstance(value, str):
                    f.write(f'{key} = "{value}"\n')
                elif isinstance(value, (int, float, bool)):
                    f.write(f'{key} = {value}\n')
                else:
                    f.write(f'{key} = "{value}"\n')
        
        print("✅ File .streamlit/secrets.toml berhasil dibuat!")
        print("\n📋 Copy isi file ini untuk di-paste ke Streamlit Cloud Secrets:")
        print("="*50)
        with open('.streamlit/secrets.toml', 'r') as f:
            print(f.read())
        print("="*50)
        
    except FileNotFoundError:
        print("❌ File credentials.json tidak ditemukan!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    json_to_toml()