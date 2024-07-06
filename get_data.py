import winreg, os, socket, sqlite3, file_decompressor, pf_data, getSID
from colorama import Fore

class Functions:
    def __init__(self):
        self.errorFile = "errors.txt"
        self.result = []

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
                        regeditData[name] = value
                        i += 1
                    except WindowsError:
                        break

                winreg.CloseKey(key)
                return regeditData.items()

            except Exception as e:
                print(f'{Fore.RED}Error! {e}{Fore.RESET}')

            finally:
                winreg.CloseKey(key)


        except Exception as e:
            print(f'{Fore.RED}Error! {e}{Fore.RESET}')
            return None

    def get_location(self, location, file_name, option=None):
        try:
            self.result.clear()
            print(f"{file_name} yapılıyor...")

            if option == None:
                for root, dirs, files in os.walk(location):
                    print(f'Klasör: {root}')
                    for file in files:
                        print(f'Dosya: {file}')
                        filePath = os.path.join(root, file)


                        if os.path.splitext(filePath)[1] == ".pf":
                            with open(filePath, "rb") as File:
                                fileHeader = File.read(8)

                            if fileHeader[4:] == b'SCCA':
                                prefetchData = pf_data.PrefetchData()

                                _file_name, file_run_count, file_executed_times, volumes = prefetchData.read_prefetch_file(filePath)

                                str_file_executed_times = [i.strftime("%Y-%m-%d %H:%M:%S") for i in file_executed_times]

                                self.result.append({"number": 1, "_file_name": _file_name, "file_run_count": file_run_count, "file_executed_times": str_file_executed_times, "volumes": volumes})

                            elif fileHeader[0:3] == b'MAM':
                                decompressed_file_path = filePath[:-3] + '_decompressedFile.pf'

                                file_decompressor.FileDecompressor(filePath, decompressed_file_path).decompress_file()

                                prefetchData = pf_data.PrefetchData()

                                _file_name, file_run_count, file_executed_times, volumes = prefetchData.read_prefetch_file(decompressed_file_path)

                                os.remove(decompressed_file_path)

                                str_file_executed_times = [i.strftime("%Y-%m-%d %H:%M:%S") for i in file_executed_times]

                                self.result.append({"number": 1, "_file_name": _file_name, "file_run_count": file_run_count, "file_executed_times": str_file_executed_times, "volumes": volumes})

                            else:
                                print(f'Unknown file header! ({fileHeader}) File Path: {filePath}')

                        else:
                            with open(filePath, "rb") as File:
                                file_content = File.read()

                            self.result.append({"number": 0, "_file_name": filePath, "file_content": file_content})

                    return self.result

            elif option == 1:
                with open(location, "rb") as File:
                    file_content = File.read()

                self.result.append({"number": 0, "_file_name": location, "file_content": file_content})
                return self.result

            else:
                print(f'Unknown option! ({option}) File Path: {location}')

        except Exception as e:
            print(f"Error: {file_name} : {e}")
            return None


Functions = Functions()

class Tuple:
    getLocationTuple = {}
    getRegeditTuple = {}

class Application_Execution:
    def miniDump(self):
        location = f"{os.environ.get('SYSTEMROOT')}"
        extract_location = os.path.join(location, "Minidump")
        Tuple.getLocationTuple["miniDump"] = Functions.get_location(extract_location, "miniDump.txt")
        return Functions.get_location(extract_location, "miniDump.txt"), None

    def crashDump(self):
        extract_location = os.path.join(os.environ.get('SYSTEMROOT'), 'MEMORY.DMP')
        Tuple.getLocationTuple["crashDump"] = Functions.get_location(extract_location, "crashDump.txt")
        return Functions.get_location(extract_location, "crashDump.txt", 1), None

    def Shimcache(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache"
        Tuple.getRegeditTuple["Shimcache"] = Functions.get_regedit(hkey, regedit_key, "Shimcache.txt")
        return None, Functions.get_regedit(hkey, regedit_key, "Shimcache.txt")

    def Task_Bar_Feature_Usage(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\FeatureUsage"
        Tuple.getRegeditTuple["Task_Bar_Feature_Usage"] = Functions.get_regedit(hkey, regedit_key, "Task_Bar_Feature_Usage.txt")
        return None, Functions.get_regedit(hkey, regedit_key, "Task_Bar_Feature_Usage.txt")

    def Amache(self):
        location = rf"{os.environ.get('SYSTEMROOT')}\appcompat\Programs\Amcache.hve"
        Tuple.getLocationTuple["Amache"] = Functions.get_location(location, "Amache.txt")
        return Functions.get_location(location, "Amache.txt"), None

    def Jump_Lists(self):
        location = f"{os.environ.get('USERPROFILE')}"
        extract_location = os.path.join(location, "AppData", "Roaming", "Microsoft", "Windows", "Recent", "AutomaticDestinations")
        Tuple.getLocationTuple["Jump_Lists"] = Functions.get_location(extract_location, "Jump_Lists.txt")
        return Functions.get_location(extract_location, "Jump_Lists.txt"), None

    def Last_Visited_MRU(self):
        hkey = winreg.HKEY_CURRENT_USER
        regedit_key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedPidlMRU"
        Tuple.getRegeditTuple["Last_Visited_MRU"] = Functions.get_regedit(hkey, regedit_key, "Last_Visited_MRU.txt")
        return None, Functions.get_regedit(hkey, regedit_key, "Last_Visited_MRU.txt")

    def Commands_Executed_in_the_Run_Dialog(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU"
        Tuple.getRegeditTuple["Commands_Executed_in_the_Run_Dialog"] = Functions.get_regedit(hkey, regedit_key, "Commands_Executed_in_the_Run_Dialog.txt")
        return None, Functions.get_regedit(hkey, regedit_key, "Commands_Executed_in_the_Run_Dialog.txt")

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
    #     Functions.get_regedit(hkey, regedit_key, "BAMDAM.txt")
    #     Tuple.getRegeditTuple["BAMDAM"] = Functions.get_regedit(hkey, regedit_key, "BAMDAM.txt")

    def SRUM(self):
        location = rf"{os.environ.get('SYSTEMROOT')}\System32\sru"
        Functions.get_location(location, "SRUM.txt")
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
        Functions.get_regedit(hkey, regedit_path, "CapabilityAccessManager.txt")
        Functions.get_regedit(hkey_, regedit_path_, "CapabilityAccessManager2.txt")
        Tuple.getRegeditTuple["CapabilityAccessManager"] = Functions.get_regedit(hkey, regedit_path, "CapabilityAccessManager.txt")
        Tuple.getRegeditTuple["CapabilityAccessManager2"] = Functions.get_regedit(hkey_, regedit_path_, "CapabilityAccessManager2.txt")

    # def UserAssist(self):
    #     # GUID bakılacak
    #     hkey = winreg.HKEY_CURRENT_USER
    #     regedit_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist\{GUID}\Count"
    #     Functions.get_regedit(hkey, regedit_path, "UserAssist.txt")
    #     Tuple.getRegeditTuple["UserAssist"] = Functions.get_regedit(hkey, regedit_path, "UserAssist.txt")
    #     pass

class File_and_Folder_Opening:
    def OpenSaveMRU(self):
        hkey = winreg.HKEY_CURRENT_USER
        regedit_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSavePIDlMRU"
        Functions.get_regedit(hkey, regedit_path, "OpenSaveMRU.txt")
        Tuple.getRegeditTuple["OpenSaveMRU"] = Functions.get_regedit(hkey, regedit_path, "OpenSaveMRU.txt")

    def RecentFiles(self):
        hkey = winreg.HKEY_CURRENT_USER
        regedit_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs"
        Functions.get_regedit(hkey, regedit_path, "RecentFiles.txt")
        Tuple.getRegeditTuple["RecentFiles"] = Functions.get_regedit(hkey, regedit_path, "RecentFiles.txt")

    def MS_Word_Reading_Locations(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_path = r"Software\Microsoft\Office\<Version>\Word\Reading Locations"
        Functions.get_regedit(hkey, regedit_path, "MS_Word_Reading_Locations.txt")
        Tuple.getRegeditTuple["MS_Word_Reading_Locations"] = Functions.get_regedit(hkey, regedit_path, "MS_Word_Reading_Locations.txt")

    def Last_Visited_MRU(self):
        hkey = winreg.HKEY_CURRENT_USER
        regedit_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedPidlMRU"
        Functions.get_regedit(hkey, regedit_path, "Last_Visited_MRU.txt")
        Tuple.getRegeditTuple["Last_Visited_MRU"] = Functions.get_regedit(hkey, regedit_path, "Last_Visited_MRU.txt")

    def Shorcut_Files(self):
        pass

    def OfficeRecentFiles(self):
        hkey = winreg.HKEY_CURRENT_USER
        hkey_ = winreg.HKEY_CURRENT_USER
        hkey__ = winreg.HKEY_CURRENT_USER
        regedit_path = r"Software\Microsoft\Office\<Version>\<AppName>\File MRU"
        regedit_path_ = r"Software\Microsoft\Office\<Version>\<AppName>\User MRU\LiveId_####\File MRU"
        regedit_path__ = r"Software\Microsoft\Office\<Version>\<AppName>\User MRU\AD_####\File MRU"
        Functions.get_regedit(hkey, regedit_path, "OfficeRecentFiles.txt")
        Functions.get_regedit(hkey_, regedit_path_, "OfficeRecentFiles2.txt")
        Functions.get_regedit(hkey__, regedit_path__, "OfficeRecentFiles3.txt")
        Tuple.getRegeditTuple["OfficeRecentFiles"] = Functions.get_regedit(hkey, regedit_path, "OfficeRecentFiles.txt")
        Tuple.getRegeditTuple["OfficeRecentFiles2"] = Functions.get_regedit(hkey_, regedit_path_, "OfficeRecentFiles2.txt")
        Tuple.getRegeditTuple["OfficeRecentFiles3"] = Functions.get_regedit(hkey__, regedit_path__, "OfficeRecentFiles3.txt")

    def ShellBags(self):
        hkey = winreg.HKEY_CURRENT_USER
        hkey_ = winreg.HKEY_CURRENT_USER
        regedit_path = r"Software\Microsoft\Windows\Shell\BagMRU"
        regedit_path_ = r"Software\Microsoft\Windows\Shell\Bags"
        Functions.get_regedit(hkey, regedit_path, "ShellBags.txt")
        Functions.get_regedit(hkey_, regedit_path_, "ShellBags2.txt")
        Tuple.getRegeditTuple["ShellBags"] = Functions.get_regedit(hkey, regedit_path, "ShellBags.txt")
        Tuple.getRegeditTuple["ShellBags2"] = Functions.get_regedit(hkey_, regedit_path_, "ShellBags2.txt")

    def JumpLists(self):
        location = f"{os.environ.get('USERPROFILE')}"
        extract_location = os.path.join(location, "AppData", "Roaming", "Microsoft", "Windows", "Recent", "AutomaticDestinations")
        extract_location_ = os.path.join(location, "AppData", "Roaming", "Microsoft", "Windows", "Recent", "AutomaticDestinations")
        Functions.get_location(extract_location, "JumpLists.txt")
        Functions.get_location(extract_location_, "JumpLists2.txt")
        Tuple.getLocationTuple["JumpLists"] = Functions.get_location(extract_location, "JumpLists.txt")
        Tuple.getLocationTuple["JumpLists2"] = Functions.get_location(extract_location_, "JumpLists2.txt")

    def OfficeTrustRecords(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_path = r"Software\Microsoft\Office\<Version>\<AppName>\Security\Trusted Documents\TrustRecords"
        Functions.get_regedit(hkey, regedit_path, "OfficeTrustRecords.txt")
        Tuple.getRegeditTuple["OfficeTrustRecords"] = Functions.get_regedit(hkey, regedit_path, "OfficeTrustRecords.txt")

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
        Functions.get_location(location, "WindowsSearchDatabase.txt", 1)
        Functions.get_location(location_, "WindowsSearchDatabase2.txt", 1)
        Tuple.getLocationTuple["WindowsSearchDatabase"] = Functions.get_location(location, "WindowsSearchDatabase.txt", 1)
        Tuple.getLocationTuple["WindowsSearchDatabase2"] = Functions.get_location(location_, "WindowsSearchDatabase2.txt", 1)

    def InternetExplorerFile(self):
        pass

    def SearchWordWheelQuery(self):
        hkey = winreg.HKEY_CURRENT_USER
        regedit_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\WordWheelQuery"
        Functions.get_regedit(hkey, regedit_path, "SearchWordWheelQuery.txt")
        Tuple.getRegeditTuple["SearchWordWheelQuery"] = Functions.get_regedit(hkey, regedit_path, "SearchWordWheelQuery.txt")

    def UserTypedPaths(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths"
        Functions.get_regedit(hkey, regedit_path, "UserTypedPaths.txt")
        Tuple.getRegeditTuple["UserTypedPaths"] = Functions.get_regedit(hkey, regedit_path, "UserTypedPaths.txt")

    def Thumbcache(self):
        pass

    def RecycleBin(self):
        location = r"C:\$Recycle.Bin"
        Functions.get_location(location, "Recycle.txt", 1)
        Tuple.getLocationTuple["Recycle"] = Functions.get_location(location, "Recycle.txt", 1)

class Browser_Activity:
    def HistoryAndDownloadHistory(self):
        pass

    def MediaHistory(self):
        pass

    def HTML5WebStorage(self):
        pass

    def HTML5FileSystem(self):
        pass

    def AutoCompleteData(self):
        pass

    def Browser_Preferences(self):
        pass

    def Cache(self):
        pass

    def Bookmarks(self):
        pass

    def Stored_Credentials(self):
        pass

    def Browser_Downloads(self):
        pass

    def Extensions(self):
        pass

    def Session_Restore(self):
        pass

    def Cookies(self):
        pass

class CloudStorage:
    def OneDrive(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_path = r"Software\Microsoft\OneDrive\Accounts\<Personal | Business1>"
        Functions.get_regedit(hkey, regedit_path, "Onedrive.txt")
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
        Functions.get_location(extract_location, "Service_Events.txt", 1)
        Functions.get_location(extract_location_, "Service_Events.txt", 1)
        Tuple.getLocationTuple["Service_Events"] = Functions.get_location(extract_location, "Service_Events.txt", 1)
        Tuple.getLocationTuple["Service_Events2"] = Functions.get_location(extract_location_, "Service_Events.txt", 1)

    def User_Accounts(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList"
        Functions.get_regedit(hkey, regedit_key, "User_Accounts.txt")
        Tuple.getRegeditTuple["User_Accounts"] = Functions.get_regedit(hkey, regedit_key, "User_Accounts.txt")

    def RDP(self):
        location = os.environ.get('SYSTEMROOT')
        extract_location = os.path.join(location, "System32", "winevt", "logs", "Security.evtx")
        Functions.get_location(extract_location, "RDP.txt", 1)
        Tuple.getLocationTuple["RDP"] = Functions.get_location(extract_location, "RDP.txt", 1)

    def SuccessfulFailedLogons(self):
        location = os.environ.get('SYSTEMROOT')
        extract_location = os.path.join(location, "System32", "winevt", "logs", "Security.evtx")
        Functions.get_location(extract_location, "SuccessfulFailedLogons.txt", 1)
        Tuple.getLocationTuple["SuccessfulFailedLogons"] = Functions.get_location(extract_location, "SuccessfulFailedLogons.txt", 1)

    def Authentication_Events(self):
        location = os.environ.get('SYSTEMROOT')
        extract_location = os.path.join(location, "System32", "winevt", "logs", "Security.evtx")
        Functions.get_location(extract_location, "Authentication_Events.txt", 1)
        Tuple.getLocationTuple["Authentication_Events"] = Functions.get_location(extract_location, "Authentication_Events.txt", 1)

    def Logon_Event_Types(self):
        location = os.environ.get('SYSTEMROOT')
        extract_location = os.path.join(location, "System32", "winevt", "logs", "Security.evtx")
        Functions.get_location(extract_location, "Logon_Event_Types.txt", 1)
        Tuple.getLocationTuple["Logon_Event_Types"] = Functions.get_location(extract_location, "Logon_Event_Types.txt", 1)

class Network_Activity_and_Physical_Location:
    def Network_History(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
        regedit_key_ = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkCards"
        regedit_key__ = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\Signatures\Unmanaged"
        regedit_key___ = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\Signatures\Managed"
        regedit_key____ = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\Nla\Cache"
        regedit_key_____ = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\Profiles"
        Functions.get_regedit(hkey, regedit_key, "Network_History.txt")
        Functions.get_regedit(hkey, regedit_key_, "Network_History2.txt")
        Functions.get_regedit(hkey, regedit_key__, "Network_History3.txt")
        Functions.get_regedit(hkey, regedit_key___, "Network_History4.txt")
        Functions.get_regedit(hkey, regedit_key____, "Network_History5.txt")
        Functions.get_regedit(hkey, regedit_key_____, "Network_History6.txt")
        Tuple.getRegeditTuple["Network_History"] = Functions.get_regedit(hkey, regedit_key, "Network_History.txt")
        Tuple.getRegeditTuple["Network_History2"] = Functions.get_regedit(hkey, regedit_key_, "Network_History2.txt")
        Tuple.getRegeditTuple["Network_History3"] = Functions.get_regedit(hkey, regedit_key__, "Network_History3.txt")
        Tuple.getRegeditTuple["Network_History4"] = Functions.get_regedit(hkey, regedit_key___, "Network_History4.txt")
        Tuple.getRegeditTuple["Network_History5"] = Functions.get_regedit(hkey, regedit_key____, "Network_History5.txt")
        Tuple.getRegeditTuple["Network_History6"] = Functions.get_regedit(hkey, regedit_key_____, "Network_History6.txt")

    def Browser_URL_Parameters(self):
        pass

    def Timezone(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"SYSTEM\CurrentControlSet\Control\TimeZoneInformation"
        Functions.get_regedit(hkey, regedit_key, "Browser_URL_Parameters.txt")
        Tuple.getRegeditTuple["Browser_URL_Parameters"] = Functions.get_regedit(hkey, regedit_key, "Browser_URL_Parameters.txt")

    def WLAN_Evet_Log(self):
        pass

    def Network_Interfaces(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
        regedit_key_ = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkCards"
        Functions.get_regedit(hkey, regedit_key, "Timezone.txt")
        Functions.get_regedit(hkey, regedit_key_, "Timezone2.txt")
        Tuple.getRegeditTuple["Timezone"] = Functions.get_regedit(hkey, regedit_key, "Timezone.txt")
        Tuple.getRegeditTuple["Timezone2"] = Functions.get_regedit(hkey, regedit_key_, "Timezone2.txt")

    def SRUM(self):
        location = rf"{os.environ.get('SYSTEMROOT')}\System32\SRU"
        Functions.get_location(location, "SRUM.txt")
        Tuple.getLocationTuple["SRUM"] = Functions.get_location(location, "SRUM.txt")

class External_Device_USB_Usage:
    def USB_Device_Identification(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"SYSTEM\CurrentControlSet\Enum\USBSTOR"
        regedit_key_ = r"SYSTEM\CurrentControlSet\Enum\USB"
        regedit_key__ = r"SYSTEM\CurrentControlSet\Enum\SCSI"
        regedit_key___ = r"SYSTEM\CurrentControlSet\Enum\HID"
        Functions.get_regedit(hkey, regedit_key, "USB_Device_Identification.txt")
        Functions.get_regedit(hkey, regedit_key_, "USB_Device_Identification2.txt")
        Functions.get_regedit(hkey, regedit_key__, "USB_Device_Identification3.txt")
        Functions.get_regedit(hkey, regedit_key___, "USB_Device_Identification4.txt")
        Tuple.getRegeditTuple["USB_Device_Identification"] = Functions.get_regedit(hkey, regedit_key, "USB_Device_Identification.txt")
        Tuple.getRegeditTuple["USB_Device_Identification2"] = Functions.get_regedit(hkey, regedit_key_, "USB_Device_Identification2.txt")
        Tuple.getRegeditTuple["USB_Device_Identification3"] = Functions.get_regedit(hkey, regedit_key__, "USB_Device_Identification3.txt")
        Tuple.getRegeditTuple["USB_Device_Identification4"] = Functions.get_regedit(hkey, regedit_key___, "USB_Device_Identification4.txt")

    def Event_Logs(self):
        location = os.environ.get('SYSTEMROOT')
        extract_location = os.path.join(location, "System32", "winevt", "logs", "System.evtx")
        extract_location_ = os.path.join(location, "System32", "winevt", "logs", "Security.evtx")
        extract_location__ = os.path.join(location, "System32", "winevt", "logs", "Microsoft-Windows-Partition", "Diagnostic.evtx")
        Functions.get_location(extract_location, "Event_Logs.txt", 1)
        Functions.get_location(extract_location_, "Event_Logs2.txt", 1)
        Functions.get_location(extract_location__, "Event_Logs3.txt", 1)
        Tuple.getLocationTuple["Event_Logs"] = Functions.get_location(extract_location, "Event_Logs.txt", 1)
        Tuple.getLocationTuple["Event_Logs2"] = Functions.get_location(extract_location_, "Event_Logs2.txt", 1)
        Tuple.getLocationTuple["Event_Logs3"] = Functions.get_location(extract_location__, "Event_Logs3.txt", 1)

    def Drive_Letter_and_Volume_Name(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"SOFTWARE\Microsoft\Windows Portable Devices\Devices"
        regedit_key_ = r"SOFTWARE\Microsoft\Windows Search\VolumeInfoCache"
        Functions.get_regedit(hkey, regedit_key, "Event_Logs.txt")
        Functions.get_regedit(hkey, regedit_key_, "Event_Logs2.txt")
        Tuple.getRegeditTuple["Event_Logs"] = Functions.get_regedit(hkey, regedit_key, "Event_Logs.txt")
        Tuple.getRegeditTuple["Event_Logs2"] = Functions.get_regedit(hkey, regedit_key_, "Event_Logs2.txt")

    def User_Information(self):
        pass

    def ShortcutFiles(self):
        location = os.environ.get('USERPROFILE')
        extract_location = os.path.join(location, "AppData", "Roaming", "Microsoft", "Windows", "Recent")
        extract_location_ = os.path.join(location, "AppData", "Roaming", "Microsoft", "Office", "Recent")
        Functions.get_location(extract_location, "ShortcutFiles.txt", 1)
        Functions.get_location(extract_location_, "ShortcutFiles2.txt", 1)
        Tuple.getLocationTuple["ShortcutFiles"] = Functions.get_location(extract_location, "ShortcutFiles.txt", 1)
        Tuple.getLocationTuple["ShortcutFiles2"] = Functions.get_location(extract_location_, "ShortcutFiles2.txt", 1)

    def Connection_Timestamps(self):
        location = rf"{os.environ.get('SYSTEMROOT')}\inf"
        Functions.get_location(location, "Connection_Timestamps.txt")
        Tuple.getLocationTuple["Connection_Timestamps"] = Functions.get_location(location, "Connection_Timestamps.txt")

    def VSN(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"SOFTWARE\Microsoft\WindowsNT\CurrentVersion\EMDMgmt"
        Functions.get_regedit(hkey, regedit_key, "VSN.txt")
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
        Functions.get_regedit(hkey, regedit_key, "Operating_System_Version.txt")
        Functions.get_regedit(hkey, regedit_key_, "Operating_System_Version2.txt")
        Tuple.getRegeditTuple["Operating_System_Version"] = Functions.get_regedit(hkey, regedit_key, "Operating_System_Version.txt")
        Tuple.getRegeditTuple["Operating_System_Version2"] = Functions.get_regedit(hkey, regedit_key_, "Operating_System_Version2.txt")

    def ComputerName(self):
        Tuple.getLocationTuple["ComputerName"] = socket.gethostname()

    def System_Boot_Autostart_Programs(self):
        hkey = winreg.HKEY_LOCAL_MACHINE
        regedit_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
        regedit_key_ = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run"
        regedit_key__ = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        regedit_key___ = r"SYSTEM\CurrentControlSet\Services"
        Functions.get_regedit(hkey, regedit_key, "System_Boot_Autostart_Programs.txt")
        Functions.get_regedit(hkey, regedit_key_, "System_Boot_Autostart_Programs2.txt")
        Functions.get_regedit(hkey, regedit_key__, "System_Boot_Autostart_Programs3.txt")
        Functions.get_regedit(hkey, regedit_key___, "System_Boot_Autostart_Programs4.txt")
        Tuple.getRegeditTuple["System_Boot_Autostart_Programs"] = Functions.get_regedit(hkey, regedit_key, "System_Boot_Autostart_Programs.txt")
        Tuple.getRegeditTuple["System_Boot_Autostart_Programs2"] = Functions.get_regedit(hkey, regedit_key_, "System_Boot_Autostart_Programs2.txt")
        Tuple.getRegeditTuple["System_Boot_Autostart_Programs3"] = Functions.get_regedit(hkey, regedit_key__, "System_Boot_Autostart_Programs3.txt")
        Tuple.getRegeditTuple["System_Boot_Autostart_Programs4"] = Functions.get_regedit(hkey, regedit_key___, "System_Boot_Autostart_Programs4.txt")

    def System_Last_Shutdown_Time(self):
        hkey = winreg.HKEY_CURRENT_USER
        regedit_key = r"SYSTEM\CurrentControlSet\Control\Windows"
        regedit_key_ = r"SYSTEM\CurrentControlSet\Control\Watchdog\Display"
        Functions.get_regedit(hkey, regedit_key, "System_Last_Shutdown_Time.txt")
        Functions.get_regedit(hkey, regedit_key_, "System_Last_Shutdown_Time2.txt")
        Tuple.getRegeditTuple["System_Last_Shutdown_Time"] = Functions.get_regedit(hkey, regedit_key, "System_Last_Shutdown_Time.txt")
        Tuple.getRegeditTuple["System_Last_Shutdown_Time2"] = Functions.get_regedit(hkey, regedit_key_, "System_Last_Shutdown_Time2.txt")

class Start:
    def StartAll(self):
        application_Execution = Application_Execution()
        application_Execution.miniDump()
        application_Execution.crashDump()
        application_Execution.Shimcache()
        application_Execution.Task_Bar_Feature_Usage()
        application_Execution.Amache()
        application_Execution.Jump_Lists()
        application_Execution.Last_Visited_MRU()
        application_Execution.Commands_Executed_in_the_Run_Dialog()
        # application_Execution.Windows10_Timeline()
        # application_Execution.BAMDAM()
        application_Execution.SRUM()
        application_Execution.Prefetch()
        application_Execution.CapabilityAccessManager()
        # application_Execution.UserAssist()

        file_and_Folder_Opening = File_and_Folder_Opening()
        file_and_Folder_Opening.OpenSaveMRU()
        file_and_Folder_Opening.RecentFiles()
        file_and_Folder_Opening.MS_Word_Reading_Locations()
        file_and_Folder_Opening.Last_Visited_MRU()
        file_and_Folder_Opening.Shorcut_Files()
        file_and_Folder_Opening.OfficeRecentFiles()
        file_and_Folder_Opening.ShellBags()
        file_and_Folder_Opening.JumpLists()
        file_and_Folder_Opening.OfficeTrustRecords()
        file_and_Folder_Opening.OfficeOAlerts()
        file_and_Folder_Opening.InternetExplorerFile()

        deleted_Items_and_File_Existence = Deleted_Items_and_File_Existence()
        deleted_Items_and_File_Existence.ThumbsDB()
        deleted_Items_and_File_Existence.WindowsSearchDatabase()
        deleted_Items_and_File_Existence.InternetExplorerFile()
        deleted_Items_and_File_Existence.SearchWordWheelQuery()
        deleted_Items_and_File_Existence.UserTypedPaths()
        deleted_Items_and_File_Existence.Thumbcache()
        deleted_Items_and_File_Existence.RecycleBin()

        browser_activity = Browser_Activity()
        browser_activity.HistoryAndDownloadHistory()
        browser_activity.MediaHistory()
        browser_activity.HTML5WebStorage()
        browser_activity.HTML5FileSystem()
        browser_activity.AutoCompleteData()
        browser_activity.Browser_Preferences()
        browser_activity.Cache()
        browser_activity.Bookmarks()
        browser_activity.Stored_Credentials()
        browser_activity.Browser_Downloads()
        browser_activity.Extensions()
        browser_activity.Session_Restore()
        browser_activity.Cookies()

        cloudStorage = CloudStorage()
        cloudStorage.OneDrive()
        cloudStorage.Google_Drive_for_Desktop()
        cloudStorage.Box_Drive()
        cloudStorage.Dropbox()

        account_Usage = Account_Usage()
        account_Usage.Cloud_Account_Details()
        account_Usage.Last_Login_and_Password_Change()
        account_Usage.Service_Events()
        account_Usage.User_Accounts()
        account_Usage.RDP()
        account_Usage.SuccessfulFailedLogons()
        account_Usage.Authentication_Events()
        account_Usage.Logon_Event_Types()

        network_Activity_and_Physical_Location = Network_Activity_and_Physical_Location()
        network_Activity_and_Physical_Location.Network_History()
        network_Activity_and_Physical_Location.Browser_URL_Parameters()
        network_Activity_and_Physical_Location.Timezone()
        network_Activity_and_Physical_Location.WLAN_Evet_Log()
        network_Activity_and_Physical_Location.Network_Interfaces()
        network_Activity_and_Physical_Location.SRUM()

        external_Device_USB_Usage = External_Device_USB_Usage()
        external_Device_USB_Usage.USB_Device_Identification()
        external_Device_USB_Usage.Event_Logs()
        external_Device_USB_Usage.Drive_Letter_and_Volume_Name()
        external_Device_USB_Usage.User_Information()
        external_Device_USB_Usage.ShortcutFiles()
        external_Device_USB_Usage.Connection_Timestamps()
        external_Device_USB_Usage.VSN()

        systemInformation = SystemInformation()
        # systemInformation.Windows_Defender()
        systemInformation.Operating_System_Version()
        systemInformation.ComputerName()
        systemInformation.System_Boot_Autostart_Programs()
        systemInformation.System_Last_Shutdown_Time()
