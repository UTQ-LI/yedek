import winreg, os, socket, sqlite3, file_decompressor, pf_data, getSID, getProccesses, threading, shutil, GetChromeData
from datetime import timedelta, datetime
from colorama import Fore

class Functions:
    def __init__(self):
        self.errorFile = "errors.txt"
        self.logFile = "logs.log"

    def bytes_to_mb(self, bytes_value):
        return bytes_value / (1024 * 1024)

    def saveLog(self, LOG=None):
        with open(self.logFile, "a") as log:
            now = datetime.now()
            log.write(f"{now} : {LOG}\n")

    def get_regedit(self, hkey, regedit_key, file_name):
        try:
            print(f'{file_name} yapılıyor...')

            key = winreg.OpenKey(hkey, regedit_key)

            try:
                i = 0
                regeditData = {}

                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)

                        if isinstance(value, bytes):
                            regeditData[name] = value.replace(b'\x00', b'')
                        elif isinstance(value, int):
                            regeditData[name] = value
                        else:
                            regeditData[name] = value.replace('\x00', '')
                        i += 1
                    except WindowsError:
                        break

                winreg.CloseKey(key)

                self.saveLog(f"{regedit_key} : read all values")
                return regeditData.items()

            except Exception as e:
                self.saveLog(f"{key} : Error! {e}")
                print(f'{Fore.RED}Error! {e}{Fore.RESET}')
                return None

            finally:
                winreg.CloseKey(key)


        except Exception as e:
            print(f'{Fore.RED}Error! {e}{Fore.RESET}')
            return None

    def get_location(self, location, file_name, option=None, SQLiteCommand=None):
        result = []
        try:
            print(f"{file_name} yapılıyor...")

            if option == None:
                try:
                    for root, dirs, files in os.walk(location):
                        print(f'Klasör: {root}')
                        self.saveLog(f"{root} : opened")
                        for file in files:
                            print(f'Dosya: {file}')
                            self.saveLog(f"({root}) {file} : opened")
                            filePath = os.path.join(root, file)

                            if os.path.splitext(filePath)[1] == ".pf":
                                self.saveLog(f"({root}) {file} : reading header")
                                with open(filePath, "rb") as File:
                                    fileHeader = File.read(8)

                                if fileHeader[4:] == b'SCCA':
                                    prefetchData = pf_data.PrefetchData()

                                    self.saveLog(f"({root}) {file} ({fileHeader}): reading prefetch file...")
                                    _file_name, file_run_count, file_executed_times, volumes = prefetchData.read_prefetch_file(filePath)

                                    str_file_executed_times = [i.strftime("%Y-%m-%d %H:%M:%S") for i in file_executed_times]

                                    result.append({"number": 1, "File Name": _file_name, "File Run Count": file_run_count, "File Executed Times": str_file_executed_times, "Volumes": volumes})

                                elif fileHeader[0:3] == b'MAM':
                                    self.saveLog(f"({root}) {file} : ({fileHeader[0:3]}) detected!")
                                    decompressed_file_path = filePath[:-3] + '_decompressedFile.pf'

                                    self.saveLog(f"({root}) {file} : ({fileHeader}) decompressing...")
                                    file_decompressor.FileDecompressor(filePath, decompressed_file_path).decompress_file()

                                    prefetchData = pf_data.PrefetchData()

                                    self.saveLog(f"({root}) {file} ({fileHeader}): reading...")
                                    _file_name, file_run_count, file_executed_times, volumes = prefetchData.read_prefetch_file(decompressed_file_path)

                                    self.saveLog(f"({root}) {file} : deleting decompressing file...")
                                    os.remove(decompressed_file_path)

                                    str_file_executed_times = [i.strftime("%Y-%m-%d %H:%M:%S") for i in file_executed_times]

                                    result.append({"number": 1, "File Name": _file_name, "File Run Count": file_run_count, "File Executed Times": str_file_executed_times, "Volumes": volumes})

                                else:
                                    self.saveLog(f"({root}) {file} ({fileHeader}): Unknown file header!")
                                    print(f'{Fore.RED}Unknown file header! ({fileHeader}) File Path: {filePath}{Fore.RESET}')
                                    result.append({"number": 0, "File Name": file_name, "Error": "Unknown file header!"})

                            else:
                                with open(filePath, "rb") as File:
                                    if File.read(len("SQLite format 3")) != b"SQLite format 3":
                                        file_content = File.read().replace(b"\x00", b"").replace(b"\xff", b"")
                                        self.saveLog(f"({root}) {file} : readed")
                                    else:
                                        if SQLiteCommand is None:
                                            file_content = File.read().replace(b"\x00", b"").replace(b"\xff", b"")
                                            self.saveLog(f"({root}) {file} : readed")
                                        else:
                                            # SQLite Kodu eklenecek
                                            pass

                                result.append({"number": 0, "File Name": filePath, "File Content": file_content})
                except PermissionError:
                    print(f'{Fore.RED}Permission denied! File Path: {location}{Fore.RESET}')
                    self.saveLog(f"{location} : Permission denied")
                    result.append({"number": 0, "File Name": file_name, "Error": "Permission denied"})
                    return result
                except FileNotFoundError:
                    print(f'{Fore.RED}File not found! File Path: {location}{Fore.RESET}')
                    self.saveLog(f"{location} : File not found")
                    result.append({"number": 0, "File Name": file_name, "Error": "File not found"})
                    return result
                except Exception as e:
                    self.saveLog(f"Error: {file_name} : {e}")
                    print(f"{Fore.RED}Error: {file_name} : {e}{Fore.RESET}")
                    result.append({"number": 0, "File Name": file_name, "Error": e})
                    return result

                return result

            elif option == 1:
                try:
                    with open(location, "rb") as File:
                        if File.read(len("SQLite format 3")) != b"SQLite format 3":
                            self.saveLog(f"({location}) read : {file_name}")
                            file_content = File.read().replace(b'\x00', b'').replace(b'\xff', b'')
                        else:
                            if SQLiteCommand is None:
                                file_content = File.read().replace(b"\x00", b"").replace(b"\xff", b"")
                                self.saveLog(f"({location}) read : {file_name}")
                            else:
                                # SQLite Kodu eklenecek
                                pass

                    result.append({"number": 0, "File Name": file_name, "File Content": file_content})
                except PermissionError:
                    self.saveLog(f"{location} : Permission denied")
                    print(f'{Fore.RED}Permission denied! File Path: {location}{Fore.RESET}')
                    result.append({"number": 0, "File Name": file_name, "Error": "Permission denied"})
                    return result
                except FileNotFoundError:
                    self.saveLog(f"{location} : File not found")
                    print(f'{Fore.RED}File not found! File Path: {location}{Fore.RESET}')
                    result.append({"number": 0, "File Name": file_name, "Error": "File not found"})
                    return result
                except Exception as e:
                    self.saveLog(f"Error: {file_name} : {e}")
                    print(f"{Fore.RED}Error: {file_name} : {e}{Fore.RESET}")
                    result.append({"number": 0, "File Name": file_name, "Error": e})
                    return result

                return result

            else:
                print(f'{Fore.RED}Unknown option! ({option}) File Path: {location}{Fore.RESET}')
                return None

        except Exception as e:
            self.saveLog(f"Error: {file_name} : {e}")
            print(f"{Fore.RED}Error: {file_name} : {e}{Fore.RESET}")
            result.append({"number": 0, "File Name": file_name, "Error": e})
            return result


Functions = Functions()

class Tuple:
    getLocationTuple = {}
    getRegeditTuple = {}

class Application_Execution:
    def MiniDump(self):
        location = f"{os.environ.get('SYSTEMROOT')}"
        extract_location = os.path.join(location, "Minidump")
        Tuple.getLocationTuple["MiniDump"] = Functions.get_location(extract_location, "MiniDump.txt")

    def CrashDump(self):
        extract_location = os.path.join(os.environ.get('SYSTEMROOT'), 'MEMORY.DMP')
        Tuple.getLocationTuple["CrashDump"] = Functions.get_location(extract_location, "CrashDump.txt")

    def Shimcache(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache"
        Tuple.getRegeditTuple["Shimcache"] = Functions.get_regedit(hkey, regedit_key, "Shimcache.txt")

    def Task_Bar_Feature_Usage(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\FeatureUsage"
        Tuple.getRegeditTuple["Task Bar Feature Usage"] = Functions.get_regedit(hkey, regedit_key, "Task_Bar_Feature_Usage.txt")

    def Amache(self):
        location = rf"{os.environ.get('SYSTEMROOT')}\appcompat\Programs\Amcache.hve"
        Tuple.getLocationTuple["Amache"] = Functions.get_location(location, "Amache.txt")

    def Jump_Lists(self):
        location = f"{os.environ.get('USERPROFILE')}"
        extract_location = os.path.join(location, "AppData", "Roaming", "Microsoft", "Windows", "Recent", "AutomaticDestinations")
        Tuple.getLocationTuple["Jump Lists"] = Functions.get_location(extract_location, "Jump_Lists.txt")

    def Last_Visited_MRU(self):
        hkey = winreg.HKEY_CURRENT_USER
        regedit_key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedPidlMRU"
        Tuple.getRegeditTuple["Last Visited MRU"] = Functions.get_regedit(hkey, regedit_key, "Last_Visited_MRU.txt")

    def Commands_Executed_in_the_Run_Dialog(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU"
        Tuple.getRegeditTuple["Commands Executed in the Run Dialog"] = Functions.get_regedit(hkey, regedit_key, "Commands_Executed_in_the_Run_Dialog.txt")

    # Burası düzenlenecek!
    
    # def Windows10_Timeline(self):
    #     try:
    #         account_id = f"L.{os.getlogin()}"
    #         target_directory = rf"{os.environ.get('%USERPROFILE%')}\AppData\Local\ConnectedDevicesPlatform\{account_id}\ActivitiesCache.db"
    #
    #         conn = sqlite3.connect(target_directory, timeout=10)
    #         cursor = conn.cursor()
    #
    #         cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    #         tables = cursor.fetchall()
    #
    #         with open("Windows_Timeline.txt", "w") as TimelineFile:
    #             for table in tables:
    #                 table_name = table[0]
    #                 TimelineFile.write(str(f"--------------------- {table_name} ---------------------\n"))
    #                 cursor.execute(f"SELECT * FROM {table_name};")
    #                 rows = cursor.fetchall()
    #
    #                 for row in rows:
    #                     TimelineFile.write(str(row))
    #                     TimelineFile.write("\n")
    #
    #                 TimelineFile.write("\n")
    #
    #         conn.close()
    #     except sqlite3.Error as sqlite_error:
    #         print(f"{Fore.RED}Sqlite Error! : {sqlite_error}{Fore.RESET}")
    #
    #     except Exception as e:
    #         print(f"{Fore.RED}Error! : {e}{Fore.RESET}")

    # def BAMDAM(self):
    #     # Yönetici izni sorunu var
    #     SID = getSID.GetSID().get_user_sid()
    #     print(f"User SID: {SID}")
    #     hkey = winreg.HKEY_LOCAL_MACHINE
    #     regedit_key = rf"SYSTEM\CurrentControlSet\Services\bam\State\UserSettings\{SID}"
    #     function.get_regedit(hkey, regedit_key, "BAMDAM.txt")
    #     Tuple.getRegeditTuple["BAMDAM"] = function.get_regedit(hkey, regedit_key, "BAMDAM.txt")

    def SRUM(self):
        location = rf"{os.environ.get('SYSTEMROOT')}\System32\sru"
        Tuple.getLocationTuple["SRUM"] = Functions.get_location(location, "SRUM.txt")

    def Prefetch(self):
        location = rf"{os.environ.get('SYSTEMROOT')}\Prefetch"
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters"
        Tuple.getLocationTuple["Prefetch"] = Functions.get_location(location, "Prefetch.txt")
        Tuple.getRegeditTuple["Prefetch"] = Functions.get_regedit(hkey, regedit_path, "Prefetch(Regedit).txt")

    def CapabilityAccessManager(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        hkey_ = winreg.HKEY_LOCAL_MACHINE
        regedit_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore"
        regedit_path_ = r"Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore"
        Tuple.getRegeditTuple["Capability AccessManager"] = Functions.get_regedit(hkey, regedit_path, "CapabilityAccessManager.txt")
        Tuple.getRegeditTuple["Capability AccessManager2"] = Functions.get_regedit(hkey_, regedit_path_, "CapabilityAccessManager2.txt")

    # def UserAssist(self):
    #     # GUID bakılacak
    #     hkey = winreg.HKEY_CURRENT_USER
    #     regedit_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist\{GUID}\Count"
    #     function.get_regedit(hkey, regedit_path, "UserAssist.txt")
    #     Tuple.getRegeditTuple["UserAssist"] = function.get_regedit(hkey, regedit_path, "UserAssist.txt")
    #     pass

class File_and_Folder_Opening:
    def OpenSaveMRU(self):
        hkey = winreg.HKEY_CURRENT_USER
        regedit_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSavePIDlMRU"
        Tuple.getRegeditTuple["Open Save MRU"] = Functions.get_regedit(hkey, regedit_path, "OpenSaveMRU.txt")

    def RecentFiles(self):
        hkey = winreg.HKEY_CURRENT_USER
        regedit_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs"
        Tuple.getRegeditTuple["Recent Files"] = Functions.get_regedit(hkey, regedit_path, "RecentFiles.txt")

    def MS_Word_Reading_Locations(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_path = r"Software\Microsoft\Office\<Version>\Word\Reading Locations"
        Tuple.getRegeditTuple["MS Word Reading Locations"] = Functions.get_regedit(hkey, regedit_path, "MS_Word_Reading_Locations.txt")

    def Last_Visited_MRU(self):
        hkey = winreg.HKEY_CURRENT_USER
        regedit_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedPidlMRU"
        Tuple.getRegeditTuple["Last Visited MRU"] = Functions.get_regedit(hkey, regedit_path, "Last_Visited_MRU.txt")

    def Shorcut_Files(self):
        pass

    def OfficeRecentFiles(self):
        hkey = winreg.HKEY_CURRENT_USER
        hkey_ = winreg.HKEY_CURRENT_USER
        hkey__ = winreg.HKEY_CURRENT_USER
        regedit_path = r"Software\Microsoft\Office\<Version>\<AppName>\File MRU"
        regedit_path_ = r"Software\Microsoft\Office\<Version>\<AppName>\User MRU\LiveId_####\File MRU"
        regedit_path__ = r"Software\Microsoft\Office\<Version>\<AppName>\User MRU\AD_####\File MRU"
        Tuple.getRegeditTuple["Office Recent Files"] = Functions.get_regedit(hkey, regedit_path, "OfficeRecentFiles.txt")
        Tuple.getRegeditTuple["Office Recent Files2"] = Functions.get_regedit(hkey_, regedit_path_, "OfficeRecentFiles2.txt")
        Tuple.getRegeditTuple["Office Recent Files3"] = Functions.get_regedit(hkey__, regedit_path__, "OfficeRecentFiles3.txt")

    def ShellBags(self):
        hkey = winreg.HKEY_CURRENT_USER
        hkey_ = winreg.HKEY_CURRENT_USER
        regedit_path = r"Software\Microsoft\Windows\Shell\BagMRU"
        regedit_path_ = r"Software\Microsoft\Windows\Shell\Bags"
        Tuple.getRegeditTuple["Shell Bags"] = Functions.get_regedit(hkey, regedit_path, "ShellBags.txt")
        Tuple.getRegeditTuple["Shell Bags2"] = Functions.get_regedit(hkey_, regedit_path_, "ShellBags2.txt")

    def JumpLists(self):
        location = f"{os.environ.get('USERPROFILE')}"
        extract_location = os.path.join(location, "AppData", "Roaming", "Microsoft", "Windows", "Recent", "AutomaticDestinations")
        extract_location_ = os.path.join(location, "AppData", "Roaming", "Microsoft", "Windows", "Recent", "AutomaticDestinations")
        Tuple.getLocationTuple["Jump Lists"] = Functions.get_location(extract_location, "JumpLists.txt")
        Tuple.getLocationTuple["Jump Lists2"] = Functions.get_location(extract_location_, "JumpLists2.txt")

    def OfficeTrustRecords(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_path = r"Software\Microsoft\Office\<Version>\<AppName>\Security\Trusted Documents\TrustRecords"
        Tuple.getRegeditTuple["Office Trust Records"] = Functions.get_regedit(hkey, regedit_path, "OfficeTrustRecords.txt")

    def OfficeOAlerts(self):
        pass

    def InternetExplorerFile(self):
        pass

class Deleted_Items_and_File_Existence:
    def ThumbsDB(self):
        pass

    def WindowsSearchDatabase(self):
        location = rf"{os.environ.get('PROGRAMDATA')}\Microsoft\Search\Data\Applications\Windows\Windows.edb"
        location_ = rf"{os.environ.get('PROGRAMDATA')}\Microsoft\Search\Data\Applications\Windows\GatherLogs\SystemIndex"
        Tuple.getLocationTuple["Windows Search Database"] = Functions.get_location(location, "WindowsSearchDatabase.txt", 1)
        Tuple.getLocationTuple["Windows Search Database2"] = Functions.get_location(location_, "WindowsSearchDatabase2.txt", 1)

    def InternetExplorerFile(self):
        pass

    def SearchWordWheelQuery(self):
        hkey = winreg.HKEY_CURRENT_USER
        regedit_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\WordWheelQuery"
        Tuple.getRegeditTuple["Search Word Wheel Query"] = Functions.get_regedit(hkey, regedit_path, "SearchWordWheelQuery.txt")

    def UserTypedPaths(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths"
        Tuple.getRegeditTuple["User Typed Paths"] = Functions.get_regedit(hkey, regedit_path, "UserTypedPaths.txt")

    def Thumbcache(self):
        pass

    def RecycleBin(self):
        location = r"C:\$Recycle.Bin"
        Tuple.getLocationTuple["Recycle"] = Functions.get_location(location, "Recycle.txt", 1)

class Browser_Activity:
    def HistoryAndDownloadHistory(self):
        firefox_location = rf"{os.environ.get('USERPROFILE')}\AppData\Roaming\Mozilla\Firefox\Profiles"
        chrome_location = rf"{os.environ.get('USERPROFILE')}\AppData\Local\Google\Chrome\User Data\Default\History"
        edge_location = rf"{os.environ.get('USERPROFILE')}AppData\Local\MicrosoftEdge\User\Default"

        Tuple.getLocationTuple["Firefox History"] = Functions.get_location(firefox_location, "FirefoxHistory.txt")
        Tuple.getLocationTuple["Chrome History"] = GetChromeData.GetChromeHistory().get_browser_history(chrome_location, Functions)
        Tuple.getLocationTuple["Edge History"] = Functions.get_location(edge_location, "EdgeHistory.txt")

    def MediaHistory(self):
        pass

    def HTML5WebStorage(self):
        chrome_location = rf"{os.environ.get('USERPROFILE')}\AppData\Local\Google\Chrome\User Data\Default\Local Storage"
        edge_location = rf"{os.environ.get('USERPROFILE')}AppData\Local\MicrosoftEdge\User\Default\Local Storage"

        Tuple.getLocationTuple["Chrome Local Storage"] = Functions.get_location(chrome_location, "ChromeLocalStorage.txt")
        Tuple.getLocationTuple["Edge Local Storage"] = Functions.get_location(edge_location, "EdgeLocalStorage.txt")
    def HTML5FileSystem(self):
        pass

    def AutoCompleteData(self):
        chrome_location_history = rf"{os.environ.get('USERPROFILE')}\AppData\Local\Google\Chrome\User Data\Default\History"
        chrome_location_WebData = rf"{os.environ.get('USERPROFILE')}\AppData\Local\Google\Chrome\User Data\Default\Web Data"
        chrome_location_Shortcuts = rf"{os.environ.get('USERPROFILE')}\AppData\Local\Google\Chrome\User Data\Default\Shortcuts"
        chrome_location_NetworkActionPredictor = rf"{os.environ.get('USERPROFILE')}\AppData\Local\Google\Chrome\User Data\Default\Network Action Predictor"
        chrome_location_LoginData = rf"{os.environ.get('USERPROFILE')}\AppData\Local\Google\Chrome\User Data\Default\Login Data"

        edge_location_history = rf"{os.environ.get('USERPROFILE')}AppData\Local\MicrosoftEdge\User\Default\History"
        edge_location_WebData = rf"{os.environ.get('USERPROFILE')}AppData\Local\MicrosoftEdge\User\Default\Web Data"
        edge_location_Shortcuts = rf"{os.environ.get('USERPROFILE')}AppData\Local\MicrosoftEdge\User\Default\Shortcuts"
        edge_location_NetworkActionPredictor = rf"{os.environ.get('USERPROFILE')}AppData\Local\MicrosoftEdge\User\Default\Network Action Predictor"
        edge_location_LoginData = rf"{os.environ.get('USERPROFILE')}AppData\Local\MicrosoftEdge\User\Default\Login Data"

        Tuple.getLocationTuple["Chrome History"] = Functions.get_location(chrome_location_history, "ChromeHistory.txt", 1)
        Tuple.getLocationTuple["Chrome Web Data"] = Functions.get_location(chrome_location_WebData, "ChromeWebData.txt", 1)
        Tuple.getLocationTuple["Chrome Shortcuts"] = Functions.get_location(chrome_location_Shortcuts, "ChromeShortcuts.txt", 1)
        Tuple.getLocationTuple["Chrome Network Action Predictor"] = Functions.get_location(chrome_location_NetworkActionPredictor, "ChromeNetworkActionPredictor.txt", 1)
        Tuple.getLocationTuple["Chrome Login Data"] = GetChromeData.GetChromeLoginData().get_login_data(chrome_location_LoginData, Functions)

        Tuple.getLocationTuple["Edge History"] = Functions.get_location(edge_location_history, "EdgeHistory.txt", 1)
        Tuple.getLocationTuple["Edge Web Data"] = Functions.get_location(edge_location_WebData, "EdgeWebData.txt", 1)
        Tuple.getLocationTuple["Edge Shortcuts"] = Functions.get_location(edge_location_Shortcuts, "EdgeShortcuts.txt", 1)
        Tuple.getLocationTuple["Edge Network Action Predictor"] = Functions.get_location(edge_location_NetworkActionPredictor, "EdgeNetworkActionPredictor.txt", 1)
        Tuple.getLocationTuple["Edge Login Data"] = Functions.get_location(edge_location_LoginData, "EdgeLoginData.txt", 1)

    def Browser_Preferences(self):
        chrome_location_preferences = rf"{os.environ.get('USERPROFILE')}\AppData\Local\Google\Chrome\User Data\Default\Preferences"
        edge_location_preferences = rf"{os.environ.get('USERPROFILE')}AppData\Local\MicrosoftEdge\User\Default\Preferences"

        Tuple.getLocationTuple["Chrome Preferences"] = Functions.get_location(chrome_location_preferences, "ChromePreferences.txt", 1)
        Tuple.getLocationTuple["Edge Preferences"] = Functions.get_location(edge_location_preferences, "EdgePreferences.txt", 1)

    def Cache(self):
        pass

    def Bookmarks(self):
        chrome_location_bookmarks = rf"{os.environ.get('USERPROFILE')}\AppData\Local\Google\Chrome\User Data\Default\Bookmarks"
        chrome_location_bookmarks2 = rf"{os.environ.get('USERPROFILE')}\AppData\Local\Google\Chrome\User Data\Default\Bookmarks.bak"
        edge_location_bookmarks = rf"{os.environ.get('USERPROFILE')}AppData\Local\MicrosoftEdge\User\Default\Bookmarks"
        edge_location_bookmarks2 = rf"{os.environ.get('USERPROFILE')}AppData\Local\MicrosoftEdge\User\Default\Bookmarks.msbak"

        Tuple.getLocationTuple["Chrome Bookmarks"] = Functions.get_location(chrome_location_bookmarks, "ChromeBookmarks.txt", 1)
        Tuple.getLocationTuple["Edge Bookmarks"] = Functions.get_location(edge_location_bookmarks, "EdgeBookmarks.txt", 1)
        Tuple.getLocationTuple["Chrome Bookmarks.bak"] = Functions.get_location(chrome_location_bookmarks2, "ChromeBookmarks.txt", 1)
        Tuple.getLocationTuple["Edge Bookmarks.msbak"] = Functions.get_location(edge_location_bookmarks2, "EdgeBookmarks.txt", 1)

    def Stored_Credentials(self):
        chrome_location_login_data = rf"{os.environ.get('USERPROFILE')}\AppData\Local\Google\Chrome\User Data\Default\Login Data"
        edge_location_login_data = rf"{os.environ.get('USERPROFILE')}AppData\Local\MicrosoftEdge\User\Default\Login Data"

        Tuple.getLocationTuple["Chrome Login Data"] = Functions.get_location(chrome_location_login_data, "ChromeLoginData.txt", 1)
        Tuple.getLocationTuple["Edge Login Data"] = Functions.get_location(edge_location_login_data, "EdgeLoginData.txt", 1)

    def Browser_Downloads(self):
        chrome_downloads = rf"{os.environ.get('USERPROFILE')}\AppData\Local\Google\Chrome\User Data\Default\History"
        edge_location_downloads = rf"{os.environ.get('USERPROFILE')}AppData\Local\MicrosoftEdge\User\Default\History"

        Tuple.getLocationTuple["Chrome Downloads"] = GetChromeData.GetChromeDownloadHistory().get_browser_download_history(chrome_downloads, Functions)
        Tuple.getLocationTuple["Edge History"] = Functions.get_location(edge_location_downloads, "EdgeHistory.txt", 1)

    def Extensions(self):
        chrome_location_extensions = rf"{os.environ.get('USERPROFILE')}\AppData\Local\Google\Chrome\User Data\Default\Extensions"
        edge_location_extensions = rf"{os.environ.get('USERPROFILE')}AppData\Local\MicrosoftEdge\User\Default\Extensions"

        Tuple.getLocationTuple["Chrome Extensions"] = Functions.get_location(chrome_location_extensions, "ChromeExtensions.txt")
        Tuple.getLocationTuple["Edge Extensions"] = Functions.get_location(edge_location_extensions, "EdgeExtensions.txt")

    def Session_Restore(self):
        chrome_location_session = rf"{os.environ.get('USERPROFILE')}\AppData\Local\Google\Chrome\User Data\Default\Sessions"
        edge_location_session = rf"{os.environ.get('USERPROFILE')}AppData\Local\MicrosoftEdge\User\Default\Sessions"

        Tuple.getLocationTuple["Chrome Sessions"] = Functions.get_location(chrome_location_session, "ChromeSessions.txt")
        Tuple.getLocationTuple["Edge Sessions"] = Functions.get_location(edge_location_session, "EdgeSessions.txt")

    def Cookies(self):
        chrome_location_sessions = rf"{os.environ.get('USERPROFILE')}\AppData\Local\Google\Chrome\User Data\Default\Network\Cookies"
        edge_location_sessions = rf"{os.environ.get('USERPROFILE')}AppData\Local\MicrosoftEdge\User\Default\Network\Cookies"

        Tuple.getLocationTuple["Chrome Cookies"] = Functions.get_location(chrome_location_sessions, "ChromeCookies.txt", 1)
        Tuple.getLocationTuple["Edge Cookies"] = Functions.get_location(edge_location_sessions, "EdgeCookies.txt", 1)

class CloudStorage:
    def OneDrive(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_path = r"Software\Microsoft\OneDrive\Accounts\<Personal | Business1>"
        Tuple.getRegeditTuple["Onedrive"] = Functions.get_regedit(hkey, regedit_path, "Onedrive.txt")

    def Google_Drive_for_Desktop(self):
        pass

    def Box_Drive(self):
        pass

    def Dropbox(self):
        pass

class Account_Usage:
    def Cloud_Account_Details(self):
        pass

    def Last_Login_and_Password_Change(self):
        pass

    def Service_Events(self):
        location = os.environ.get('SYSTEMROOT')
        extract_location = os.path.join(location, "System32", "winevt", "logs", "System.evtx")
        extract_location_ = os.path.join(location, "System32", "winevt", "logs", "Security.evtx")
        Tuple.getLocationTuple["Service Events"] = Functions.get_location(extract_location, "Service_Events.txt", 1)
        Tuple.getLocationTuple["Service Events2"] = Functions.get_location(extract_location_, "Service_Events.txt", 1)

    def User_Accounts(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList"
        Tuple.getRegeditTuple["User Accounts"] = Functions.get_regedit(hkey, regedit_key, "User_Accounts.txt")

    def RDP(self):
        location = os.environ.get('SYSTEMROOT')
        extract_location = os.path.join(location, "System32", "winevt", "logs", "Security.evtx")
        Tuple.getLocationTuple["RDP"] = Functions.get_location(extract_location, "RDP.txt", 1)

    def SuccessfulFailedLogons(self):
        location = os.environ.get('SYSTEMROOT')
        extract_location = os.path.join(location, "System32", "winevt", "logs", "Security.evtx")
        Tuple.getLocationTuple["Successful Failed Logons"] = Functions.get_location(extract_location, "SuccessfulFailedLogons.txt", 1)

    def Authentication_Events(self):
        location = os.environ.get('SYSTEMROOT')
        extract_location = os.path.join(location, "System32", "winevt", "logs", "Security.evtx")
        Tuple.getLocationTuple["Authentication Events"] = Functions.get_location(extract_location, "Authentication_Events.txt", 1)

    def Logon_Event_Types(self):
        location = os.environ.get('SYSTEMROOT')
        extract_location = os.path.join(location, "System32", "winevt", "logs", "Security.evtx")
        Tuple.getLocationTuple["Logon Event Types"] = Functions.get_location(extract_location, "Logon_Event_Types.txt", 1)

class Network_Activity_and_Physical_Location:
    def Network_History(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
        regedit_key_ = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkCards"
        regedit_key__ = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\Signatures\Unmanaged"
        regedit_key___ = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\Signatures\Managed"
        regedit_key____ = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\Nla\Cache"
        regedit_key_____ = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\Profiles"
        Tuple.getRegeditTuple["Network History"] = Functions.get_regedit(hkey, regedit_key, "Network_History.txt")
        Tuple.getRegeditTuple["Network History2"] = Functions.get_regedit(hkey, regedit_key_, "Network_History2.txt")
        Tuple.getRegeditTuple["Network History3"] = Functions.get_regedit(hkey, regedit_key__, "Network_History3.txt")
        Tuple.getRegeditTuple["Network History4"] = Functions.get_regedit(hkey, regedit_key___, "Network_History4.txt")
        Tuple.getRegeditTuple["Network History5"] = Functions.get_regedit(hkey, regedit_key____, "Network_History5.txt")
        Tuple.getRegeditTuple["Network History6"] = Functions.get_regedit(hkey, regedit_key_____, "Network_History6.txt")

    def Browser_URL_Parameters(self):
        pass

    def Timezone(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"SYSTEM\CurrentControlSet\Control\TimeZoneInformation"
        Tuple.getRegeditTuple["Browser URL Parameters"] = Functions.get_regedit(hkey, regedit_key, "Browser_URL_Parameters.txt")

    def WLAN_Evet_Log(self):
        pass

    def Network_Interfaces(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
        regedit_key_ = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkCards"
        Tuple.getRegeditTuple["Timezone"] = Functions.get_regedit(hkey, regedit_key, "Timezone.txt")
        Tuple.getRegeditTuple["Timezone2"] = Functions.get_regedit(hkey, regedit_key_, "Timezone2.txt")

    def SRUM(self):
        location = rf"{os.environ.get('SYSTEMROOT')}\System32\SRU"
        Tuple.getLocationTuple["SRUM"] = Functions.get_location(location, "SRUM.txt")

class External_Device_USB_Usage:
    def USB_Device_Identification(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"SYSTEM\CurrentControlSet\Enum\USBSTOR"
        regedit_key_ = r"SYSTEM\CurrentControlSet\Enum\USB"
        regedit_key__ = r"SYSTEM\CurrentControlSet\Enum\SCSI"
        regedit_key___ = r"SYSTEM\CurrentControlSet\Enum\HID"
        Tuple.getRegeditTuple["USB Device Identification"] = Functions.get_regedit(hkey, regedit_key, "USB_Device_Identification.txt")
        Tuple.getRegeditTuple["USB Device Identification2"] = Functions.get_regedit(hkey, regedit_key_, "USB_Device_Identification2.txt")
        Tuple.getRegeditTuple["USB Device Identification3"] = Functions.get_regedit(hkey, regedit_key__, "USB_Device_Identification3.txt")
        Tuple.getRegeditTuple["USB Device Identification4"] = Functions.get_regedit(hkey, regedit_key___, "USB_Device_Identification4.txt")

    def Event_Logs(self):
        location = os.environ.get('SYSTEMROOT')
        extract_location = os.path.join(location, "System32", "winevt", "logs", "System.evtx")
        extract_location_ = os.path.join(location, "System32", "winevt", "logs", "Security.evtx")
        extract_location__ = os.path.join(location, "System32", "winevt", "logs", "Microsoft-Windows-Partition", "Diagnostic.evtx")
        Tuple.getLocationTuple["Event Logs"] = Functions.get_location(extract_location, "Event_Logs.txt", 1)
        Tuple.getLocationTuple["Event Logs2"] = Functions.get_location(extract_location_, "Event_Logs2.txt", 1)
        Tuple.getLocationTuple["Event Logs3"] = Functions.get_location(extract_location__, "Event_Logs3.txt", 1)

    def Drive_Letter_and_Volume_Name(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"SOFTWARE\Microsoft\Windows Portable Devices\Devices"
        regedit_key_ = r"SOFTWARE\Microsoft\Windows Search\VolumeInfoCache"
        Tuple.getRegeditTuple["Event Logs"] = Functions.get_regedit(hkey, regedit_key, "Event_Logs.txt")
        Tuple.getRegeditTuple["Event Logs2"] = Functions.get_regedit(hkey, regedit_key_, "Event_Logs2.txt")

    def User_Information(self):
        pass

    def ShortcutFiles(self):
        location = os.environ.get('USERPROFILE')
        extract_location = os.path.join(location, "AppData", "Roaming", "Microsoft", "Windows", "Recent")
        extract_location_ = os.path.join(location, "AppData", "Roaming", "Microsoft", "Office", "Recent")
        Tuple.getLocationTuple["Shortcut Files"] = Functions.get_location(extract_location, "ShortcutFiles.txt", 1)
        Tuple.getLocationTuple["Shortcut Files2"] = Functions.get_location(extract_location_, "ShortcutFiles2.txt", 1)

    def Connection_Timestamps(self):
        location = rf"{os.environ.get('SYSTEMROOT')}\inf"
        Tuple.getLocationTuple["Connection Timestamps"] = Functions.get_location(location, "Connection_Timestamps.txt")

    def VSN(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"SOFTWARE\Microsoft\WindowsNT\CurrentVersion\EMDMgmt"
        Tuple.getRegeditTuple["VSN"] = Functions.get_regedit(hkey, regedit_key, "VSN.txt")

class SystemInformation:
    # Bu düzenlencecek
    # def Windows_Defender(self):
    #     try:
    #         target_directory = rf"{os.environ.get('PROGRAMDATA')}\Microsoft\Windows Defender\Support"
    #
    #         files = os.listdir(target_directory)
    #
    #         with open("Windows_Defender.txt", "w") as WindowsDefender:
    #             for file in files:
    #                 file_path = os.path.join(target_directory, file)
    #                 with open(file_path, "r") as current_file:
    #                     file_content = current_file.read()
    #                     WindowsDefender.write(f"--------------------- {file} ---------------------\n{file_content}\n")
    #
    #     except Exception as e:
    #         with open("defenderError.txt", "w") as defenderErrFile:
    #             defenderErrFile.write(f"Error! : {e}")

    def Operating_System_Version(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        regedit_key_ = r"SYSTEM\Setup\Source OS"
        Tuple.getRegeditTuple["Operating System Version"] = Functions.get_regedit(hkey, regedit_key, "Operating_System_Version.txt")
        Tuple.getRegeditTuple["Operating System Version2"] = Functions.get_regedit(hkey, regedit_key_, "Operating_System_Version2.txt")
        
    def ComputerName(self):
        Tuple.getLocationTuple["Computer Name"] = {socket.gethostname()}

    def GetProcesses(self):
        print("Processes yapılıyor...")
        Tuple.getLocationTuple["Processes"] = getProccesses.GetProccesses.getProccesses()

    def System_Boot_Autostart_Programs(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
        regedit_key_ = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run"
        regedit_key__ = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        regedit_key___ = r"SYSTEM\CurrentControlSet\Services"
        Tuple.getRegeditTuple["System Boot Autostart Programs"] = Functions.get_regedit(hkey, regedit_key, "System_Boot_Autostart_Programs.txt")
        Tuple.getRegeditTuple["System Boot Autostart Programs2"] = Functions.get_regedit(hkey, regedit_key_, "System_Boot_Autostart_Programs2.txt")
        Tuple.getRegeditTuple["System Boot Autostart Programs3"] = Functions.get_regedit(hkey, regedit_key__, "System_Boot_Autostart_Programs3.txt")
        Tuple.getRegeditTuple["System Boot Autostart Programs4"] = Functions.get_regedit(hkey, regedit_key___, "System_Boot_Autostart_Programs4.txt")

    def System_Last_Shutdown_Time(self):
        hkey = winreg.HKEY_CURRENT_USER
        regedit_key = r"SYSTEM\CurrentControlSet\Control\Windows"
        regedit_key_ = r"SYSTEM\CurrentControlSet\Control\Watchdog\Display"
        Tuple.getRegeditTuple["System Last Shutdown Time"] = Functions.get_regedit(hkey, regedit_key, "System_Last_Shutdown_Time.txt")
        Tuple.getRegeditTuple["System Last Shutdown Time2"] = Functions.get_regedit(hkey, regedit_key_, "System_Last_Shutdown_Time2.txt")

class Start:
    def StartAll(self):
        application_Execution = Application_Execution()
        file_and_Folder_Opening = File_and_Folder_Opening()
        deleted_Items_and_File_Existence = Deleted_Items_and_File_Existence()
        browser_activity = Browser_Activity()
        cloudStorage = CloudStorage()
        account_Usage = Account_Usage()
        network_Activity_and_Physical_Location = Network_Activity_and_Physical_Location()
        external_Device_USB_Usage = External_Device_USB_Usage()
        systemInformation = SystemInformation()

        threads = []

        for func in [application_Execution.MiniDump, application_Execution.CrashDump, application_Execution.Shimcache,
                     application_Execution.Task_Bar_Feature_Usage,
                     application_Execution.Amache, application_Execution.Jump_Lists,
                     application_Execution.Last_Visited_MRU,
                     application_Execution.Commands_Executed_in_the_Run_Dialog, application_Execution.SRUM,
                     application_Execution.Prefetch,
                     application_Execution.CapabilityAccessManager]:
            thread = threading.Thread(target=func)
            thread.start()
            threads.append(thread)

        for func in [file_and_Folder_Opening.OpenSaveMRU, file_and_Folder_Opening.RecentFiles,
                     file_and_Folder_Opening.MS_Word_Reading_Locations,
                     file_and_Folder_Opening.Last_Visited_MRU, file_and_Folder_Opening.Shorcut_Files,
                     file_and_Folder_Opening.OfficeRecentFiles,
                     file_and_Folder_Opening.ShellBags, file_and_Folder_Opening.JumpLists,
                     file_and_Folder_Opening.OfficeTrustRecords,
                     file_and_Folder_Opening.OfficeOAlerts, file_and_Folder_Opening.InternetExplorerFile]:
            thread = threading.Thread(target=func)
            thread.start()
            threads.append(thread)

        for func in [deleted_Items_and_File_Existence.ThumbsDB, deleted_Items_and_File_Existence.WindowsSearchDatabase,
                     deleted_Items_and_File_Existence.InternetExplorerFile,
                     deleted_Items_and_File_Existence.SearchWordWheelQuery,
                     deleted_Items_and_File_Existence.UserTypedPaths, deleted_Items_and_File_Existence.Thumbcache,
                     deleted_Items_and_File_Existence.RecycleBin]:
            thread = threading.Thread(target=func)
            thread.start()
            threads.append(thread)

        for func in [browser_activity.HistoryAndDownloadHistory, browser_activity.MediaHistory,
                     browser_activity.HTML5WebStorage,
                     browser_activity.HTML5FileSystem, browser_activity.AutoCompleteData,
                     browser_activity.Browser_Preferences,
                     browser_activity.Cache, browser_activity.Bookmarks, browser_activity.Stored_Credentials,
                     browser_activity.Browser_Downloads,
                     browser_activity.Extensions, browser_activity.Session_Restore, browser_activity.Cookies]:
            thread = threading.Thread(target=func)
            thread.start()
            threads.append(thread)

        for func in [cloudStorage.OneDrive, cloudStorage.Google_Drive_for_Desktop, cloudStorage.Box_Drive,
                     cloudStorage.Dropbox]:
            thread = threading.Thread(target=func)
            thread.start()
            threads.append(thread)

        for func in [account_Usage.Cloud_Account_Details, account_Usage.Last_Login_and_Password_Change,
                     account_Usage.Service_Events,
                     account_Usage.User_Accounts, account_Usage.RDP, account_Usage.SuccessfulFailedLogons,
                     account_Usage.Authentication_Events, account_Usage.Logon_Event_Types]:
            thread = threading.Thread(target=func)
            thread.start()
            threads.append(thread)

        for func in [network_Activity_and_Physical_Location.Network_History,
                     network_Activity_and_Physical_Location.Browser_URL_Parameters,
                     network_Activity_and_Physical_Location.Timezone,
                     network_Activity_and_Physical_Location.WLAN_Evet_Log,
                     network_Activity_and_Physical_Location.Network_Interfaces,
                     network_Activity_and_Physical_Location.SRUM]:
            thread = threading.Thread(target=func)
            thread.start()
            threads.append(thread)

        for func in [external_Device_USB_Usage.USB_Device_Identification, external_Device_USB_Usage.Event_Logs,
                     external_Device_USB_Usage.Drive_Letter_and_Volume_Name, external_Device_USB_Usage.User_Information,
                     external_Device_USB_Usage.ShortcutFiles, external_Device_USB_Usage.Connection_Timestamps,
                     external_Device_USB_Usage.VSN]:
            thread = threading.Thread(target=func)
            thread.start()
            threads.append(thread)

        for func in [systemInformation.Operating_System_Version, systemInformation.ComputerName,
                     systemInformation.System_Boot_Autostart_Programs, systemInformation.System_Last_Shutdown_Time]:
            thread = threading.Thread(target=func)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
