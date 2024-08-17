## Oszust OS Music Tools - Oszust Industries
## Created on: 1-02-23 - Last update: 8-17-24
softwareVersion = "v1.4.2"
systemName, systemBuild = "Oszust OS Music Tools", "dev"
import AutoUpdater
try:
    filesVerified = True
    import bs4, cloudscraper, ctypes, datetime, eyed3, io, json, math, os, pathlib, platform, psutil, pyuac, random, re, requests, shutil, textwrap, threading, time, urllib.request, webbrowser, win32clipboard, yt_dlp
    from moviepy.editor import *
    from mutagen.mp3 import MP3
    from mutagen.wave import WAVE
    from PIL import Image
    from pytube import YouTube ## REMOVE
    import PySimpleGUI as sg
except Exception as Argument:
    filesVerified = False
    print(f"[ERROR]: Software files are missing. Please reinstall the software from GitHub and try again. Missing: {Argument}")

def softwareConfig():
    ## System Configuration
    global userSettingsData
    try: ## Try opening exisiting setting file
        with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Settings.json"), 'r') as file: userSettingsData = json.load(file)
        if userSettingsData["firstSoftwareUse"] != None: pass
    except: ## Create new file and assign default values
        print(f"[WARNING]: Failed to retrieve userSettingsData")
        userSettingsData = { ## Default Data
            "firstSoftwareUse": True, ## First use of Music Tools
            "musicSearchContract": False, ## Has the user accepted the Music Downloader contract
            "musicService": "Apple Music", ## User's preferred music service
            "billboardList": "hot 100", ## User's preferred music service
            "defaultDownloadLocation": str(pathlib.Path.home() / "Downloads"), ## User's preferred music service
        }
        with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Settings.json"), 'w') as file: json.dump(userSettingsData, file)
    print(f"[userSettingsData]: {userSettingsData}")

def softwareSetup():
    global appSelected, output, topSongsList, wifiStatus
    ## Setup Commands
    print("Loading...\nLaunching Interface...")
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0) ## Hides the console
    pathlib.Path(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache")).mkdir(parents=True, exist_ok=True) ## Create Cache folder in appdata
    pathlib.Path(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Playlists")).mkdir(parents=True, exist_ok=True) ## Create Playlists folder in appdata
    if systemBuild != "dev": ## Redirects the output to a txt file
        try: os.remove(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "outputLog.txt"))
        except: pass
        output = open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "outputLog.txt"), "wt")
        sys.stdout = output
        sys.stderr = output
    ## Get User's Configs
    print(f"[LOG START] {datetime.datetime.now().strftime("%Y-%m-%d | %H:%M:%S")}:\nSoftware: {systemName}\nBuild: {systemBuild}\nVersion: {softwareVersion}")
    softwareConfig()
    ## Check WIFI
    appSelected, wifiStatus = None, True
    checkInternetstatusThread = threading.Thread(name="checkInternetstatus", target=checkInternetstatus)
    checkInternetstatusThread.start()
    ## Billboard Top 100 Hits from Cache
    try:
        billboardCache, index, topSongsList = (open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Billboard.txt"), "r")).read().split("\n"), 1, []
        if datetime.datetime.strptime(billboardCache[0], '%Y-%m-%d') + datetime.timedelta(days=7) >= datetime.datetime.now(): ## Check if Cache is >= week
            if billboardCache[2][1] == ".":
                print(f"[WARNING]: Old Billboard format")
                loadingScreen("Billboard_List_Download", False) ## Old Billboard Data
            else:
                while index < len(billboardCache):
                    if index + 1 < len(billboardCache):
                        topSongsList.append([billboardCache[index].strip(), billboardCache[index + 1].strip()])
                        index += 2
                    else: break ## Get list from Cache
        else:
            print(f"[WARNING]: Outdated Billboard")
            loadingScreen("Billboard_List_Download", False) ## Download Billboard Data
    except:
        print(f"[WARNING]: Billboard file failed to load")
        loadingScreen("Billboard_List_Download", False) ## Download Billboard Data
    ## Retrieve Profanity Engine Definitions
    loadProfanityEngineDefinitions(False)
    ## AutoUpdater
    checkAutoUpdater("setup")

def crashMessage(message):
    RightClickMenu = ['', ['Copy']] ## Right Click Menu - Crash Message
    errorWindow = sg.Window(message.split(':')[0], [[sg.Text(systemName + " has crashed.", font=("Any", 13))], [sg.Multiline(message, size=(50,5), font=("Any", 13), disabled=True, autoscroll=False, right_click_menu=RightClickMenu, key='crashMessageErrorCodeText')], [sg.Button("Log File", button_color=("White", "Orange"), key='OpenLogFile'), sg.Button("Report Error", button_color=("White", "Blue"), key='Report'), sg.Button("Quit", button_color=("White", "Red"), key='Quit')]], resizable=False, finalize=True, keep_on_top=True, element_justification='c')
    errorLine:sg.Multiline = errorWindow['crashMessageErrorCodeText']
    print(f"[CRASH]: {message}")
    ## Window Shortcuts
    errorWindow.bind('<Insert>', '_Insert')  ## Report Error shortcut
    errorWindow.bind('<Delete>', '_Delete')  ## Close Window shortcut
    ## Mouse Icon Changes
    for key in ['Report', 'Quit']: errorWindow[key].Widget.config(cursor="hand2") ## Hover icons
    try: output.close()
    except: pass
    while True:
        event, values = errorWindow.read(timeout=10)
        if event == sg.WIN_CLOSED or event == 'Quit' or (event == '_Delete'):
            try: errorWindow.close()
            except: pass
            if systemBuild != "dev":
                thisSystem = psutil.Process(os.getpid()) ## Close Program
                thisSystem.terminate()
            return
        elif event == 'Report' or (event == '_Insert'): webbrowser.open("https://github.com/Oszust-Industries/" + systemName.replace(" ", "-") + "/issues/new", new=2, autoraise=True)
        elif event == 'OpenLogFile':
            try: os.startfile(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools"))
            except: pass
        elif event in RightClickMenu[1]: ## Right Click Menu Actions
            try:
                if event == 'Copy': ## Copy Error Text
                    try:
                        errorWindow.TKroot.clipboard_clear()
                        errorWindow.TKroot.clipboard_append(errorLine.Widget.selection_get())
                    except: pass
            except: pass

def checkInternetstatus():
    global wifiStatus
    while True:
        try:
            urllib.request.urlopen("http://google.com", timeout=3)
            wifiStatus = True
        except: wifiStatus = False
        time.sleep(10)

def downloadBillboardSongs():
    global loadingStatus, topSongsList
    ## Set Local Variables
    try: billboardList = userSettingsData["billboardList"]
    except: billboardList = "hot 100"
    try:
        import billboard
        chart, topSongsList = billboard.ChartData(billboardList.replace(" ", "-").lower(), fetch=True, max_retries=3, timeout=25), []
        for position, song in enumerate(chart):
            try:
                if billboardList == "Adult Contemporary" and position < 20:
                    if position < 8:
                        if song.weeks == 1: topSongsList.append([f"A{position + 1}. {song.title} - {song.artist}", "   NEW"])
                        elif song.lastPos > song.rank: topSongsList.append([f"A{position + 1}. {song.title} -  {song.artist}", str(song.weeks) + (f"     ^ {song.lastPos - position}" if song.weeks <= 9 else f"   ^ {song.lastPos - position}")])
                        elif song.lastPos == song.rank: topSongsList.append([f"A{position + 1}. {song.title} -  {song.artist}", str(song.weeks) + ("     ^" if song.weeks <= 9 else "   -") + (position - song.lastPos)])
                        elif song.lastPos < song.rank: topSongsList.append([f"A{position + 1}. {song.title} -  {song.artist}", str(song.weeks) + (f"     v {song.lastPos - position}" if song.weeks <= 9 else f"   v {song.lastPos - position}")])
                    elif position < 20:
                        if song.weeks == 1: topSongsList.append([f"B{position + 1}. {song.title} - {song.artist}", "   NEW"])
                        elif song.lastPos > song.rank: topSongsList.append([f"B{position + 1}. {song.title} -  {song.artist}", str(song.weeks) + (f"     ^ {song.lastPos - position}" if song.weeks <= 9 else f"   ^ {song.lastPos - position}")])
                        elif song.lastPos == song.rank: topSongsList.append([f"B{position + 1}. {song.title} -  {song.artist}", str(song.weeks) + ("     ^" if song.weeks <= 9 else "   -") + (position - song.lastPos)])
                        elif song.lastPos < song.rank: topSongsList.append([f"B{position + 1}. {song.title} -  {song.artist}", str(song.weeks) + (f"     v {song.lastPos - position}" if song.weeks <= 9 else f"   v {song.lastPos - position}")])
                else:
                    if song.weeks == 1: topSongsList.append([f"{position + 1}. {song.title} - {song.artist}", "   NEW"])
                    elif song.lastPos > song.rank: topSongsList.append([f"{position + 1}. {song.title} -  {song.artist}", str(song.weeks) + (f"     ^ {song.lastPos - position}" if song.weeks <= 9 else f"   ^ {song.lastPos - position}")])
                    elif song.lastPos == song.rank: topSongsList.append([f"{position + 1}. {song.title} -  {song.artist}", str(song.weeks) + ("     -" if song.weeks <= 9 else "   -")])
                    elif song.lastPos < song.rank: topSongsList.append([f"{position + 1}. {song.title} -  {song.artist}", str(song.weeks) + (f"     v {song.lastPos - position}" if song.weeks <= 9 else f"   v {song.lastPos - position}")])
            except: topSongsList.append([f"{position + 1}. Result Failed to Load.", "N/A"])
        try: ## Cache the List
            with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Billboard.txt"), "w") as billboardTextFile:  # Create Cache File
                lastTuesday = datetime.date.today() - datetime.timedelta(days=(datetime.date.today().weekday() - 1) % 7)  # Data is fresh on Tuesday
                billboardTextFile.write(str(lastTuesday))
                for sublist in topSongsList:
                    for item in sublist: billboardTextFile.write("\n" + item)
        except: pass
    except Exception as error:
        print(f"[WARNING]: Billboard failed to load. {error}")
        topSongsList = [["Billboard Failed to Load.", "N/A"]]
    loadingStatus = "Done"

def loadProfanityEngineDefinitions(downloadList):
    global profanityEngineDefinitions
    try:
        if downloadList:
            print(f"[INFO]: Refreshing Profanity Engine Definitions")
            profanityEngineDefinitions = []
            try:
                ## Read default Profanity Engine Definitions
                with open(os.path.join(pathlib.Path(__file__).resolve().parent, "data", "Default data", "profanityEngineDefaults.json"), 'r') as file: data = json.load(file)
                for category, value in data['categories'].items(): profanityEngineDefinitions.extend(value)
                ## Write Definitions to User save
                try:
                    with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Profanity Engine User Definitions.txt"), 'w') as file:
                        for item in profanityEngineDefinitions: file.write(item + '\n')
                except: pass
            except:
                print(f"[WARNING]: Failed to refresh Profanity Engine Definitions")
                profanityEngineDefinitions = "Failed"
        else:
            try:
                with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Profanity Engine User Definitions.txt"), 'r') as file: lines = file.readlines()
                profanityEngineDefinitions = [line.strip() for line in lines]
                if len(profanityEngineDefinitions) == 0: loadProfanityEngineDefinitions(True)
            except:
                print(f"[WARNING]: Failed to open Profanity Engine Definitions file")
                loadProfanityEngineDefinitions(True)
    except:
        print(f"[WARNING]: Profanity Engine Definitions failed to load")
        profanityEngineDefinitions = "Failed"

def checkAutoUpdater(command):
    try: AutoUpdaterDate = (open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "AutoUpdater Date.txt"), "r")).read().split("\n")
    except:
        print(f"[WARNING]: Missing AutoUpdater Date file")
        AutoUpdaterDate = [str(datetime.date.today() - datetime.timedelta(days=3)), "Missing File"]
    if (datetime.datetime.strptime(AutoUpdaterDate[0], '%Y-%m-%d') <= datetime.datetime.now() and systemBuild.lower() not in ["dev", "main"] and wifiStatus) or (command == "check" and wifiStatus) or (len(AutoUpdaterDate) == 2 and AutoUpdaterDate[1] == "Missing File" and wifiStatus):
        try: newestVersion = ((requests.get("https://api.github.com/repos/Oszust-Industries/" + systemName.replace(" ", "-") + "/releases/latest")).json())['tag_name']
        except: newestVersion = "Failed"
        if newestVersion != softwareVersion and newestVersion != "Failed":
            if not pyuac.isUserAdmin():
                try: releaseInfo = (json.loads(urllib.request.urlopen(f"https://api.github.com/repos/Oszust-Industries/" + systemName.replace(" ", "-") + "/releases?per_page=1").read().decode()))[0]['body'] ## Changelog File
                except: releaseInfo = "Failed"
                if "[AutoUpdater Code 0]" in releaseInfo: response = popupMessage("New Update Available", "A new version " + newestVersion + " is now available for " + systemName + ". AutoUpdater will not work for this update, so you must install it manually. Would you like to open the downloads page?", "downloaded")
                else: response = popupMessage("New Update Available", "A new version " + newestVersion + " is now available for " + systemName + ". Would you like to update now?", "downloaded")
                if response == True and "[AutoUpdater Code 0]" in releaseInfo: ## AutoUpdater is Blacklisted
                    webbrowser.open("https://github.com/Oszust-Industries/" + systemName.replace(" ", "-") + "/releases/latest", new=2, autoraise=True)
                    thisSystem = psutil.Process(os.getpid()) ## Close Program
                    thisSystem.terminate()
                    return 
                elif response == True: 
                    try:
                        try:
                            os.remove(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "AutoUpdater Date.txt"))
                            HomeWindow.close()
                        except: pass
                        pyuac.runAsAdmin()
                    except:
                        print(f"[ERROR]: AutoUpdater couldn't get admin")
                        if command == "check": popupMessage("AutoUpdater", "Failed to launch the software with administrator privileges.", "error")
                        else: homeScreen()
                else:
                    try: ## Cache the Next Date
                        with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "AutoUpdater Date.txt"), "w") as AutoUpdaterDateFile: ## Create Cache File
                            if response == "Week": AutoUpdaterDateFile.write(str(datetime.date.today() + datetime.timedelta(days=7)))
                            else: AutoUpdaterDateFile.write(str(datetime.date.today() + datetime.timedelta(days=1)))
                            AutoUpdaterDateFile.close()
                    except: pass
                    if command == "check": pass
                    else: homeScreen()
            else:
                AutoUpdater.main(systemName, systemBuild, softwareVersion, newestVersion, False)
        elif newestVersion == "Failed" and command == "check": ## GitHub Error
            print(f"[ERROR]: AutoUpdater couldn't get newestVersion: {newestVersion}")
            popupMessage("AutoUpdater", "There was an error while trying to fetch the latest version of  " + systemName + ".", "error")
            homeScreen()
        else: ## On Newest Version
            try: ## Cache the Next Date
                with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "AutoUpdater Date.txt"), "w") as AutoUpdaterDateFile: AutoUpdaterDateFile.write(str(datetime.date.today() + datetime.timedelta(days=1))) ## Create Cache File
            except: pass      
            if command == "check": popupMessage("AutoUpdater", "You are already using the latest version of " + systemName + ".", "success")
            else: homeScreen()
    else: homeScreen()
   
def homeScreenAppPanels(toolPanelApps, pinnedApps):
    ## Set Local Variables
    try: musicSub = userSettingsData["musicService"]
    except: musicSub = "Apple Music"
    try: billboardList = userSettingsData["billboardList"]
    except: billboardList = "hot 100"
    try: defaultDownloadLocation = userSettingsData["defaultDownloadLocation"]
    except: defaultDownloadLocation = str(pathlib.Path.home() / "Downloads")
    toolsPanel, toolPanelAppLocation, toolsPanelRow = [[]], 0, []
    for toolsPanelRowNumber in range(math.ceil(len(toolPanelApps)/6)):
        try:
            for app in range(toolPanelAppLocation, 6*(toolsPanelRowNumber+1)): toolsPanelRow.append(toolPanelApps[app])
        except: pass
        toolsPanel += [[sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\Tool icons\\' + app[0].lower() + app[1:].replace(" ", "") + '.png', border_width=0, button_color='#657076', key='musicTool_' + app.replace(" ", "_"), tooltip="Open " + app)]], background_color='#657076', pad=((10,10), (10, 10))) for app in toolsPanelRow]]
        toolsPanelRow = []
        toolPanelAppLocation += 6
    ## Listboxes
    topSongsListBoxed = [[sg.Table(values=topSongsList, headings=('Songs' + " " * int((-7 / 25) * ctypes.windll.shcore.GetScaleFactorForDevice(0) + 67), 'Weeks'), col_widths=[53, 8], num_rows=16, auto_size_columns=False, enable_events=True, background_color='white', text_color='black', justification='l', key='musicSearchPanel_billboardTopSongsList')]]
    profanityEngineListBoxed = [[sg.Listbox([item.replace("~", "'") for item in profanityEngineDefinitions], size=(25, 17), horizontal_scroll=True, select_mode=None, enable_events=True, right_click_menu=['&Right Click', ['&Delete']], highlight_background_color='blue', highlight_text_color='white', key='profanityEnginePanel_definitionsList')]]
    ## Music Search Panel [Default]
    return [[sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("Music Search:", font='Any 20 bold', justification='c', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Text("Search:", font='Any 16', background_color='#2B475D'), sg.Input(do_not_clear=True, size=(45,1), font='Any 11', enable_events=True, key='musicSearchPanel_songSearchInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\search.png', border_width=0, button_color='#2B475D', key='musicSearchPanel_normalSongSearchButton', tooltip="Search Music"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\listSearch.png', border_width=0, button_color='#2B475D', key='musicSearchPanel_listSongSearchButton', tooltip="Music Search - All Results"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clearInput.png', border_width=0, button_color='#2B475D', key='musicSearchPanel_clearSongSearchInputButton', tooltip="Clear Search")],
    [sg.Frame("The Billboard: " + billboardList, topSongsListBoxed, relief='flat', background_color='#2B475D', key='topSongsListFrame'), sg.Push(background_color='#2B475D')]], pad=((0,0), (0, 0)), background_color='#2B475D', visible=True, key='musicSearchPanel'),
    ## Music Downloader Panel
     sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\help.png', border_width=0, button_color='#2B475D', key='musicDownloaderPanel_helpButton'), sg.Push(background_color='#2B475D'), sg.Text("Music Downloader:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Text("", size=(5, 1), background_color='#2B475D')],
    [sg.Text("YouTube Link:", font='Any 13', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(48,1), enable_events=True, key='musicDownloaderPanel_youtubeUrlInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clipboard.png', border_width=0, button_color='#2B475D', key='musicDownloaderPanel_pasteClipboardButton', tooltip="Paste Link"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\openYoutube.png', border_width=0, button_color='#2B475D', key='musicDownloaderPanel_openYoutubeButton', tooltip="Open YouTube")],
    [sg.Text("Download Location:", font='Any 13', background_color='#2B475D'), sg.Input(defaultDownloadLocation, do_not_clear=True, size=(50,1), enable_events=True, key='musicDownloaderPanel_downloadLocationInput'), sg.FolderBrowse(initial_folder=defaultDownloadLocation, key='musicDownloaderPanel_fileBrowseButton')],
    [sg.HorizontalSeparator()], [sg.Push(background_color='#2B475D'), sg.Text("Downloader Settings:", font='Any 15', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\reset.png', border_width=0, button_color='#2B475D', key='musicDownloaderPanel_resetSettings', tooltip="Reset Settings")],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\true.png', border_width=0, button_color='#2B475D', key='musicDownloaderPanel_burnLyricsCheckbox'), sg.Text("Burn lyrics to the audio file", font='Any 14', background_color='#2B475D')],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\false.png', border_width=0, button_color='#2B475D', key='musicDownloaderPanel_compilationCheckbox'), sg.Text("Song's album is a compilation by various artists", font='Any 14', background_color='#2B475D')],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\false.png', border_width=0, button_color='#2B475D', key='musicDownloaderPanel_changeNameCheckbox'), sg.Text("Custom rename to:", font='Any 14', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(36,1), enable_events=True, visible=False, key='musicDownloaderPanel_changeNameInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clipboard_Small.png', border_width=0, button_color='#2B475D', visible=False, key='musicDownloaderPanel_changeNameClipboard', tooltip="Paste Link"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clearInput.png', border_width=0, button_color='#2B475D', visible=False, key='musicDownloaderPanel_changeNameClearInput', tooltip="Clear Input")],
    [sg.HorizontalSeparator()], [sg.Text("", font='Any 4', background_color='#2B475D')], [sg.Push(background_color='#2B475D'), sg.Button("Download", button_color=("White", "Blue"), font='Any 15', size=(10, 1), key='musicDownloaderPanel_downloadButton'), sg.Push(background_color='#2B475D')]], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='musicDownloaderPanel'),
    ## YouTube Downloader Panel
     sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("YouTube Downloader:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Text("YouTube Link:", font='Any 13', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(48,1), enable_events=True, key='youtubeDownloaderPanel_youtubeUrlInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clipboard.png', border_width=0, button_color='#2B475D', key='youtubeDownloaderPanel_pasteClipboardButton', tooltip="Paste Link"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\openYoutube.png', border_width=0, button_color='#2B475D', key='youtubeDownloaderPanel_openYoutubeButton', tooltip="Open YouTube")],
    [sg.Text("Download Location:", font='Any 13', background_color='#2B475D'), sg.Input(defaultDownloadLocation, do_not_clear=True, size=(50,1), enable_events=True, key='youtubeDownloaderPanel_downloadLocationInput'), sg.FolderBrowse(initial_folder=defaultDownloadLocation, key='youtubeDownloaderPanel_fileBrowseButton')],
    [sg.HorizontalSeparator()], [sg.Push(background_color='#2B475D'), sg.Text("Downloader Settings:", font='Any 15', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\reset.png', border_width=0, button_color='#2B475D', key='youtubeDownloaderPanel_resetSettings', tooltip="Reset Settings")],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\false.png', border_width=0, button_color='#2B475D', key='youtubeDownloaderPanel_audioDownloadCheckbox'), sg.Text("Download audio file (.MP3) of the YouTube Video", font='Any 14', background_color='#2B475D')],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\true.png', border_width=0, button_color='#2B475D', key='youtubeDownloaderPanel_videoDownloadCheckbox'), sg.Text("Download video file (.MP4) of the YouTube Video", font='Any 14', background_color='#2B475D')],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\false.png', border_width=0, button_color='#2B475D', key='youtubeDownloaderPanel_changeNameCheckbox'), sg.Text("Rename download to:", font='Any 14', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(33,1), enable_events=True, visible=False, key='youtubeDownloaderPanel_changeNameInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clipboard_Small.png', border_width=0, button_color='#2B475D', visible=False, key='youtubeDownloaderPanel_changeNameClipboard', tooltip="Paste Clipboard"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clearInput.png', border_width=0, button_color='#2B475D', visible=False, key='youtubeDownloaderPanel_changeNameClearInput', tooltip="Clear Input")],
    [sg.HorizontalSeparator()], [sg.Text("", font='Any 4', background_color='#2B475D')], [sg.Push(background_color='#2B475D'), sg.Button("Download", button_color=("White", "Blue"), font='Any 15', size=(10, 1), key='youtubeDownloaderPanel_downloadButton'), sg.Push(background_color='#2B475D')]], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='youtubeDownloaderPanel'),
    ## Metadata Burner Panel
    sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("Metadata Burner:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("Song Location:", font='Any 13', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(50,1), enable_events=True, key='metadataBurnerPanel_songLocationInput'), sg.FileBrowse(file_types=(("Music Files", "*.mp3;*.wav;"), ("All Files", "*.*")), initial_folder=defaultDownloadLocation, key='metadataBurnerPanel_songLocationBrowser'), sg.Push(background_color='#2B475D')],
    [sg.HorizontalSeparator()], [sg.Text("Song Name:", font='Any 13', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(61,1), enable_events=True, key='metadataBurnerPanel_songNameInput')],
    [sg.Text("Artist:", font='Any 13', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(68,1), enable_events=True, key='metadataBurnerPanel_songArtistInput')],
    [sg.Text("Album:", font='Any 13', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(67,1), enable_events=True, key='metadataBurnerPanel_songAlbumInput')],
    [sg.Text("Year:", font='Any 13', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(16,1), enable_events=True, key='metadataBurnerPanel_songYearInput'), sg.Push(background_color='#2B475D'), sg.Text("Genre:", font='Any 13', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(20,1), enable_events=True, key='metadataBurnerPanel_songGenreInput')],
    [sg.Push(background_color='#2B475D'), sg.Text("Track Number:", font='Any 13', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(6,1), enable_events=True, key='metadataBurnerPanel_albumCurrentLengthInput'), sg.Text("/", font='Any 13', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(6,1), enable_events=True, key='metadataBurnerPanel_albumTotalLengthInput'), sg.Push(background_color='#2B475D'), sg.Text("CD Number:", font='Any 13', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(6,1), enable_events=True, key='metadataBurnerPanel_cdCurrentLengthInput'), sg.Text("/", font='Any 13', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(6,1), enable_events=True, key='metadataBurnerPanel_cdTotalLengthInput'), sg.Push(background_color='#2B475D')],
    [sg.Text("Publisher:", font='Any 13', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(64,1), enable_events=True, key='metadataBurnerPanel_songPublisherInput')],
    [sg.Text("Album Artwork:", font='Any 13', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(50,1), enable_events=True, key='metadataBurnerPanel_songArtworkInput'), sg.FileBrowse(file_types = (("Image Files", "*.png;*.jpg"), ("All Files", "*.*")), key='metadataBurnerPanel_songArtworkBrowser')],
    [sg.HorizontalSeparator()], [sg.Push(background_color='#2B475D'), sg.Text("Options:", font='Any 13', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\false.png', border_width=0, button_color='#2B475D', key='metadataBurnerPanel_onlyLyricsCheckbox'), sg.Text("Burn only lyrics", font='Any 14', background_color='#2B475D')],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\false.png', border_width=0, button_color='#2B475D', key='metadataBurnerPanel_multipleArtistsCheckbox'), sg.Text("Album includes multiple artists?", font='Any 14', background_color='#2B475D')],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\true.png', border_width=0, button_color='#2B475D', key='metadataBurnerPanel_renameFileCheckbox'), sg.Text("Change file name to song title", font='Any 14', background_color='#2B475D')],
    [sg.HorizontalSeparator()], [sg.Push(background_color='#2B475D'), sg.Text("Lyrics:", font='Any 13', background_color='#2B475D'), sg.Push(background_color='#2B475D')], [sg.Push(background_color='#2B475D'), sg.Multiline("", size=(65,18), font='Any 11', autoscroll=False, disabled=False, key='metadataBurnerPanel_lyricsInput'), sg.Push(background_color='#2B475D')]
    ], scrollable=True, vertical_scroll_only=True, size=(565, 280), background_color='#2B475D')], [sg.HorizontalSeparator()], [sg.Push(background_color='#2B475D'), sg.Button("Burn Metadata", button_color=("White", "Blue"), font='Any 15', size=(15, 1), key='metadataBurnerPanel_burnButton'), sg.Push(background_color='#2B475D')]], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='metadataBurnerPanel'),
    ## CD Burner Panel
    sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("CD Burner:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Listbox(values=[], size=(80, 12), key='cdburnerPanel_songsListbox', enable_events=True)],
    [sg.Input("", do_not_clear=True, size=(55,1), enable_events=True, key='cdburnerPanel_songInput'), sg.FileBrowse(file_types=(("Music Files", "*.mp3;*.wav;"), ("All Files", "*.*")), initial_folder=defaultDownloadLocation, key='cdburnerPanel_fileBrowseButton'),
     sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\newItem.png', border_width=0, button_color='#2B475D', key="cdburnerPanel_addSongButton", tooltip="Add Song"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\trash.png', border_width=0, button_color='#2B475D', key="cdburnerPanel_removeSongButton", tooltip="Remove Song"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clear-small.png', border_width=0, button_color='#2B475D', key="cdburnerPanel_clearSongsButton", tooltip="Clear CD List")],
    [sg.HorizontalSeparator()], [sg.Push(background_color='#2B475D'), sg.Text("Space: (0.0 / 650) MB", font='Any 13', background_color='#2B475D', key='cdburnerPanel_cdSizeText'), sg.Push(background_color='#2B475D')],
    [sg.Push(background_color='#2B475D'), sg.Button("Burn CD", button_color=("White", "Blue"), font='Any 15', size=(8, 1), key='cdburnerPanel_burnButton'), sg.Push(background_color='#2B475D')]
    ], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='cdburnerPanel'),
    ## CD Ripper Panel
    sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("CD Ripper:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Listbox(values=[], size=(80, 11), key='cdripperPanel_songsListbox', enable_events=True)],
    [sg.Text("CD Reader:", font='Any 13', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(52,1), enable_events=True, key='cdripperPanel_cdInput'), sg.FolderBrowse(key='cdripperPanel_importBrowseButton')],
    [sg.Text("Export Location:", font='Any 13', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(52,1), enable_events=True, key='cdripperPanel_exportInput'), sg.FolderBrowse(initial_folder=defaultDownloadLocation, key='cdripperPanel_exportBrowseButton')],
    [sg.HorizontalSeparator()], [sg.Push(background_color='#2B475D'), sg.Text("Space Required: 0.0 MB", font='Any 13', background_color='#2B475D', key='cdripperPanel_sizeText'), sg.Push(background_color='#2B475D')],
    [sg.Push(background_color='#2B475D'), sg.Button("Rip CD", button_color=("White", "Blue"), font='Any 15', size=(8, 1), key='cdripperPanel_ripButton'), sg.Push(background_color='#2B475D')]
    ], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='cdripperPanel'),
    ## Music Player Panel
    sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("Music Player:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\addSong.png', border_width=0, button_color='#2B475D', key='musicPlayerPanel_addSongButtonPlayer', visible=False), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\search.png', border_width=0, button_color='#2B475D', key='musicPlayerPanel_searchButtonPlayer', visible=True)], [sg.Text("", font='Any 18', background_color='#2B475D', visible=False)], [sg.Text("", font='Any 16', background_color='#2B475D')], [sg.Text("Not Playing", font='Any 14 bold', background_color='#2B475D', key='musicPlayerPanel_songTitle')], [sg.Text("Artist", font='Any 12', background_color='#2B475D', key='musicPlayerPanel_songArtist')], [sg.Text("Album", font='Any 12', background_color='#2B475D', key='musicPlayerPanel_songAlbum')],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\rewind.png', border_width=0, button_color='#2B475D', key='musicPlayerPanel_rewindButton'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\play.png', border_width=0, button_color='#2B475D', key='musicPlayerPanel_playButton'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\forward.png', border_width=0, button_color='#2B475D', key='musicPlayerPanel_forwardButton')], [sg.Text("", background_color='#2B475D', size=(43, 1))], [sg.Text("", font='Any 24', background_color='#2B475D')]], background_color='#2B475D', element_justification='c', visible=True, key='musicPlayerPanel_playerPanel'),
    sg.Column([[sg.Text("Not Playing - Artist", font='Any 11', background_color='#2B475D', key='musicPlayerPanel_songTitleLyrics')], [sg.Listbox([], size=(48,14), font='Any 10', disabled=True, key='musicPlayerPanel_lyricsListbox')], [sg.Text("", background_color='#2B475D', size=(43, 1))]], background_color='#2B475D', element_justification='c', visible=False, key='musicPlayerPanel_lyricsPanel'),
    sg.Column([[sg.Text("Not Playing - Artist", font='Any 11', background_color='#2B475D', key='musicPlayerPanel_songTitleQueue')], [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\addSong.png', border_width=0, button_color='#2B475D', key='musicPlayerPanel_addSongButton'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\upList.png', border_width=0, button_color='#2B475D', key='musicPlayerPanel_upQueueButton'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\downList.png', border_width=0, button_color='#2B475D', key='musicPlayerPanel_downQueueButton'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\trash.png', border_width=0, button_color='#2B475D', key='musicPlayerPanel_trashQueueButton')], [sg.Text("", font='Any 1', background_color='#2B475D')], [sg.Listbox([], size=(48,11), font='Any 10', disabled=False, right_click_menu=['&Right Click', ['&Play Next', '&Delete']], key='musicPlayerPanel_queueListbox')], [sg.Text("", background_color='#2B475D', size=(43, 1))]], background_color='#2B475D', element_justification='c', visible=False, key='musicPlayerPanel_queuePanel'),
    sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\shuffle.png', border_width=0, button_color='#2B475D', key='musicPlayerPanel_shuffleQueue'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\loop.png', border_width=0, button_color='#2B475D', key='musicPlayerPanel_loopQueue'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\lyrics.png', border_width=0, button_color='#2B475D', key='musicPlayerPanel_lyricsPage'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\queue.png', border_width=0, button_color='#2B475D', key='musicPlayerPanel_queuePage')],
    [sg.Image(str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\defaultMusicPlayerArtwork.png', size=(200,200), key='musicPlayerPanel_songArtwork')]], background_color='#2B475D', element_justification='c', key='musicPlayerPanel_artworkPanel')],
    [sg.Text("0:00", font='Any 12', background_color='#2B475D', key='musicPlayerPanel_startTime'), sg.Slider(range=(0, 240), default_value=0, expand_x=True, enable_events=True, disable_number_display=True, orientation='horizontal', key='musicPlayerPanel_timeSlider', background_color='#2B475D'), sg.Text("0:00", font='Any 12', background_color='#2B475D', key='musicPlayerPanel_endTime')]
    ], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='musicPlayerPanel'),
    ## Lyrics Guesser Panel
    sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("Lyrics Guesser Game:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')]
    ], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='lyricsGuesserPanel'),
    ## Music Editor Panel
    sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("Music Editor:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')]
    ], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='musicEditorPanel'),
    ## Playlist Maker Panel
    sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("Playlist Maker:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Listbox(values=sorted([os.path.splitext(f)[0] for f in os.listdir(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Playlists")) if os.path.isfile(os.path.join(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Playlists"), f))]), size=(62, 15), font='Any 12', key='playlistMakerPanel_playlistListbox', enable_events=True)],
    [sg.Input("", do_not_clear=True, size=(51,1), enable_events=True, key='playlistMakerPanel_playlistInput'), sg.Push(background_color='#2B475D'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\openView-small.png', border_width=0, button_color='#2B475D', key="playlistMakerPanel_openPlaylistButton", tooltip="Open Playlist"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\newItem.png', border_width=0, button_color='#2B475D', key="playlistMakerPanel_addPlaylistButton", tooltip="Add Playlist"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\trash.png', border_width=0, button_color='#2B475D', key="playlistMakerPanel_removePlaylistButton", tooltip="Remove Playlist"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\import-small.png', border_width=0, button_color='#2B475D', key="playlistMakerPanel_importPlaylistButton", tooltip="Import Playlist"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\share.png', border_width=0, button_color='#2B475D', key="playlistMakerPanel_exportPlaylistButton", tooltip="Export Playlist")]
    ], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='playlistMakerPanel'),
    ## Radio Show Maker Panel
    sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("Radio Show Maker:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')]
    ], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='radioShowMakerPanel'),
    ## Extra Apps Panel
    sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\sidebar.png', border_width=0, button_color='#2B475D', key='musicToolsPanel_moveSidebarButton'), sg.Push(background_color='#2B475D'), sg.Text("All Music Tools:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Text("", size=(5, 1), background_color='#2B475D')],
    [sg.Column(toolsPanel, size=(595,390), pad=((10,10), (10, 10)), background_color='#2B475D')]], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='musicToolsPanel'),
    ## Reorder Tools Panel
    sg.Column([[sg.Frame("All Music Tools", [[sg.Listbox(values=toolPanelApps, size=(28, 20), key='desktopMoverPanel_allListbox', enable_events=True),
    sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\pin.png', border_width=0, button_color='#2B475D', key='desktopMoverPanel_pinButton', tooltip="Pin App")],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\up.png', border_width=0, button_color='#2B475D', key='desktopMoverPanel_allUpButton', tooltip="Move App Up")],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\down.png', border_width=0, button_color='#2B475D', key='desktopMoverPanel_allDownButton', tooltip="Move App Down")],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\resetList.png', border_width=0, button_color='#2B475D', key='desktopMoverPanel_allResetButton', tooltip="Reset Tool Apps")]], vertical_alignment='center', background_color='#2B475D')]], relief='flat', title_location='nw', background_color='#2B475D'),
    sg.Frame("Pinned Tools", [[sg.Listbox(values=pinnedApps, size=(28, 20), key='desktopMoverPanel_pinnedListbox', enable_events=True),
    sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\unpin.png', border_width=0, button_color='#2B475D', key='desktopMoverPanel_unpinButton', tooltip="Unpin App")],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\up.png', border_width=0, button_color='#2B475D', key='desktopMoverPanel_pinnedUpButton', tooltip="Move App Up")],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\down.png', border_width=0, button_color='#2B475D', key='desktopMoverPanel_pinnedDownButton', tooltip="Move App Down")],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\resetList.png', border_width=0, button_color='#2B475D', key='desktopMoverPanel_pinnedResetButton', tooltip="Reset Pinned Apps")]
    ], vertical_alignment='center', background_color='#2B475D')]], relief='flat', title_location='nw', background_color='#2B475D'), ]], pad=((0, 0), (0, 0)), background_color='#2B475D', visible=False, key='desktopMoverPanel'),
    ## Settings Panel
    sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("Settings:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Frame("User Preferences", [[sg.Push(background_color='#2B475D'), sg.Text("Music Service:", background_color='#2B475D'), sg.Combo(('Apple Music', 'Spotify'), readonly=True, default_value=musicSub, key='settingsPanel_musicServiceCombo'), sg.Text("Billboard List:", background_color='#2B475D'), sg.Combo(("Hot 100", "Billboard 200", "Global", "Streaming Songs", "Radio Songs", "Adult Contemporary", "Digital Song Sales", "Pop Songs", "Country Songs", "Rock Songs", "Rap Songs", "Latin Songs", "Christian Songs", "Gospel Songs", "Jazz Songs", "Soundtracks"), readonly=True, default_value=billboardList, key='settingsPanel_billboardListCombo'), sg.Push(background_color='#2B475D')], [sg.Push(background_color='#2B475D'), sg.Text("Default Download Location:", background_color='#2B475D'), sg.Input(defaultDownloadLocation, do_not_clear=True, size=(30,1), enable_events=True, key='settingsPanel_defaultDownloadLocationInput'), sg.FolderBrowse(initial_folder=defaultDownloadLocation, key='settingsPanel_defaultDownloadLocationBrowser'), sg.Push(background_color='#2B475D')]], size=(580, 80), background_color='#2B475D')],
    [sg.Frame("Cache Management", [[sg.Push(background_color='#2B475D'), sg.Text(str(round(sum(os.path.getsize(os.path.join(dp, f)) for dp, _, filenames in os.walk(str(os.getenv('APPDATA')) + "\\Oszust Industries\\Oszust OS Music Tools\\Cache\\") for f in filenames) / (1024 * 1024), 2)) + " MB", background_color='#2B475D', key='settingsPanel_cacheStorageText'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clean.png', border_width=0, button_color='#2B475D', key='settingsPanel_cleanCacheButton', tooltip="Clean Cache Storage"), sg.Push(background_color='#2B475D')]], size=(580, 60), background_color='#2B475D')],
    [sg.Push(background_color='#2B475D'), sg.Button("Save Settings", button_color='#2B475D', key='settingsPanel_saveButton'), sg.Push(background_color='#2B475D')]
    ], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='settingsPanel'),
    ## Lyrics Checker Panel
     sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("Lyrics Checker:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Push(background_color='#2B475D'), sg.Multiline("", size=(63,18), font='Any 11', autoscroll=False, disabled=False, right_click_menu=['', ['Copy', 'Lookup Definition', 'Add to Profanity Engine', 'Remove from Profanity Engine']], key='lyricsCheckerPanel_lyricsInput'), sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\openWeb.png', border_width=0, button_color='#2B475D', key='lyricsCheckerPanel_openWebButton')], [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clipboard_Small.png', border_width=0, button_color='#2B475D', key='lyricsCheckerPanel_pasteClipboardButton')], [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clearInput.png', border_width=0, button_color='#2B475D', key='lyricsCheckerPanel_clearInputButton')], [sg.Text("", font='Any 14', background_color='#2B475D')], [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\checkInput.png', border_width=0, button_color='#2B475D', key='lyricsCheckerPanel_checkLyricsButton')]], vertical_alignment='b', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Push(background_color='#2B475D'), sg.Text("Profanity Engine: Not checked yet", font='Any 11', background_color='#2B475D', key='lyricsCheckerPanel_songUsableText'), sg.Push(background_color='#2B475D')]], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='lyricsCheckerPanel'),
    ## Profanity Engine Editor Panel
    sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("Profanity Engine:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Frame("Profanity Engine Definitions", profanityEngineListBoxed, relief='flat', title_location='n', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Column([[
     sg.Frame("Editor Commands", [[sg.Push(background_color='#2B475D'), sg.Text("Search:", background_color='#2B475D'), sg.InputText(size=(28,1), font='Any 11', enable_events=True, key="profanityEnginePanel_searchInput"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clearInput.png', border_width=0, button_color='#2B475D', key='profanityEnginePanel_searchClearInput', tooltip="Clear Search"), sg.Push(background_color='#2B475D')], [sg.Push(background_color='#2B475D'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\sort.png', border_width=0, button_color='#2B475D', key='profanityEnginePanel_sortButton', tooltip="Sort List (A-Z)"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\import.png', border_width=0, button_color='#2B475D', key='profanityEnginePanel_importButton', tooltip="Import New Definitions"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\download.png', border_width=0, button_color='#2B475D', key='profanityEnginePanel_exportButton', tooltip="Export Your List"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clear.png', border_width=0, button_color='#2B475D', key='profanityEnginePanel_clearButton', tooltip="Clear Entire List"), sg.Push(background_color='#2B475D')]], size=(350, 100), background_color='#2B475D')],
    [sg.Frame("Add Predefined Categories", [[sg.Push(background_color='#2B475D'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\swear.png', border_width=0, button_color='#2B475D', key='profanityEnginePanel_swearPredefinedWords', tooltip="Add Predefined Swear Language"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\drinking.png', border_width=0, button_color='#2B475D', key='profanityEnginePanel_alcoholPredefinedWords', tooltip="Add Predefined Drinking Language"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\drugs.png', border_width=0, button_color='#2B475D', key='profanityEnginePanel_drugsVapePredefinedWords', tooltip="Add Predefined Drugs & Vape Language"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\sex.png', border_width=0, button_color='#2B475D', key='profanityEnginePanel_sexPredefinedWords', tooltip="Add Predefined Sexual Language"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\other.png', border_width=0, button_color='#2B475D', key='profanityEnginePanel_otherPredefinedWords', tooltip="Add Other Predefined Language"), sg.Push(background_color='#2B475D')]], size=(350, 80), background_color='#2B475D')],
    [sg.Frame("Add / Edit Words", [[sg.Push(background_color='#2B475D'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\save.png', border_width=0, button_color='#2B475D', key="profanityEnginePanel_saveEditButton", tooltip="Save Word to List"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\trash.png', border_width=0, button_color='#2B475D', key="profanityEnginePanel_deleteWordButton", tooltip="Remove Word from List"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\newItem.png', border_width=0, button_color='#2B475D', key="profanityEnginePanel_newWordButton", tooltip="Create New Word for List")], [sg.Push(background_color='#2B475D'), sg.InputText(size=(40,8), font='Any 11', key="profanityEnginePanel_wordEditorInput"), sg.Push(background_color='#2B475D')]], size=(350, 100), background_color='#2B475D')]], background_color='#2B475D'),
    ]], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='profanityEnginePanel'),
    ]]

def homeScreen():
    global appSelected, HomeWindow, homeWindowLocationX, homeWindowLocationY, musicSearchResultData, profanityEngineDefinitions
    try: billboardList = userSettingsData["billboardList"]
    except: billboardList = "hot 100"
    try: defaultDownloadLocation = userSettingsData["defaultDownloadLocation"]
    except: defaultDownloadLocation = str(pathlib.Path.home() / "Downloads")
    ## Import PyGame
    try: from pygame import mixer
    except:
        print(f"[ERROR]: Software files are missing. Please reinstall the software from GitHub and try again. Missing: pygame")
        crashMessage("Missing the pygame package.")
    applist, defaultToolPanelApps, defaultPinnedApps, onlineApps = [[]], ["Music Search", "Music Downloader", "Youtube Downloader", "Metadata Burner", "Music Player", "Lyrics Checker", "Profanity Engine", "Settings"], ["Music Search", "Music Downloader", "Youtube Downloader", "Metadata Burner", "Music Tools", "Settings"], ["Music Search", "Music Downloader", "Youtube Downloader"]
    #if systemBuild == "dev":
    #    for app in ["Playlist Maker", "Radio Show Maker", "CD Ripper", "CD Burner", "Music Player", "Music Editor", "Lyrics Guesser"]: defaultToolPanelApps.append(app)
    try: ## All Music Tools
        with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "toolLayout.json"), 'r') as file:
            toolLayoutData = (json.load(file))
            toolPanelApps, pinnedApps = toolLayoutData["toolPanelApps"].copy(), toolLayoutData["pinnedApps"].copy()
    except:
        toolLayoutData = {"toolPanelApps": defaultToolPanelApps, "pinnedApps": defaultPinnedApps}
        toolPanelApps, pinnedApps = toolLayoutData["toolPanelApps"].copy(), toolLayoutData["pinnedApps"].copy()
    for app in defaultToolPanelApps: ## Add apps not in user's save
        if app not in toolPanelApps: toolPanelApps.append(app)
    if wifiStatus: 
        for app in onlineApps:
            if app not in toolPanelApps: toolPanelApps.append(app)
    else:
        for app in onlineApps: ## Remove apps that need internet
            if app in toolPanelApps: toolPanelApps.remove(app)
            if app in pinnedApps: pinnedApps.remove(app)
    for app in pinnedApps: applist += [[sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent) + "\\data\\App icons\\" + app.lower().replace(" ", "") + ".png", button_color='#657076', border_width=0, key=app.replace(" ", "_") + '_AppSelector', tooltip='Open ' + app)]], pad=((5,5), (5, 5)), background_color='#657076')]] ## Add Apps to Side Panel
    ## Home Window
    layout = [[sg.Column(applist, size=(72,390), pad=((10,10), (10, 10)), background_color='#2B475D', scrollable=False, vertical_scroll_only=True), sg.Column(homeScreenAppPanels(toolPanelApps, pinnedApps), size=(595,390), pad=((10,10), (10, 10)), background_color='#2B475D', scrollable=False, vertical_scroll_only=True)]]
    if wifiStatus: layout += [[sg.Column([[sg.Text(f"{platform.system()} | {softwareVersion} | {systemBuild} | Online", enable_events=True, font='Any 13', background_color='#5A6E80', key='versionTextHomeBottom', tooltip="View Changelog and Check Updates"), sg.Push(background_color='#5A6E80'), sg.Text("Oszust Industries", enable_events=True, font='Any 13', background_color='#5A6E80', key='creditsTextHomeBottom')], [sg.Column([[]], size=(710, 1), pad=(0,0))]], size=(710, 30), pad=(0,0), background_color='#5A6E80')]]
    else: layout += [[sg.Column([[sg.Text(f"{platform.system()} | {softwareVersion} | {systemBuild} | Offline", enable_events=True, font='Any 13', background_color='#5A6E80', key='versionTextHomeBottom'), sg.Push(background_color='#5A6E80'), sg.Text("Oszust Industries", enable_events=True, font='Any 13', background_color='#5A6E80', key='creditsTextHomeBottom')], [sg.Column([[]], size=(710, 1), pad=(0,0))]], size=(710, 30), pad=(0,0), background_color='#5A6E80')]]
    windowSize = ((int((-4*(ctypes.windll.shcore.GetScaleFactorForDevice(0))+1060) * (ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100)), int((-4*(ctypes.windll.shcore.GetScaleFactorForDevice(0))+800) * (ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100))))
    HomeWindow = sg.Window('Oszust OS Music Tools', layout, size=windowSize, background_color='#657076', margins=(0,0), finalize=True, resizable=False, text_justification='r')
    HomeWindow.hide()
    HomeWindow.TKroot.minsize(710, 440)
    ## Music Search: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    HomeWindow['musicSearchPanel_billboardTopSongsList'].bind('<Return>', '_Enter')  ## Enter on Top 100 list
    HomeWindow['musicSearchPanel_billboardTopSongsList'].bind('<Insert>', '_Ins')    ## Insert on Top 100 list
    HomeWindow['musicSearchPanel_songSearchInput'].bind('<Return>', '_Enter')        ## Enter on Song Search
    HomeWindow['musicSearchPanel_songSearchInput'].bind('<Insert>', '_Ins')          ## Insert on Song Search
    HomeWindow['musicSearchPanel_songSearchInput'].bind('<Delete>', '_Del')          ## Delete on Song Search
    for key in ['normalSongSearchButton', 'listSongSearchButton', 'clearSongSearchInputButton', 'billboardTopSongsList']: HomeWindow['musicSearchPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## Settings: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    for key in ['musicServiceCombo', 'billboardListCombo', 'defaultDownloadLocationBrowser', 'saveButton']: HomeWindow['settingsPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## Music Downloader: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    HomeWindow['musicDownloaderPanel_youtubeUrlInput'].bind('<Return>', '_Enter')  ## Enter on Link Input
    musicBurnLyrics, musicCompilationAlbum, musicDownloadName = True, False, False ## App Variables
    for key in ['pasteClipboardButton', 'openYoutubeButton', 'fileBrowseButton', 'resetSettings', 'burnLyricsCheckbox', 'compilationCheckbox', 'changeNameCheckbox', 'changeNameClipboard', 'changeNameClearInput', 'downloadButton']: HomeWindow['musicDownloaderPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## YouTube Downloader: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    HomeWindow['youtubeDownloaderPanel_youtubeUrlInput'].bind('<Return>', '_Enter')  ## Enter on Link Input
    youtubeAudioDownload, youtubeVideoDownload, youtubeDownloadName = False, True, False ## App Variables
    for key in ['pasteClipboardButton', 'openYoutubeButton', 'fileBrowseButton', 'resetSettings', 'audioDownloadCheckbox', 'videoDownloadCheckbox', 'changeNameCheckbox', 'changeNameClipboard', 'changeNameClearInput', 'downloadButton']: HomeWindow['youtubeDownloaderPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## Music Player: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    musicPlayerCurrentSong, musicPlayerQueueCurrentState, musicPlayerQueueCurrentIndex, musicPlayerLoop, musicPlayerPage, musicPlayerShuffle, musicPlayerQueue = "", "pause", 0, False, "player", False, []
    for key in ['searchButtonPlayer', 'rewindButton', 'playButton', 'forwardButton', 'shuffleQueue', 'loopQueue', 'lyricsPage', 'queuePage', 'addSongButton', 'upQueueButton', 'downQueueButton', 'trashQueueButton']: HomeWindow['musicPlayerPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## Lyrics Checker: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    HomeWindow['lyricsCheckerPanel_lyricsInput'].bind('<Insert>', '_Ins')          ## Insert on Input
    HomeWindow['lyricsCheckerPanel_lyricsInput'].bind('<Delete>', '_Del')          ## Delete on Input
    for key in ['openWebButton', 'pasteClipboardButton', 'clearInputButton', 'checkLyricsButton']: HomeWindow['lyricsCheckerPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## Profanity Engine Editor: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    HomeWindow['profanityEnginePanel_wordEditorInput'].bind('<Return>', '_Enter')  ## Enter on Word Input
    HomeWindow['profanityEnginePanel_definitionsList'].bind('<Delete>', '_Del')    ## Delete on Word List
    for key in ['definitionsList', 'searchClearInput', 'sortButton', 'importButton', 'exportButton', 'clearButton', 'swearPredefinedWords', 'alcoholPredefinedWords', 'drugsVapePredefinedWords', 'sexPredefinedWords', 'otherPredefinedWords', 'saveEditButton', 'deleteWordButton', 'newWordButton']: HomeWindow['profanityEnginePanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## Metadata Burner: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    metadataBurnerLyricsOnly, metadataBurnerMultipleArtist, metadataBurnerRenameFile = False, False, True ## App Variables
    for key in ['songLocationBrowser', 'songArtworkBrowser', 'onlyLyricsCheckbox', 'multipleArtistsCheckbox', 'renameFileCheckbox', 'burnButton']: HomeWindow['metadataBurnerPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## Playlist Maker: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    HomeWindow['playlistMakerPanel_playlistListbox'].bind('<Return>', '_Enter')  ## Enter on Playlist list
    HomeWindow['playlistMakerPanel_playlistListbox'].bind('<Delete>', '_Del')    ## Delete on Playlist List
    HomeWindow['playlistMakerPanel_playlistInput'].bind('<Return>', '_Enter')    ## Enter on Playlist Input
    for key in ['playlistListbox', 'openPlaylistButton', 'addPlaylistButton', 'removePlaylistButton', 'importPlaylistButton', 'exportPlaylistButton']: HomeWindow['playlistMakerPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## CD Burner: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    cdBurningList = []
    for key in ['songsListbox', 'fileBrowseButton', 'addSongButton', 'removeSongButton', 'clearSongsButton', 'burnButton']: HomeWindow['cdburnerPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## CD Ripper: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    for key in ['songsListbox', 'importBrowseButton', 'exportBrowseButton', 'ripButton']: HomeWindow['cdripperPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## Music Tools: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    for key in toolPanelApps: HomeWindow['musicTool_' + key.replace(" ", "_")].Widget.config(cursor="hand2") ## Hover icons
    for key in ['moveSidebarButton']: HomeWindow['musicToolsPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## Desktop Mover: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    for key in ['allListbox', 'pinButton', 'allUpButton', 'allDownButton', 'allResetButton', 'pinnedListbox', 'unpinButton', 'pinnedUpButton', 'pinnedDownButton', 'pinnedResetButton']: HomeWindow['desktopMoverPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## Main Window: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    savedWifiStatus = wifiStatus
    HomeWindow['versionTextHomeBottom'].Widget.config(cursor="hand2") ## Hover icons
    if appSelected != None:
        HomeWindow['musicSearchPanel'].update(visible=False)
        HomeWindow['creditsTextHomeBottom'].Widget.config(cursor="hand2") ## Hover icons
        if (appSelected.replace("_", " ") not in onlineApps or wifiStatus):
            for app in toolPanelApps:
                if app.replace(" ", "_") == appSelected: HomeWindow[(app[:4].lower() + app[4:]).replace(" ", "") + "Panel"].update(visible=True)
                else: HomeWindow[(app[:4].lower() + app[4:]).replace(" ", "") + "Panel"].update(visible=False)
            if appSelected == "Music_Tools": HomeWindow["musicToolsPanel"].update(visible=True) ## Show Music Tools Window
            elif appSelected != "Music_Tools": HomeWindow["musicToolsPanel"].update(visible=False) ## Hide Music Tools Window
            if appSelected == "Settings": HomeWindow.Element('settingsPanel_cacheStorageText').Update(str(round(sum(os.path.getsize(os.path.join(dp, f)) for dp, _, filenames in os.walk(str(os.getenv('APPDATA')) + "\\Oszust Industries\\Oszust OS Music Tools\\Cache\\") for f in filenames) / (1024 * 1024), 2)) + " MB")
        else:
            for app in toolPanelApps: HomeWindow[(app[:4].lower() + app[4:]).replace(" ", "") + "Panel"].update(visible=False)
            appSelected = "Music_Tools" ## App Variables
            HomeWindow['musicToolsPanel'].update(visible=True)
    else:
        if wifiStatus:
            appSelected = "Music_Search" ## App Variables
            HomeWindow['creditsTextHomeBottom'].Widget.config(cursor="hand2") ## Hover icons
        else:
            appSelected = "Music_Tools" ## App Variables
            HomeWindow['musicToolsPanel'].update(visible=True)
            HomeWindow['musicSearchPanel'].update(visible=False)
    if userSettingsData["firstSoftwareUse"]:
        popupMessage("Welcome to Music Tools!", "Explore the pinned apps on the left sidebar. Look for blue buttons marked with question marks for assistance. Access more tools in the drawer by clicking the nine-square icon.", "help") ## First Software Launch Popup
        savingSettings("firstSoftwareUse", False)
    for app in pinnedApps: HomeWindow[app.replace(" ", "_") + "_AppSelector"].Widget.config(cursor="hand2") ## App Side Panel hover icons
    HomeWindow.un_hide()
    ## Reading Home Window
    while True:
        event, values = HomeWindow.read(timeout=10)
        homeWindowLocationX, homeWindowLocationY = HomeWindow.CurrentLocation() ## X & Y Location of Home Window
## Closed Window      
        if event == sg.WIN_CLOSED or event == 'Exit':
            HomeWindow.close()
            try: output.close()
            except: pass
            thisSystem = psutil.Process(os.getpid()) ## Close Program
            thisSystem.terminate()
            return
## Home Screen Bottom Text
        elif event == 'versionTextHomeBottom' and wifiStatus: ## Home Screen: Version Text
            webbrowser.open("https://github.com/Oszust-Industries/" + systemName.replace(" ", "-") + "/releases", new=2, autoraise=True)
            checkAutoUpdater("check")
        elif event == 'creditsTextHomeBottom' and wifiStatus: webbrowser.open("https://github.com/Oszust-Industries/", new=2, autoraise=True) ## Home Screen: Credits Button
## Side Panel Apps (Buttons)
        elif "_AppSelector" in event and event.replace("_AppSelector", "") != appSelected:
            if savedWifiStatus != wifiStatus: ## Change in Internet
                appSelected = event.replace("_AppSelector", "")
                HomeWindow.close()
                homeScreen()
                return
            elif appSelected == "desktop_mover" and (toolLayoutData["toolPanelApps"] != toolPanelApps or toolLayoutData["pinnedApps"] != pinnedApps): ## Save Desktop Mover Changes
                appSelected = event.replace("_AppSelector", "")
                with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "toolLayout.json"), 'w') as file:
                    toolLayoutData = {}
                    toolLayoutData["toolPanelApps"] = toolPanelApps
                    toolLayoutData["pinnedApps"] = pinnedApps
                    json.dump(toolLayoutData, file)
                HomeWindow.close()
                homeScreen()
                return
            appSelected = event.replace("_AppSelector", "")
            HomeWindow["desktopMoverPanel"].update(visible=False)
            for app in toolPanelApps:
                if app.replace(" ", "_") == appSelected: HomeWindow[(app[:4].lower() + app[4:]).replace(" ", "") + "Panel"].update(visible=True)
                else: HomeWindow[(app[:4].lower() + app[4:]).replace(" ", "") + "Panel"].update(visible=False)
            if appSelected == "Music_Tools": HomeWindow["musicToolsPanel"].update(visible=True) ## Show Music Tools Window
            elif appSelected != "Music_Tools": HomeWindow["musicToolsPanel"].update(visible=False) ## Hide Music Tools Window
            if appSelected == "Settings": HomeWindow.Element('settingsPanel_cacheStorageText').Update(str(round(sum(os.path.getsize(os.path.join(dp, f)) for dp, _, filenames in os.walk(str(os.getenv('APPDATA')) + "\\Oszust Industries\\Oszust OS Music Tools\\Cache\\") for f in filenames) / (1024 * 1024), 2)) + " MB")
## Music Tools
        elif appSelected == "Music_Tools":
            if savedWifiStatus != wifiStatus: ## Change in Internet
                HomeWindow.close()
                homeScreen()
                return
            if event == 'musicToolsPanel_moveSidebarButton':
                HomeWindow['desktopMoverPanel'].update(visible=True)
                HomeWindow['musicToolsPanel'].update(visible=False)
                appSelected = "desktop_mover"
            elif "musicTool_" in event:
                HomeWindow["desktopMoverPanel"].update(visible=False)
                appSelected = event.replace("musicTool_", "")
                for tool in toolPanelApps:
                    if tool.replace(" ", "_") == appSelected: HomeWindow[(tool[:4].lower() + tool[4:]).replace(" ", "") + "Panel"].update(visible=True)
                    else: HomeWindow[(tool[:4].lower() + tool[4:]).replace(" ", "") + "Panel"].update(visible=False)
                HomeWindow["musicToolsPanel"].update(visible=False)
## Desktop Mover
        elif appSelected == "desktop_mover":
            if event == 'desktopMoverPanel_pinButton': ## Pin App
                selectedApp = values['desktopMoverPanel_allListbox']
                if selectedApp and selectedApp[0] not in pinnedApps and len(pinnedApps) < 6:
                    pinnedApps.append(selectedApp[0])
                    HomeWindow['desktopMoverPanel_pinnedListbox'].update(values=pinnedApps)
            elif event == 'desktopMoverPanel_unpinButton': ## Unpin App
                selectedApp = values['desktopMoverPanel_pinnedListbox']
                if selectedApp and selectedApp[0] != "Music Tools":
                    pinnedApps.remove(selectedApp[0])
                    HomeWindow['desktopMoverPanel_pinnedListbox'].update(values=pinnedApps)
            elif event == 'desktopMoverPanel_allResetButton': ## Reset Normal
                toolPanelApps = defaultToolPanelApps
                HomeWindow['desktopMoverPanel_allListbox'].update(values=toolPanelApps)
            elif event == 'desktopMoverPanel_pinnedResetButton': ## Reset Pinned
                pinnedApps = defaultPinnedApps
                HomeWindow['desktopMoverPanel_pinnedListbox'].update(values=pinnedApps)
            elif event == 'desktopMoverPanel_allUpButton': ## Normal Up
                selectedApp = values['desktopMoverPanel_allListbox']
                for app in selectedApp:
                    index = toolPanelApps.index(app)
                    if index > 0:
                        toolPanelApps[index], toolPanelApps[index - 1] = toolPanelApps[index - 1], toolPanelApps[index]
                HomeWindow['desktopMoverPanel_allListbox'].update(values=toolPanelApps)
                HomeWindow['desktopMoverPanel_allListbox'].set_value(selectedApp)
            elif event == 'desktopMoverPanel_allDownButton': ## Normal Down
                selectedApp = values['desktopMoverPanel_allListbox']
                for app in reversed(selectedApp):
                    index = toolPanelApps.index(app)
                    if index < len(toolPanelApps) - 1:
                        toolPanelApps[index], toolPanelApps[index + 1] = toolPanelApps[index + 1], toolPanelApps[index]
                HomeWindow['desktopMoverPanel_allListbox'].update(values=toolPanelApps)
                HomeWindow['desktopMoverPanel_allListbox'].set_value(selectedApp)
            elif event == 'desktopMoverPanel_pinnedUpButton': ## Pinned Up
                selectedApp = values['desktopMoverPanel_pinnedListbox']
                for app in selectedApp:
                    index = pinnedApps.index(app)
                    if index > 0:
                        pinnedApps[index], pinnedApps[index - 1] = pinnedApps[index - 1], pinnedApps[index]
                HomeWindow['desktopMoverPanel_pinnedListbox'].update(values=pinnedApps)
                HomeWindow['desktopMoverPanel_pinnedListbox'].set_value(selectedApp)
            elif event == 'desktopMoverPanel_pinnedDownButton': ## Pinned Down
                selectedApp = values['desktopMoverPanel_pinnedListbox']
                for app in reversed(selectedApp):
                    index = pinnedApps.index(app)
                    if index < len(pinnedApps) - 1:
                        pinnedApps[index], pinnedApps[index + 1] = pinnedApps[index + 1], pinnedApps[index]
                HomeWindow['desktopMoverPanel_pinnedListbox'].update(values=pinnedApps)
                HomeWindow['desktopMoverPanel_pinnedListbox'].set_value(selectedApp)
## Settings (Buttons/Events)
        elif appSelected == "Settings":
            if event == 'settingsPanel_saveButton':
                savingSettings("musicService", values['settingsPanel_musicServiceCombo'])
                try:
                    if os.access(values['settingsPanel_defaultDownloadLocationInput'], os.W_OK) and (open(os.path.join(values['settingsPanel_defaultDownloadLocationInput'], 'test_write.tmp'), 'w').close() or os.remove(os.path.join(values['settingsPanel_defaultDownloadLocationInput'], 'test_write.tmp')) or True): savingSettings("defaultDownloadLocation", values['settingsPanel_defaultDownloadLocationInput'])
                except: popupMessage("Settings", "The Default Download Location must be a valid folder with write permissions.", "error")
                if values['settingsPanel_billboardListCombo'] != billboardList:
                    savingSettings("billboardList", values['settingsPanel_billboardListCombo'])
                    try: os.remove(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Billboard.txt"))
                    except: pass
                    HomeWindow.close()
                    loadingScreen("Billboard_List_Download", False) ## Download Billboard Data
                    homeScreen()
                    return
                ## Set Variables as Settings
                try: billboardList = userSettingsData["billboardList"]
                except: billboardList = "hot 100"
                try: defaultDownloadLocation = userSettingsData["defaultDownloadLocation"]
                except: defaultDownloadLocation = str(pathlib.Path.home() / "Downloads")
                HomeWindow['musicDownloaderPanel_downloadLocationInput'].update(defaultDownloadLocation)
                HomeWindow['youtubeDownloaderPanel_downloadLocationInput'].update(defaultDownloadLocation)
                print(f"[INFO]: Settings were saved: {userSettingsData}")
            elif event == 'settingsPanel_cleanCacheButton':
                if popupMessage("Cache Cleaner Confirmation", "Are you sure you want to delete all software Cache?", "confirmation"):
                    try:
                        for location in ["Artworks", "Mini Artworks", "Music Search Info", "Music Search List Info"]:
                            if os.path.exists(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Music Search", location)) and os.listdir(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Music Search", location)) != []:
                                for item in os.listdir(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Music Search", location)):
                                    os.remove(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Music Search", location, item))
                                os.rmdir(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Music Search", location))
                        HomeWindow.Element('settingsPanel_cacheStorageText').Update(str(round(sum(os.path.getsize(os.path.join(dp, f)) for dp, _, filenames in os.walk(str(os.getenv('APPDATA')) + "\\Oszust Industries\\Oszust OS Music Tools\\Cache\\") for f in filenames) / (1024 * 1024), 2)) + " MB")
                        popupMessage("Settings", "Cache has been successfully cleaned.", "success")
                    except: popupMessage("Settings", "Unable to clean the Cache.", "error")
## Music Search (Buttons/Events)
        elif appSelected == "Music_Search":
            if (event == 'musicSearchPanel_normalSongSearchButton' or (event == 'musicSearchPanel_songSearchInput' + '_Enter')) and values['musicSearchPanel_songSearchInput'].replace(" ","").lower() not in ["", "resultfailedtoload", "billboardfailedtoload"]: geniusMusicSearch(values['musicSearchPanel_songSearchInput'], False) ## Music Search
            elif (event == 'musicSearchPanel_listSongSearchButton' or (event == 'musicSearchPanel_songSearchInput' + '_Ins') or (event == 'musicSearchPanel_billboardTopSongsList' + '_Ins')) and values['musicSearchPanel_songSearchInput'].replace(" ","").lower() not in ["", "resultfailedtoload", "billboardfailedtoload"]: geniusMusicSearchList(values['musicSearchPanel_songSearchInput']) ## Music Search All Results
            elif event == 'musicSearchPanel_clearSongSearchInputButton' or (event == 'musicSearchPanel_songSearchInput' + '_Del'): HomeWindow.Element('musicSearchPanel_songSearchInput').Update("") ## Clear Music Search Input
            elif event == 'musicSearchPanel_billboardTopSongsList' and (topSongsList[values['musicSearchPanel_billboardTopSongsList'][0]][0].split('.')[1].replace(" ","").replace(".","").lower() not in ["", "resultfailedtoload", "billboardfailedtoload"]): HomeWindow.Element('musicSearchPanel_songSearchInput').Update((topSongsList[values['musicSearchPanel_billboardTopSongsList'][0]][0]).split(". ", 1)[1].split("   (", 1)[0]) ## Copy Top 100 to Music Search
            elif (event == 'musicSearchPanel_billboardTopSongsList' + '_Enter'): geniusMusicSearch((topSongsList[values['musicSearchPanel_billboardTopSongsList'][0]][0]).split(". ", 1)[1].split("   (", 1)[0], False) ## Top 100 Song Search
## Music Downloader (Buttons/Events)
        elif appSelected == "Music_Downloader":
            if not userSettingsData["musicSearchContract"]:
                popupMessage("Terms of Service", "Songs downloaded from Music Downloader cannot be used in public settings. Using songs on the radio or in any public context would violate YouTube's Terms of Service and FCC regulations.", "announcement")
                savingSettings("musicSearchContract", True)
            if event == 'musicDownloaderPanel_helpButton': popupMessage("Helper", "To download a song, enter a YouTube link and click 'Download'. Next, a new window will appear, correct the song title if needed and search. Once found, click 'Open' to add metadata to your download.", "help") ## Help Popup
            elif event == 'musicDownloaderPanel_pasteClipboardButton': ## Paste Clipboard in YouTube Link Input
                try:
                    win32clipboard.OpenClipboard()
                    HomeWindow.Element('musicDownloaderPanel_youtubeUrlInput').Update(win32clipboard.GetClipboardData())
                    win32clipboard.CloseClipboard()
                except: pass
            elif event == 'musicDownloaderPanel_openYoutubeButton': webbrowser.open("youtube.com", new=2, autoraise=True) ## Open YouTube Website
            elif event == 'musicDownloaderPanel_resetSettings': ## Reset Settings
                musicBurnLyrics, musicCompilationAlbum, musicDownloadName = True, False, False
                HomeWindow['musicDownloaderPanel_burnLyricsCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\true.png')
                HomeWindow['musicDownloaderPanel_compilationCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\false.png')
                HomeWindow['musicDownloaderPanel_changeNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\false.png')
                HomeWindow.Element('musicDownloaderPanel_changeNameInput').Update("")
                for key in ['musicDownloaderPanel_changeNameInput', 'musicDownloaderPanel_changeNameClipboard', 'musicDownloaderPanel_changeNameClearInput']: HomeWindow.Element(key).Update(visible=False)
            elif event == 'musicDownloaderPanel_burnLyricsCheckbox' and musicBurnLyrics == True: ## Burn Lyrics - False
                HomeWindow['musicDownloaderPanel_burnLyricsCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\false.png')
                musicBurnLyrics = False
            elif event == 'musicDownloaderPanel_burnLyricsCheckbox' and musicBurnLyrics == False: ## Burn Lyrics - True
                HomeWindow['musicDownloaderPanel_burnLyricsCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\true.png')
                musicBurnLyrics = True
            elif event == 'musicDownloaderPanel_compilationCheckbox' and musicCompilationAlbum == True: ## Compilation Album - False
                HomeWindow['musicDownloaderPanel_compilationCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\false.png')
                musicCompilationAlbum = False
            elif event == 'musicDownloaderPanel_compilationCheckbox' and musicCompilationAlbum == False: ## Compilation Album - True
                HomeWindow['musicDownloaderPanel_compilationCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\true.png')
                musicCompilationAlbum = True
            elif event == 'musicDownloaderPanel_changeNameCheckbox' and musicDownloadName == True: ## Change File Name - False
                HomeWindow['musicDownloaderPanel_changeNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\false.png')
                for key in ['musicDownloaderPanel_changeNameInput', 'musicDownloaderPanel_changeNameClipboard', 'musicDownloaderPanel_changeNameClearInput']: HomeWindow.Element(key).Update(visible=False)
                musicDownloadName = False
            elif event == 'musicDownloaderPanel_changeNameCheckbox' and musicDownloadName == False: ## Change File Name - True
                HomeWindow['musicDownloaderPanel_changeNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\true.png')
                for key in ['musicDownloaderPanel_changeNameInput', 'musicDownloaderPanel_changeNameClipboard', 'musicDownloaderPanel_changeNameClearInput']: HomeWindow.Element(key).Update(visible=True)
                musicDownloadName = True
            elif event == 'musicDownloaderPanel_changeNameClipboard': ## Paste Clipboard in File Name Input
                try:
                    win32clipboard.OpenClipboard()
                    HomeWindow.Element('musicDownloaderPanel_changeNameInput').Update(win32clipboard.GetClipboardData())
                    win32clipboard.CloseClipboard()
                except: pass
            elif event == 'musicDownloaderPanel_changeNameClearInput': HomeWindow.Element('musicDownloaderPanel_changeNameInput').Update("") ## Clear File Name Input
            elif event == 'musicDownloaderPanel_downloadButton' or (event == 'musicDownloaderPanel_youtubeUrlInput' + '_Enter'): ## Download Music Button
                if os.path.isdir(values['musicDownloaderPanel_downloadLocationInput'].replace("/", "\\")) == False: popupMessage("Music Downloader", "The provided download location is invalid.", "error", 5000) ## Invalid Download Location Popup
                elif musicDownloadName != False and os.path.isfile(os.path.join(values['musicDownloaderPanel_downloadLocationInput'].replace("/", "\\"), values['musicDownloaderPanel_changeNameInput'] + ".mp3")): popupMessage("Music Downloader", "The selected name already exists at the download location. Please choose a different name for the download.", "error", 5000) ## Rename Already Exists Popup
                elif musicDownloadName != False and (len(values['musicDownloaderPanel_changeNameInput']) > 255 or len(values['musicDownloaderPanel_changeNameInput']) == 0 or any(char in values['musicDownloaderPanel_changeNameInput'] for char in r'<>:"/\\|?*') or values['musicDownloaderPanel_changeNameInput'].endswith(' ') or values['musicDownloaderPanel_changeNameInput'].endswith('.')): popupMessage("Music Downloader", "Invalid naming scheme for Windows. Please choose a different name for the download.", "error", 5000) ## Invalid Naming Scheme Popup
                elif ("youtube.com" in values['musicDownloaderPanel_youtubeUrlInput'].lower() or "youtu.be" in values['musicDownloaderPanel_youtubeUrlInput'].lower()):
                    if musicDownloadName: musicDownloadName = values['musicDownloaderPanel_changeNameInput']
                    loadingScreen("Music_Downloader", True, values['musicDownloaderPanel_youtubeUrlInput'], values['musicDownloaderPanel_downloadLocationInput'].replace("/", "\\"), musicBurnLyrics, musicCompilationAlbum, musicDownloadName)
                    HomeWindow["musicDownloaderPanel_youtubeUrlInput"].update("")
                    if musicDownloadName != False: musicDownloadName = True
                else: popupMessage("Music Downloader", "The provided YouTube link is invalid.", "error", 5000) ## Invalid Link Popup
## YouTube Downloader (Buttons/Events)
        elif appSelected == "Youtube_Downloader":
            if event == 'youtubeDownloaderPanel_pasteClipboardButton': ## Paste Clipboard in YouTube Link Input
                try:
                    win32clipboard.OpenClipboard()
                    HomeWindow.Element('youtubeDownloaderPanel_youtubeUrlInput').Update(win32clipboard.GetClipboardData())
                    win32clipboard.CloseClipboard()
                except: pass
            elif event == 'youtubeDownloaderPanel_openYoutubeButton': webbrowser.open("youtube.com", new=2, autoraise=True) ## Open YouTube Website
            elif event == 'youtubeDownloaderPanel_resetSettings': ## Reset Settings
                youtubeAudioDownload, youtubeVideoDownload, youtubeDownloadName = False, True, False
                HomeWindow['youtubeDownloaderPanel_audioDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\false.png')
                HomeWindow['youtubeDownloaderPanel_videoDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\true.png')
                HomeWindow['youtubeDownloaderPanel_changeNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\false.png')
                HomeWindow.Element('youtubeDownloaderPanel_changeNameInput').Update("")
                for key in ['youtubeDownloaderPanel_changeNameInput', 'youtubeDownloaderPanel_changeNameClipboard', 'youtubeDownloaderPanel_changeNameClearInput']: HomeWindow.Element(key).Update(visible=False)
            elif event == 'youtubeDownloaderPanel_audioDownloadCheckbox' and youtubeAudioDownload == True: ## Download Audio - False
                HomeWindow['youtubeDownloaderPanel_audioDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\false.png')
                youtubeAudioDownload = False
            elif event == 'youtubeDownloaderPanel_audioDownloadCheckbox' and youtubeAudioDownload == False: ## Download Audio - True
                HomeWindow['youtubeDownloaderPanel_audioDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\true.png')
                youtubeAudioDownload = True
            elif event == 'youtubeDownloaderPanel_videoDownloadCheckbox' and youtubeVideoDownload == True: ## Download Video - False
                HomeWindow['youtubeDownloaderPanel_videoDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\false.png')
                youtubeVideoDownload = False
            elif event == 'youtubeDownloaderPanel_videoDownloadCheckbox' and youtubeVideoDownload == False: ## Download Video - True
                HomeWindow['youtubeDownloaderPanel_videoDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\true.png')
                youtubeVideoDownload = True
            elif event == 'youtubeDownloaderPanel_changeNameCheckbox' and youtubeDownloadName == True: ## Change File Name - False
                HomeWindow['youtubeDownloaderPanel_changeNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\false.png')
                for key in ['youtubeDownloaderPanel_changeNameInput', 'youtubeDownloaderPanel_changeNameClipboard', 'youtubeDownloaderPanel_changeNameClearInput']: HomeWindow.Element(key).Update(visible=False)
                youtubeDownloadName = False
            elif event == 'youtubeDownloaderPanel_changeNameCheckbox' and youtubeDownloadName == False: ## Change File Name - True
                HomeWindow['youtubeDownloaderPanel_changeNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\true.png')
                for key in ['youtubeDownloaderPanel_changeNameInput', 'youtubeDownloaderPanel_changeNameClipboard', 'youtubeDownloaderPanel_changeNameClearInput']: HomeWindow.Element(key).Update(visible=True)
                youtubeDownloadName = True
            elif event == 'youtubeDownloaderPanel_changeNameClipboard': ## Paste Clipboard in File Name Input
                try:
                    win32clipboard.OpenClipboard()
                    HomeWindow.Element('youtubeDownloaderPanel_changeNameInput').Update(win32clipboard.GetClipboardData())
                    win32clipboard.CloseClipboard()
                except: pass
            elif event == 'youtubeDownloaderPanel_changeNameClearInput': HomeWindow.Element('youtubeDownloaderPanel_changeNameInput').Update("") ## Clear File Name Input
            elif event == 'youtubeDownloaderPanel_downloadButton' or (event == 'youtubeDownloaderPanel_youtubeUrlInput' + '_Enter'): ## Download YouTube Button
                if os.path.isdir(values['youtubeDownloaderPanel_downloadLocationInput'].replace("/", "\\")) == False: popupMessage("YouTube Downloader", "The provided download location is invalid.", "error", 5000) ## Invalid Download Location Popup
                elif youtubeAudioDownload == False and youtubeVideoDownload == False: popupMessage("YouTube Downloader", "Please select either audio or video download.", "error", 5000) ## Audio/Video Unpicked Popup
                elif youtubeDownloadName != False and os.path.isfile(os.path.join(values['youtubeDownloaderPanel_downloadLocationInput'].replace("/", "\\"), values['youtubeDownloaderPanel_changeNameInput'] + ".mp4")) and youtubeAudioDownload == False: popupMessage("YouTube Downloader", "The selected name already exists at the download location. Please choose a different name for the download.", "error", 5000) ## Rename Already Exists Popup Video
                elif youtubeDownloadName != False and os.path.isfile(os.path.join(values['youtubeDownloaderPanel_downloadLocationInput'].replace("/", "\\"), values['youtubeDownloaderPanel_changeNameInput'] + ".mp3")) and youtubeVideoDownload == False: popupMessage("YouTube Downloader", "The selected name already exists at the download location. Please choose a different name for the download.", "error", 5000) ## Rename Already Exists Popup Music
                elif youtubeDownloadName != False and (os.path.isfile(os.path.join(values['youtubeDownloaderPanel_downloadLocationInput'].replace("/", "\\"), values['youtubeDownloaderPanel_changeNameInput'] + ".mp3")) or os.path.isfile(os.path.join(values['youtubeDownloaderPanel_downloadLocationInput'].replace("/", "\\"), values['youtubeDownloaderPanel_changeNameInput'] + ".mp4"))): popupMessage("YouTube Downloader", "The selected name already exists at the download location. Please choose a different name for the download.", "error", 5000) ## Rename Already Exists Popup Both
                elif youtubeDownloadName != False and (len(values['youtubeDownloaderPanel_changeNameInput']) > 255 or len(values['youtubeDownloaderPanel_changeNameInput']) == 0 or any(char in values['youtubeDownloaderPanel_changeNameInput'] for char in r'<>:"/\\|?*') or values['youtubeDownloaderPanel_changeNameInput'].endswith(' ') or values['youtubeDownloaderPanel_changeNameInput'].endswith('.')): popupMessage("YouTube Downloader", "Invalid naming scheme for Windows. Please choose a different name for the download.", "error", 5000) ## Invalid Naming Scheme Popup
                elif ("youtube.com" in values['youtubeDownloaderPanel_youtubeUrlInput'].lower() or "youtu.be" in values['youtubeDownloaderPanel_youtubeUrlInput'].lower()):
                    if youtubeDownloadName: youtubeDownloadName = values['youtubeDownloaderPanel_changeNameInput']
                    loadingScreen("YouTube_Downloader", True, values['youtubeDownloaderPanel_youtubeUrlInput'], values['youtubeDownloaderPanel_downloadLocationInput'].replace("/", "\\"), youtubeAudioDownload, youtubeVideoDownload, youtubeDownloadName)
                    HomeWindow["youtubeDownloaderPanel_youtubeUrlInput"].update("")
                    if youtubeDownloadName != False: youtubeDownloadName = True
                else: popupMessage("YouTube Downloader", "The provided YouTube link is invalid.", "error", 5000) ## Invalid Link Popup
## Lyrics Checker (Buttons/Events)
        elif appSelected == "Lyrics_Checker":
            if event == 'lyricsCheckerPanel_openWebButton': webbrowser.open("google.com", new=2, autoraise=True) ## Open Web Browser
            elif event == 'lyricsCheckerPanel_pasteClipboardButton': ## Paste Clipboard in Lyrics Input
                try:    
                    win32clipboard.OpenClipboard()
                    HomeWindow.Element('lyricsCheckerPanel_lyricsInput').Update(win32clipboard.GetClipboardData())
                    win32clipboard.CloseClipboard()
                except: pass
            elif event == 'lyricsCheckerPanel_clearInputButton' or (event == 'lyricsCheckerPanel_lyricsInput' + '_Del'): ## Clear Lyrics Input
                HomeWindow.Element('lyricsCheckerPanel_lyricsInput').Update("")
                HomeWindow.Element('lyricsCheckerPanel_songUsableText').Update("Profanity Engine: Not checked yet", text_color='#FFFFFF', font='Any 11')
            elif event == 'lyricsCheckerPanel_checkLyricsButton' or (event == 'lyricsCheckerPanel_lyricsInput' + '_Ins'): ## Check Lyrics
                if len(values['lyricsCheckerPanel_lyricsInput'].strip()) > 0: musicSearchPrintSongLyrics("lyricsCheck", values['lyricsCheckerPanel_lyricsInput'].splitlines())
                else: HomeWindow.Element('lyricsCheckerPanel_songUsableText').Update("Profanity Engine: No lyrics found", text_color='#FFFFFF', font='Any 11')
            elif event in ['Copy', 'Lookup Definition', 'Add to Profanity Engine', 'Remove from Profanity Engine']: ## Right Click Menu Actions
                lyricsLine:sg.Multiline = HomeWindow['lyricsCheckerPanel_lyricsInput']
                try:
                    if event == 'Copy': ## Copy Lyrics Text
                        try:
                            MusicSearchSongWindow.TKroot.clipboard_clear()
                            MusicSearchSongWindow.TKroot.clipboard_append(lyricsLine.Widget.selection_get())
                        except: pass
                    elif event == 'Lookup Definition': webbrowser.open("https://www.dictionary.com/browse/" + (lyricsLine.Widget.selection_get().split(" ")[0]).replace(",", "").replace(".", "").replace("?", "").replace("!", "").replace(" ", "-"), new=2, autoraise=True)
                    elif event == 'Add to Profanity Engine' and lyricsLine.Widget.selection_get().strip().replace("'", "~").lower() not in profanityEngineDefinitions: ## Add Text to Profanity Engine
                        try:
                            wordToAdd = re.sub(r'[\'"\.,!?;:]', '', (lyricsLine.Widget.selection_get()).strip().lower())
                            profanityEngineDefinitions.append(wordToAdd.replace("'", "~"))
                            saveProfanityEngine(profanityEngineDefinitions)
                            musicSearchPrintSongLyrics("lyricsCheck", values['lyricsCheckerPanel_lyricsInput'].splitlines())
                            popupMessage("Profanity Engine", '"' + wordToAdd + '"  has been successfully added to the Profanity Engine.', "saved", 3000) ## Show Success Message
                        except: popupMessage("Profanity Engine", 'Failed to add "' + wordToAdd + '" to the Profanity Engine.', "error", 3000) ## Show Error Message
                    elif event == 'Remove from Profanity Engine': ## Remove Text from Profanity Engine
                        try:
                            wordToRemove = re.sub(r'[\'"\.,!?;:]', '', (lyricsLine.Widget.selection_get()).strip().lower())
                            try:
                                profanityEngineDefinitions.remove(wordToRemove.replace("'", "~"))
                                saveProfanityEngine(profanityEngineDefinitions)
                                musicSearchPrintSongLyrics("lyricsCheck", values['lyricsCheckerPanel_lyricsInput'].splitlines())
                                popupMessage("Profanity Engine", '"' + wordToRemove + '"  has been successfully added to the Profanity Engine.', "saved", 3000) ## Show Success Message
                            except: popupMessage("Profanity Engine", '"' + wordToRemove + '" is not in the Profanity Engine.', "fail", 3000) ## Show Fail Message
                        except: popupMessage("Profanity Engine", 'Failed to add "' + wordToRemove + '" to the Profanity Engine.', "error", 3000) ## Show Error Message
                except: pass
## Profanity Engine Editor (Buttons/Events)
        elif appSelected == "Profanity_Engine":
            if event == 'profanityEnginePanel_searchInput': ## Search Profanity Definitions
                if values['profanityEnginePanel_searchInput'].strip().lower() != "": HomeWindow['profanityEnginePanel_definitionsList'].update([item.replace("~", "'") for item in profanityEngineDefinitions if (values['profanityEnginePanel_searchInput'].strip().lower().replace("'", "~")) in item.lower()]) ##Searched List
                else: HomeWindow.Element('profanityEnginePanel_definitionsList').Update([item.replace("~", "'") for item in profanityEngineDefinitions]) ## Default List
            elif values['profanityEnginePanel_definitionsList'] and event == 'Delete': ## Right Click - Delete
                try: profanityEngineDefinitions.remove(values['profanityEnginePanel_definitionsList'][0].replace("'", "~"))
                except: pass
                saveProfanityEngine(profanityEngineDefinitions)
                HomeWindow.Element('profanityEnginePanel_wordEditorInput').Update("")
            elif event == 'profanityEnginePanel_searchClearInput': ## Clear Search Input
                HomeWindow.Element('profanityEnginePanel_searchInput').Update("")
                HomeWindow.Element('profanityEnginePanel_definitionsList').Update([item.replace("~", "'") for item in profanityEngineDefinitions]) ## Default List
            elif event == 'profanityEnginePanel_definitionsList' and len(values['profanityEnginePanel_definitionsList']) > 0: HomeWindow.Element('profanityEnginePanel_wordEditorInput').Update(values['profanityEnginePanel_definitionsList'][0]) ## Copy Word to Editor Input
            elif event == 'profanityEnginePanel_sortButton': ## Sort Entire List
                profanityEngineDefinitions = sorted(profanityEngineDefinitions)
                saveProfanityEngine(profanityEngineDefinitions)
            elif event == 'profanityEnginePanel_importButton': ## Import New List from Downloads
                profanityEngineDefinitions, fileBrowserWindow = [], sg.Window("File Location Selector", [[sg.Text("Select a file location:")], [sg.Input(key="fileLocation"), sg.FileBrowse(file_types=(("Text Files", "*.txt"), ("All Files", "*.*")),initial_folder=defaultDownloadLocation)], [sg.Push(), sg.Button("OK"), sg.Push()]], no_titlebar=True, keep_on_top=True, finalize=True)
                while True:
                    event, values = fileBrowserWindow.read(timeout=10)
                    try: fileBrowserWindow.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - fileBrowserWindow.size[0] // 2, HomeWindow.TKroot.winfo_y() + HomeWindow.TKroot.winfo_height() // 2 - fileBrowserWindow.size[1] // 2)
                    except: pass
                    if event == sg.WINDOW_CLOSED or event == "OK":
                        fileLocation = values["fileLocation"]
                        fileBrowserWindow.close()
                        break
                if fileLocation != "":
                    with open(fileLocation, 'r') as file:
                        for line in file: profanityEngineDefinitions.append(line.strip())
                    saveProfanityEngine(profanityEngineDefinitions)
            elif event == 'profanityEnginePanel_exportButton': ## Export List to Downloads
                try:
                    with open(str(defaultDownloadLocation) + "\\ExportedProfanityEngine" + str((datetime.datetime.now()).strftime("%d-%m-%Y-%H-%M-%S")) + ".txt", 'w') as file:
                        for item in profanityEngineDefinitions: file.write(item + '\n')
                    popupMessage("Profanity Engine", "Your Profanity Engine definitions have been successfully exported to your default folder.", "success", 3000) ## Show Error Message
                except: popupMessage("Profanity Engine", "Failed to export Profanity Engine definitions.", "error", 3000) ## Show Error Message
            elif event == 'profanityEnginePanel_clearButton': ## Clear Entire List
                if popupMessage("Profanity Engine Confirmation", "Are you sure you want to delete the entire Profanity Engine definitions list?", "confirmation"):
                    profanityEngineDefinitions = []
                    saveProfanityEngine(profanityEngineDefinitions)
            elif event == 'profanityEnginePanel_saveEditButton' and values['profanityEnginePanel_wordEditorInput'].strip() not in [""]: ## Save Editor Word to List
                profanityEngineDefinitions.append(values['profanityEnginePanel_wordEditorInput'].strip().replace("'", "~"))
                saveProfanityEngine(profanityEngineDefinitions)
                HomeWindow.Element('profanityEnginePanel_wordEditorInput').Update("")
            elif event == 'profanityEnginePanel_deleteWordButton' or (event == 'profanityEnginePanel_definitionsList' + '_Del'): ## Delete Editor Word from List
                try: profanityEngineDefinitions.remove(values['profanityEnginePanel_wordEditorInput'].replace("'", "~"))
                except: pass
                saveProfanityEngine(profanityEngineDefinitions)
                HomeWindow.Element('profanityEnginePanel_wordEditorInput').Update("")
            elif event == 'profanityEnginePanel_newWordButton' or (event == 'profanityEnginePanel_wordEditorInput' + '_Enter'): ## New Editor Word
                if values['profanityEnginePanel_wordEditorInput'] not in profanityEngineDefinitions:
                    profanityEngineDefinitions.append(values['profanityEnginePanel_wordEditorInput'].strip().replace("'", "~"))
                    saveProfanityEngine(profanityEngineDefinitions)
                HomeWindow.Element('profanityEnginePanel_wordEditorInput').Update("")
            elif 'PredefinedWords' in event: ## Add default Profanity Engine Definitions
                with open(os.path.join(pathlib.Path(__file__).resolve().parent, "data", "Default data", "profanityEngineDefaults.json"), 'r') as file: data = json.load(file)
                profanityEngineDefinitions.extend(data['categories'][event.replace("profanityEnginePanel_", "").replace("PredefinedWords", "")])
                saveProfanityEngine(profanityEngineDefinitions)
## Metadata Burner (Buttons/Events)              
        elif appSelected == "Metadata_Burner":
            if event == 'metadataBurnerPanel_onlyLyricsCheckbox' and metadataBurnerLyricsOnly == True: ## Lyrics Only - False
                HomeWindow['metadataBurnerPanel_onlyLyricsCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\false.png')
                metadataBurnerLyricsOnly = False
            elif event == 'metadataBurnerPanel_onlyLyricsCheckbox' and metadataBurnerLyricsOnly == False: ## Lyrics Only - True
                HomeWindow['metadataBurnerPanel_onlyLyricsCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\true.png')
                metadataBurnerLyricsOnly = True
            elif event == 'metadataBurnerPanel_multipleArtistsCheckbox' and metadataBurnerMultipleArtist == True: ## Multiple Artists - False
                HomeWindow['metadataBurnerPanel_multipleArtistsCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\false.png')
                metadataBurnerMultipleArtist = False
            elif event == 'metadataBurnerPanel_multipleArtistsCheckbox' and metadataBurnerMultipleArtist == False: ## Multiple Artists - True
                HomeWindow['metadataBurnerPanel_multipleArtistsCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\true.png')
                metadataBurnerMultipleArtist = True
            elif event == 'metadataBurnerPanel_renameFileCheckbox' and metadataBurnerRenameFile == True: ## Change File Name - False
                HomeWindow['metadataBurnerPanel_renameFileCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\false.png')
                metadataBurnerRenameFile = False
            elif event == 'metadataBurnerPanel_renameFileCheckbox' and metadataBurnerRenameFile == False: ## Change File Name - True
                HomeWindow['metadataBurnerPanel_renameFileCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\true.png')
                metadataBurnerRenameFile = True
            elif event == 'metadataBurnerPanel_songLocationInput' and os.path.isfile(os.path.join(values['metadataBurnerPanel_songLocationInput'].replace("/", "\\"))):
                if popupMessage("Metadata Burner Confirmation", "Would you like to to pull existing metadata from the selected file?", "confirmation"):
                    try:
                        audiofile = eyed3.load(values['metadataBurnerPanel_songLocationInput'].replace("/", "\\"))
                        HomeWindow.Element('metadataBurnerPanel_songNameInput').Update(audiofile.tag.title)
                        HomeWindow.Element('metadataBurnerPanel_songArtistInput').Update(audiofile.tag.artist)
                        HomeWindow.Element('metadataBurnerPanel_songAlbumInput').Update(audiofile.tag.album)
                        HomeWindow.Element('metadataBurnerPanel_songYearInput').Update(audiofile.tag.recording_date)
                        HomeWindow.Element('metadataBurnerPanel_songGenreInput').Update((re.search(r'\)([^)]*)$', str(audiofile.tag.genre)).group(1).strip()))
                        HomeWindow.Element('metadataBurnerPanel_albumCurrentLengthInput').Update(audiofile.tag.track_num[0])
                        HomeWindow.Element('metadataBurnerPanel_albumTotalLengthInput').Update(audiofile.tag.track_num[1])
                        HomeWindow.Element('metadataBurnerPanel_cdCurrentLengthInput').Update(audiofile.tag.disc_num[0])
                        HomeWindow.Element('metadataBurnerPanel_cdTotalLengthInput').Update(audiofile.tag.disc_num[1])
                        HomeWindow.Element('metadataBurnerPanel_songPublisherInput').Update(audiofile.tag.publisher)
                        HomeWindow.Element('metadataBurnerPanel_lyricsInput').update("")
                        for lyric in audiofile.tag.lyrics: HomeWindow.Element('metadataBurnerPanel_lyricsInput').print(str(lyric.text) + "\n")
                    except: popupMessage("Metadata Burner", "Unable to open the song's metadata.", "error") ## Failed Reading Popup
            elif event == 'metadataBurnerPanel_burnButton':
                if os.path.isfile(os.path.join(values['metadataBurnerPanel_songLocationInput'].replace("/", "\\"))) == False: popupMessage("Metadata Burner", "The specified song (.mp3) file location is invalid.", "error") ## Invalid Song File Popup
                elif values['metadataBurnerPanel_songArtworkInput'] != "" and os.path.isfile(os.path.join(values['metadataBurnerPanel_songArtworkInput'].replace("/", "\\"))) == False: popupMessage("Metadata Burner", "The specified album artwork file location is invalid.", "error") ## Invalid Artwork File Popup
                elif not (values['metadataBurnerPanel_albumCurrentLengthInput'].isdigit() or values['metadataBurnerPanel_albumCurrentLengthInput'] == "") or not (values['metadataBurnerPanel_albumTotalLengthInput'].isdigit() or values['metadataBurnerPanel_albumTotalLengthInput'] == "") or not (values['metadataBurnerPanel_cdCurrentLengthInput'].isdigit() or values['metadataBurnerPanel_cdCurrentLengthInput'] == "") or not (values['metadataBurnerPanel_cdTotalLengthInput'].isdigit() or values['metadataBurnerPanel_cdTotalLengthInput'] == ""): popupMessage("Metadata Burner", "The specified album location, album length, CD location, and CD length must be numbers.", "error") ## Invalid Number Input Popup
                else:
                    if True:
                        if values['metadataBurnerPanel_songArtworkInput'] != "" and "defaultMusicArtwork.png" not in values['metadataBurnerPanel_songArtworkInput']:
                            pil_image, png_bio = Image.open(values['metadataBurnerPanel_songArtworkInput'].replace("/", "\\")), io.BytesIO()
                            pil_image.save(png_bio, format="PNG")
                            musicSearchResultData, png_data = {}, png_bio.getvalue()
                        else: musicSearchResultData, png_data = {}, str(pathlib.Path(__file__).resolve().parent) + "\\data\\icons\\defaultMusicArtwork.png"
                        musicSearchResultData.update({"geniusMusicSearchArtists": values['metadataBurnerPanel_songArtistInput'], "geniusMusicSearchPrimeArtist": values['metadataBurnerPanel_songArtistInput'], "geniusMusicSearchDate": values['metadataBurnerPanel_songYearInput'],
                        "geniusMusicSearchSongNameInfo": values['metadataBurnerPanel_songNameInput'], "geniusMusicSearchSongName": values['metadataBurnerPanel_songNameInput'], "png_data": png_data, "geniusMusicSearchAlbum": values['metadataBurnerPanel_songAlbumInput'], "geniusMusicSearchAlbumCurrent": values['metadataBurnerPanel_albumCurrentLengthInput'], "geniusMusicSearchAlbumLength": values['metadataBurnerPanel_albumTotalLengthInput'], "geniusMusicSearchCDCurrent": values['metadataBurnerPanel_cdCurrentLengthInput'], "geniusMusicSearchCDLength": values['metadataBurnerPanel_cdTotalLengthInput'], 
                        "geniusMusicSearchGenre": values['metadataBurnerPanel_songGenreInput'], "geniusMusicSearchLabels": values['metadataBurnerPanel_songPublisherInput'].split(", "), "lyrics": "UserInputted", "lyricsListFinal": values['metadataBurnerPanel_lyricsInput'].split("/n"), "extendedSongInfo": [values['metadataBurnerPanel_songNameInput'], values['metadataBurnerPanel_songArtistInput'], values['metadataBurnerPanel_songAlbumInput']]})
                        if metadataBurnerRenameFile: metadataBurnerRenameFile = values['metadataBurnerPanel_songNameInput']
                        else: metadataBurnerRenameFile = (values['metadataBurnerPanel_songLocationInput'].rsplit('/', 1)[-1]).replace(".mp3", "")
                        burnAudioData(values['metadataBurnerPanel_songLocationInput'], metadataBurnerLyricsOnly, metadataBurnerMultipleArtist, metadataBurnerRenameFile, displayMessage=True)
                    if False: popupMessage("Metadata Burner", "Unable to convert user input to metadata.", "error") ## Couldn't Convert Popup
                    metadataBurnerRenameFile = True
                    HomeWindow['metadataBurnerPanel_renameFileCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\true.png')
## CD Burner (Buttons/Events)              
        elif appSelected == "CD_Burner":
            if event == 'cdburnerPanel_songsListbox' and len(values['cdburnerPanel_songsListbox']) > 0: HomeWindow.Element('cdburnerPanel_songInput').Update(values['cdburnerPanel_songsListbox'][0]) ## Copy Song to Song Input
            elif event == 'cdburnerPanel_addSongButton': ## Add Song
                if os.path.isfile(values['cdburnerPanel_songInput']):
                    cdBurningList.append(values['cdburnerPanel_songInput'])
                    HomeWindow.Element('cdburnerPanel_songsListbox').Update(cdBurningList)
                    HomeWindow.Element('cdburnerPanel_songInput').Update("")
                    totalCDUsedSize = 0
                    for songFile in cdBurningList:
                        if os.path.isfile(songFile): totalCDUsedSize += os.path.getsize(songFile)
                    HomeWindow.Element('cdburnerPanel_cdSizeText').Update(f"Space: ({round(totalCDUsedSize / (1024 * 1024), 2)} / 650) MB")
                else: popupMessage("CD Burner", "The selected item is not a valid file.", "error", 5000) ## Show Error Message
            elif event == 'cdburnerPanel_removeSongButton': ## Remove Song
                try: cdBurningList.remove(values['cdburnerPanel_songInput'])
                except: pass
                HomeWindow.Element('cdburnerPanel_songsListbox').Update(cdBurningList)
                HomeWindow.Element('cdburnerPanel_songInput').Update("")
                totalCDUsedSize = 0
                for songFile in cdBurningList:
                    if os.path.isfile(songFile): totalCDUsedSize += os.path.getsize(songFile)
                HomeWindow.Element('cdburnerPanel_cdSizeText').Update(f"Space: ({round(totalCDUsedSize / (1024 * 1024), 2)} / 650) MB")
            elif event == 'cdburnerPanel_clearSongsButton': ## Clear all Songs
                cdBurningList = []
                HomeWindow.Element('cdburnerPanel_songInput').Update("")
                HomeWindow.Element('cdburnerPanel_songsListbox').Update("")
                HomeWindow.Element('cdburnerPanel_cdSizeText').Update("Space: (0.0 / 650) MB")
            elif event == 'cdburnerPanel_burnButton': ## Burn CD
                if len(cdBurningList) > 0: popupMessage("CD Burner", "CD Burner is still being developed.", "error")
                else: popupMessage("CD Burner", "There must be at least one song to start the burn process.", "error", 5000)
## CD Burner (Buttons/Events)              
        elif appSelected == "CD_Ripper":
            if event == 'cdripperPanel_ripButton': ## Rip CD
                popupMessage("CD Ripper", "CD Ripper is still being developed.", "error")
## Playlist Maker (Buttons/Events)              
        elif appSelected == "Playlist_Maker":
            if event == 'playlistMakerPanel_playlistListbox' and len(values['playlistMakerPanel_playlistListbox']) > 0: HomeWindow.Element('playlistMakerPanel_playlistInput').Update(values['playlistMakerPanel_playlistListbox'][0]) ## Copy Playlist to Playlist Input
            elif event == 'playlistMakerPanel_openPlaylistButton' or (event == 'playlistMakerPanel_playlistListbox' + '_Enter'): ## Add New Playlist
                popupMessage("Playlist Maker", "Playlist Maker is still being developed.", "error")
            elif event == 'playlistMakerPanel_addPlaylistButton' or (event == 'playlistMakerPanel_playlistInput' + '_Enter'): ## Add New Playlist
                with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Playlists", values['playlistMakerPanel_playlistInput'] + ".json"), 'w') as f: json.dump({}, f)
                HomeWindow.Element('playlistMakerPanel_playlistListbox').Update(sorted([os.path.splitext(f)[0] for f in os.listdir(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Playlists")) if os.path.isfile(os.path.join(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Playlists"), f))]))
                HomeWindow.Element('playlistMakerPanel_playlistInput').Update("")            
            elif event == 'playlistMakerPanel_removePlaylistButton' or (event == 'playlistMakerPanel_playlistListbox' + '_Del'): ## Remove Playlist
                os.remove(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Playlists", values['playlistMakerPanel_playlistInput'] + ".json"))
                HomeWindow.Element('playlistMakerPanel_playlistListbox').Update(sorted([os.path.splitext(f)[0] for f in os.listdir(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Playlists")) if os.path.isfile(os.path.join(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Playlists"), f))]))
                HomeWindow.Element('playlistMakerPanel_playlistInput').Update("")
            elif event == 'playlistMakerPanel_exportPlaylistButton': ## Export Playlist to Downloads
                if values['playlistMakerPanel_playlistInput'] in values['playlistMakerPanel_playlistListbox']:
                    try:
                        shutil.copyfile(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Playlists", values['playlistMakerPanel_playlistInput'] + ".json"), os.path.join(defaultDownloadLocation, values['playlistMakerPanel_playlistInput'] + ".json"))
                        popupMessage("Playlist Maker", "Your Playlist has been successfully exported to your default folder.", "success", 3000) ## Show Error Message
                    except: popupMessage("Playlist Maker", "Failed to export playlist.", "error", 3000) ## Show Error Message
            elif event == 'playlistMakerPanel_importPlaylistButton': ## Import Playlist
                try:
                    fileBrowserWindow = sg.Window("File Location Selector", [[sg.Text("Select file locations:")], [sg.Input(key="fileLocation"), sg.FilesBrowse(file_types=(("Text Files", "*.json"), ("All Files", "*.*")),initial_folder=defaultDownloadLocation)], [sg.Push(), sg.Button("OK"), sg.Push()]], no_titlebar=True, keep_on_top=True, finalize=True)
                    while True:
                        event, values = fileBrowserWindow.read(timeout=10)
                        try: fileBrowserWindow.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - fileBrowserWindow.size[0] // 2, HomeWindow.TKroot.winfo_y() + HomeWindow.TKroot.winfo_height() // 2 - fileBrowserWindow.size[1] // 2)
                        except: pass
                        if event == sg.WINDOW_CLOSED or event == "OK":
                            if values["fileLocation"] != "":
                                for item in values["fileLocation"].split(";"): shutil.move(item, os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Playlists", item.split('/')[-1]))
                                HomeWindow.Element('playlistMakerPanel_playlistListbox').Update(sorted([os.path.splitext(f)[0] for f in os.listdir(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Playlists")) if os.path.isfile(os.path.join(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Playlists"), f))]))
                            fileBrowserWindow.close()
                            break
                except: popupMessage("Playlist Maker", "Failed to import playlists.", "error", 3000) ## Show Error Message
## Music Player (Buttons/Events)              
        elif appSelected == "Music_Player":
            if musicPlayerQueueCurrentState == "play" and event != 'musicPlayerPanel_timeSlider': ## Update Slider and Time
                HomeWindow['musicPlayerPanel_startTime'].update(f"{int((sliderPos + (mixer.music.get_pos() / 1000)) // 60)}:{int((sliderPos + (mixer.music.get_pos() / 1000)) % 60):02}")
                HomeWindow['musicPlayerPanel_timeSlider'].update(sliderPos + (mixer.music.get_pos() / 1000))
            if musicPlayerQueueCurrentState == "play" and audio.info.length <= sliderPos + (mixer.music.get_pos() / 1000) + 0.5: ## Song Finished
                if musicPlayerLoop and musicPlayerQueueCurrentIndex == len(musicPlayerQueue) - 1: ## Loop on
                    musicPlayerQueueCurrentIndex = 0
                elif musicPlayerQueueCurrentIndex == len(musicPlayerQueue) - 1: ## Loop off
                    musicPlayerQueueCurrentIndex = 0
                    musicPlayerQueueCurrentState = "stop"
                else: musicPlayerQueueCurrentIndex = musicPlayerQueueCurrentIndex + 1 ## Next Song
                sliderPos = 0
                if len(musicPlayerQueue) > 0 and musicPlayerQueueCurrentIndex+1 < len(musicPlayerQueue): HomeWindow['musicPlayerPanel_queueListbox'].update([os.path.splitext(os.path.basename(file_path))[0] for file_path in musicPlayerQueue[musicPlayerQueueCurrentIndex+1:]])
                else: HomeWindow['musicPlayerPanel_queueListbox'].update([])
            if len(musicPlayerQueue) > 0 and musicPlayerCurrentSong != musicPlayerQueue[musicPlayerQueueCurrentIndex]: ## Song is Ready to Play
                musicPlayerCurrentSong = musicPlayerQueue[musicPlayerQueueCurrentIndex]
                try:
                    audiofile = eyed3.load(musicPlayerQueue[musicPlayerQueueCurrentIndex])
                    try: ## Get Song Artwork
                        HomeWindow.Element('musicPlayerPanel_songArtwork').update(filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\defaultMusicPlayerArtwork.png')
                        for tag in audiofile.tag.images:
                            if tag.mime_type == 'image/png':
                                bio = io.BytesIO(tag.image_data)
                                HomeWindow.Element('musicPlayerPanel_songArtwork').update(data=bio.read())
                    except: HomeWindow.Element('musicPlayerPanel_songArtwork').update(filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\defaultMusicPlayerArtwork.png')
                    try: ## Get Song Lyrics
                        HomeWindow.Element('musicPlayerPanel_lyricsListbox').update(disabled=False)
                        formattedLyrics = []
                        for lyric in audiofile.tag.lyrics:
                            lyricLines = lyric.text.split("\n")
                            for line in lyricLines:
                                if line.strip(): formattedLyrics.extend((textwrap.TextWrapper(width=55, max_lines=6, placeholder='...')).wrap(line))
                                else: formattedLyrics.append('')
                        while formattedLyrics and formattedLyrics[-1] == '': formattedLyrics.pop()
                        HomeWindow.Element('musicPlayerPanel_lyricsListbox').update(formattedLyrics)
                        HomeWindow.Element('musicPlayerPanel_lyricsListbox').update(disabled=True)
                    except: HomeWindow.Element('musicPlayerPanel_lyricsListbox').update([])
                    HomeWindow.Element('musicPlayerPanel_songTitle').Update(audiofile.tag.title)
                    HomeWindow.Element('musicPlayerPanel_songArtist').Update(audiofile.tag.artist)
                    HomeWindow.Element('musicPlayerPanel_songAlbum').Update(audiofile.tag.album)
                    if len(str(audiofile.tag.title + " - " + audiofile.tag.artist)) > 60:
                        if len(audiofile.tag.title) > len(audiofile.tag.artist): ## Title is longer than artist
                            HomeWindow.Element('musicPlayerPanel_songTitleLyrics').Update(audiofile.tag.title[:30] + "... - " + audiofile.tag.artist)
                            HomeWindow.Element('musicPlayerPanel_songTitleQueue').Update(audiofile.tag.title[:30] + "... - " + audiofile.tag.artist)
                        else:
                            HomeWindow.Element('musicPlayerPanel_songTitleLyrics').Update(audiofile.tag.title + " - " + audiofile.tag.artist[:30] + "...")
                            HomeWindow.Element('musicPlayerPanel_songTitleQueue').Update(audiofile.tag.title + " - " + audiofile.tag.artist[:30] + "...")
                    else:
                        HomeWindow.Element('musicPlayerPanel_songTitleLyrics').Update(audiofile.tag.title + " - " + audiofile.tag.artist)
                        HomeWindow.Element('musicPlayerPanel_songTitleQueue').Update(audiofile.tag.title + " - " + audiofile.tag.artist)
                except:
                    print(f"[ERROR]: Failed to load metadata from Music Player song")
                    popupMessage("Music Player", "Metadata Failed to load from song.", "error", 5000)
                ## Start Playing Song
                sliderPos = 0
                if len(musicPlayerQueue) > 0 and musicPlayerQueueCurrentIndex+1 < len(musicPlayerQueue): HomeWindow['musicPlayerPanel_queueListbox'].update([os.path.splitext(os.path.basename(file_path))[0] for file_path in musicPlayerQueue[musicPlayerQueueCurrentIndex+1:]])
                else: HomeWindow['musicPlayerPanel_queueListbox'].update([])
                if musicPlayerQueueCurrentState != "stop": musicPlayerQueueCurrentState = "play"    
                mixer.music.load(musicPlayerQueue[musicPlayerQueueCurrentIndex])
                HomeWindow.Element('musicPlayerPanel_playButton').update(image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\pause.png')
                if musicPlayerQueue[musicPlayerQueueCurrentIndex].endswith('.mp3'):
                    audio = MP3(musicPlayerQueue[musicPlayerQueueCurrentIndex])
                elif musicPlayerQueue[musicPlayerQueueCurrentIndex].endswith('.wav'):
                    audio = WAVE(musicPlayerQueue[musicPlayerQueueCurrentIndex])
                HomeWindow['musicPlayerPanel_timeSlider'].update(range=(0, int(audio.info.length)), value=0)
                HomeWindow.Element('musicPlayerPanel_endTime').update(f"{int(audio.info.length // 60)}:{int(audio.info.length % 60)}")
                HomeWindow['musicPlayerPanel_startTime'].update(f"0:00")
                mixer.music.play()
                if musicPlayerQueueCurrentState == "stop":
                    mixer.music.pause()
                    musicPlayerQueueCurrentState = "pause"
                    HomeWindow.Element('musicPlayerPanel_playButton').update(image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\play.png')
            if event == 'musicPlayerPanel_playButton' and len(musicPlayerQueue) > 0: ## Play / Pause Button
                if musicPlayerQueueCurrentState == "pause": ## play
                    mixer.music.unpause()
                    HomeWindow.Element('musicPlayerPanel_playButton').update(image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\pause.png')
                    musicPlayerQueueCurrentState = "play"
                else: ## Pause
                    mixer.music.pause()
                    HomeWindow.Element('musicPlayerPanel_playButton').update(image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\play.png')
                    musicPlayerQueueCurrentState = "pause"
            elif event == 'musicPlayerPanel_rewindButton' and len(musicPlayerQueue) > 0: ## Rewind Button
                sliderPos = 0
                if musicPlayerQueueCurrentIndex > 0: musicPlayerQueueCurrentIndex = musicPlayerQueueCurrentIndex - 1
                else: mixer.music.play()
            elif event == 'musicPlayerPanel_forwardButton' and len(musicPlayerQueue) > 0: ## Forward Button
                sliderPos = 0
                if musicPlayerQueueCurrentIndex < len(musicPlayerQueue) - 1: musicPlayerQueueCurrentIndex = musicPlayerQueueCurrentIndex + 1
                elif musicPlayerLoop and len(musicPlayerQueue) > 1: musicPlayerQueueCurrentIndex = 0
                else:
                    musicPlayerQueueCurrentIndex = 0
                    if musicPlayerLoop == False:
                        musicPlayerQueueCurrentState = "stop"
                        mixer.music.pause()
                        HomeWindow['musicPlayerPanel_timeSlider'].update(range=(0, int(audio.info.length)), value=0)
                        HomeWindow['musicPlayerPanel_startTime'].update(f"0:00")
                        HomeWindow.Element('musicPlayerPanel_playButton').update(image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\play.png')
                    else: mixer.music.play()
            elif event == 'musicPlayerPanel_searchButtonPlayer' and len(musicPlayerQueue) > 0: geniusMusicSearch(audiofile.tag.title + " " + audiofile.tag.artist, False) ## Music Search Button
            elif event == 'musicPlayerPanel_shuffleQueue': ## Shuffle Queue Button
                if musicPlayerShuffle:
                    part1 = musicPlayerQueue[:musicPlayerQueueCurrentIndex+1]
                    part2 = musicPlayerQueueCopy[musicPlayerQueueCurrentIndex+1:]
                    musicPlayerQueue = part1 + part2
                    musicPlayerShuffle = False
                    HomeWindow['musicPlayerPanel_shuffleQueue'].update(button_color='#2B475D')
                else:
                    musicPlayerQueueCopy = musicPlayerQueue
                    if musicPlayerQueueCurrentIndex < len(musicPlayerQueue)-1:
                        part1 = musicPlayerQueue[:musicPlayerQueueCurrentIndex+1]
                        part2 = musicPlayerQueue[musicPlayerQueueCurrentIndex+1:]
                        random.shuffle(part2)
                        musicPlayerQueue = part1 + part2
                    musicPlayerShuffle = True
                    HomeWindow['musicPlayerPanel_shuffleQueue'].update(button_color='blue')
                HomeWindow['musicPlayerPanel_queueListbox'].update([os.path.splitext(os.path.basename(file_path))[0] for file_path in musicPlayerQueue[musicPlayerQueueCurrentIndex+1:]])
            elif event == 'musicPlayerPanel_loopQueue': ## Loop Queue Button
                if musicPlayerLoop:
                    musicPlayerLoop = False
                    HomeWindow['musicPlayerPanel_loopQueue'].update(button_color='#2B475D')
                else:
                    musicPlayerLoop = True
                    HomeWindow['musicPlayerPanel_loopQueue'].update(button_color='blue')
            elif event == 'musicPlayerPanel_lyricsPage': ## Open / Close Lyrics Panel
                if musicPlayerPage == "player":
                    musicPlayerPage = "lyrics"
                    HomeWindow['musicPlayerPanel_lyricsPage'].update(button_color='blue')
                    HomeWindow['musicPlayerPanel_playerPanel'].update(visible=False)
                    HomeWindow['musicPlayerPanel_artworkPanel'].update(visible=False)
                    HomeWindow['musicPlayerPanel_lyricsPanel'].update(visible=True)
                    HomeWindow['musicPlayerPanel_artworkPanel'].update(visible=True)
                elif musicPlayerPage == "lyrics":
                    musicPlayerPage = "player"
                    HomeWindow['musicPlayerPanel_lyricsPage'].update(button_color='#2B475D')
                    HomeWindow['musicPlayerPanel_lyricsPanel'].update(visible=False)
                    HomeWindow['musicPlayerPanel_artworkPanel'].update(visible=False)
                    HomeWindow['musicPlayerPanel_playerPanel'].update(visible=True)
                    HomeWindow['musicPlayerPanel_artworkPanel'].update(visible=True)
                elif musicPlayerPage == "queue":
                    musicPlayerPage = "lyrics"
                    HomeWindow['musicPlayerPanel_lyricsPage'].update(button_color='blue')
                    HomeWindow['musicPlayerPanel_queuePage'].update(button_color='#2B475D')
                    HomeWindow['musicPlayerPanel_queuePanel'].update(visible=False)
                    HomeWindow['musicPlayerPanel_artworkPanel'].update(visible=False)
                    HomeWindow['musicPlayerPanel_lyricsPanel'].update(visible=True)
                    HomeWindow['musicPlayerPanel_artworkPanel'].update(visible=True)
            elif event == 'musicPlayerPanel_queuePage': ## Open / Close Queue Panel
                if musicPlayerPage == "player":
                    musicPlayerPage = "queue"
                    HomeWindow['musicPlayerPanel_queuePage'].update(button_color='blue')
                    HomeWindow['musicPlayerPanel_playerPanel'].update(visible=False)
                    HomeWindow['musicPlayerPanel_artworkPanel'].update(visible=False)
                    HomeWindow['musicPlayerPanel_queuePanel'].update(visible=True)
                    HomeWindow['musicPlayerPanel_artworkPanel'].update(visible=True)
                elif musicPlayerPage == "queue":
                    musicPlayerPage = "player"
                    HomeWindow['musicPlayerPanel_queuePage'].update(button_color='#2B475D')
                    HomeWindow['musicPlayerPanel_queuePanel'].update(visible=False)
                    HomeWindow['musicPlayerPanel_artworkPanel'].update(visible=False)
                    HomeWindow['musicPlayerPanel_playerPanel'].update(visible=True)
                    HomeWindow['musicPlayerPanel_artworkPanel'].update(visible=True)
                elif musicPlayerPage == "lyrics":
                    musicPlayerPage = "queue"
                    HomeWindow['musicPlayerPanel_lyricsPage'].update(button_color='#2B475D')
                    HomeWindow['musicPlayerPanel_queuePage'].update(button_color='Blue')
                    HomeWindow['musicPlayerPanel_lyricsPanel'].update(visible=False)
                    HomeWindow['musicPlayerPanel_artworkPanel'].update(visible=False)
                    HomeWindow['musicPlayerPanel_queuePanel'].update(visible=True)
                    HomeWindow['musicPlayerPanel_artworkPanel'].update(visible=True)
            elif event == 'musicPlayerPanel_timeSlider' and len(musicPlayerQueue) > 0: ## Change Part of Song
                if musicPlayerQueueCurrentState == "pause": ## play
                    mixer.music.unpause()
                    HomeWindow.Element('musicPlayerPanel_playButton').update(image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\pause.png')
                    musicPlayerQueueCurrentState = "play"
                sliderPos = values['musicPlayerPanel_timeSlider']
                mixer.music.play(start=values['musicPlayerPanel_timeSlider'])
            elif event == 'musicPlayerPanel_addSongButton' or event == 'musicPlayerPanel_addSongButtonPlayer': ## Add Song to Queue
                if event == 'musicPlayerPanel_addSongButtonPlayer': musicPlayerQueue = []
                fileBrowserWindow = sg.Window("Song Selector", [[sg.Text("Song File:")], [sg.Input(key="fileLocation"), sg.FilesBrowse(file_types=(("Music Files", "*.mp3;*.wav;"), ("All Files", "*.*")))], [sg.Push(), sg.Button("OK"), sg.Push()]], no_titlebar=True, keep_on_top=True, finalize=True)
                while True:
                    event, values = fileBrowserWindow.read(timeout=10)
                    try: fileBrowserWindow.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - fileBrowserWindow.size[0] // 2, HomeWindow.TKroot.winfo_y() + HomeWindow.TKroot.winfo_height() // 2 - fileBrowserWindow.size[1] // 2)
                    except: pass
                    if event == sg.WINDOW_CLOSED or event == "OK":
                        if values["fileLocation"] != "":
                            for item in values["fileLocation"].split(";"):
                                if item not in musicPlayerQueue: musicPlayerQueue.append(item)
                            HomeWindow['musicPlayerPanel_queueListbox'].update([os.path.splitext(os.path.basename(file_path))[0] for file_path in musicPlayerQueue[musicPlayerQueueCurrentIndex:]])
                        fileBrowserWindow.close()
                        break
            elif event == 'musicPlayerPanel_upQueueButton': ## Queue Move Up
                selectedSong = values['musicPlayerPanel_queueListbox']
                if selectedSong:
                    selectedSongIndex = [os.path.splitext(os.path.basename(file_path))[0] for file_path in musicPlayerQueue].index(selectedSong[0])
                    if selectedSongIndex > 0 and selectedSongIndex > musicPlayerQueueCurrentIndex+1:
                        musicPlayerQueue[selectedSongIndex], musicPlayerQueue[selectedSongIndex - 1] = musicPlayerQueue[selectedSongIndex - 1], musicPlayerQueue[selectedSongIndex]
                        HomeWindow['musicPlayerPanel_queueListbox'].update([os.path.splitext(os.path.basename(song))[0] for song in musicPlayerQueue[musicPlayerQueueCurrentIndex+1:]])
                        HomeWindow['musicPlayerPanel_queueListbox'].update(set_to_index=selectedSongIndex-2)
            elif event == 'musicPlayerPanel_downQueueButton': ## Queue Move Down
                selectedSong = values['musicPlayerPanel_queueListbox']
                if selectedSong:
                    selectedSongIndex = [os.path.splitext(os.path.basename(file_path))[0] for file_path in musicPlayerQueue].index(selectedSong[0])
                    if selectedSongIndex > 0 and selectedSongIndex < len(musicPlayerQueue)-1:
                        musicPlayerQueue[selectedSongIndex], musicPlayerQueue[selectedSongIndex + 1] = musicPlayerQueue[selectedSongIndex + 1], musicPlayerQueue[selectedSongIndex]
                        HomeWindow['musicPlayerPanel_queueListbox'].update([os.path.splitext(os.path.basename(song))[0] for song in musicPlayerQueue[musicPlayerQueueCurrentIndex+1:]])
                        HomeWindow['musicPlayerPanel_queueListbox'].update(set_to_index=selectedSongIndex)
            elif event == 'musicPlayerPanel_trashQueueButton' or values['musicPlayerPanel_queueListbox'] and event == 'Delete': ## Remove Song Queue and Right Click - Delete
                selectedSong = values['musicPlayerPanel_queueListbox']
                if selectedSong:
                    selectedSongIndex = [os.path.splitext(os.path.basename(file_path))[0] for file_path in musicPlayerQueue].index(selectedSong[0])
                    if selectedSongIndex > 0:
                        del musicPlayerQueue[selectedSongIndex]
                        HomeWindow['musicPlayerPanel_queueListbox'].update([os.path.splitext(os.path.basename(song))[0] for song in musicPlayerQueue[musicPlayerQueueCurrentIndex+1:]])
                        HomeWindow['musicPlayerPanel_queueListbox'].update(set_to_index=selectedSongIndex-1)
            elif values['musicPlayerPanel_queueListbox'] and event == 'Play Next': ## Right Click - Play Next
                selectedSong = values['musicPlayerPanel_queueListbox']
                if selectedSong:
                    selectedSongIndex = [os.path.splitext(os.path.basename(file_path))[0] for file_path in musicPlayerQueue].index(selectedSong[0])
                    if selectedSongIndex > 0 and selectedSongIndex > musicPlayerQueueCurrentIndex+1:
                        song = musicPlayerQueue.pop(selectedSongIndex)
                        musicPlayerQueue.insert(musicPlayerQueueCurrentIndex+1, song)
                        HomeWindow['musicPlayerPanel_queueListbox'].update([os.path.splitext(os.path.basename(song))[0] for song in musicPlayerQueue[musicPlayerQueueCurrentIndex+1:]])
                        HomeWindow['musicPlayerPanel_queueListbox'].update(set_to_index=musicPlayerQueueCurrentIndex)
## Internet Status Changes
        HomeWindow['versionTextHomeBottom'].update(f"{platform.system()} | {softwareVersion} | {systemBuild} | {'Online' if wifiStatus else 'Offline'}")
            
## Software Tools

def saveProfanityEngine(profanityEngineDefinitions):
    HomeWindow.Element('profanityEnginePanel_searchInput').Update("") ## Clear Search
    HomeWindow.Element('profanityEnginePanel_definitionsList').Update([item.replace("~", "'") for item in profanityEngineDefinitions]) ## Update List
    try: ## Save to File
        with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Profanity Engine User Definitions.txt"), 'w') as file:
            for item in profanityEngineDefinitions: file.write(item.replace("'", "~") + '\n')
    except: print(f"[ERROR]: Failed to save Profanity Engine Definitions: {profanityEngineDefinitions}")

def savingSettings(setting, argument):
    global userSettingsData
    try:
        with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Settings.json"), 'r') as file: userSettingsData = json.load(file)
        userSettingsData[setting] = argument
        with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Settings.json"), 'w') as file: json.dump(userSettingsData, file)
    except:
        print(f"[ERROR]: Failed to save setting: {setting}, argument: {argument}")
        popupMessage("Settings", "Unable to save settings.", "error")

def loadingScreen(functionLoader, homeHasLaunched, agr1=False, arg2=False, arg3=False, arg4=False, arg5=False):
    global loadingStatus, metadataInfo
    if homeHasLaunched:
        loadingPopup, loadingStatus, metadataInfo = sg.Window("", [[sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", background_color='#1b2838', key='loadingGIFImage')], [sg.Text("Loading...", font='Any 16', background_color='#1b2838', key='loadingScreenText')]], background_color='#1b2838', element_justification='c', no_titlebar=True, keep_on_top=True, finalize=True), "Start", {}
        loadingPopup.hide()
        loadingPopup.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - loadingPopup.size[0] // 2, HomeWindow.TKroot.winfo_y() + HomeWindow.TKroot.winfo_height() // 2 - loadingPopup.size[1] // 2)
        loadingPopup.un_hide()
    else: loadingPopup, loadingStatus, metadataInfo = sg.Window("", [[sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", background_color='#1b2838', key='loadingGIFImage')], [sg.Text("Downloading Billboard List...", font='Any 16', background_color='#1b2838', key='loadingScreenText')]], background_color='#1b2838', element_justification='c', no_titlebar=True, keep_on_top=True), "Start", {}
    while True:
        event, values = loadingPopup.read(timeout=10)
        if homeHasLaunched: loadingPopup.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - loadingPopup.size[0] // 2, HomeWindow.TKroot.winfo_y() + HomeWindow.TKroot.winfo_height() // 2 - loadingPopup.size[1] // 2) ## Fix Position
        try: loadingPopup["loadingGIFImage"].UpdateAnimation(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", time_between_frames=30) ## Load Loading GIF
        except: pass
        loadingPopup["loadingScreenText"].update(loadingStatus)
        if event == sg.WIN_CLOSED:
            thisSystem = psutil.Process(os.getpid()) ## Close Program
            thisSystem.terminate()
        elif loadingStatus == "Start":
            if functionLoader == "Billboard_List_Download":
                downloadBillboardSongsThread = threading.Thread(name="downloadBillboardSongs", target=downloadBillboardSongs, args=())
                downloadBillboardSongsThread.start()
                loadingStatus = "Downloading Billboard List..."  
            elif functionLoader == "YouTube_Downloader":
                youtubeDownloaderThread = threading.Thread(name="downloadYouTube", target=downloadYouTube, args=(agr1, arg2, arg3, arg4, arg5,))
                youtubeDownloaderThread.start()
                loadingStatus = "Downloading YouTube Video..."
            elif functionLoader == "Music_Downloader":
                musicDownloaderThread = threading.Thread(name="downloadAudio", target=downloadAudio, args=(agr1, arg2,))
                musicDownloaderThread.start()
                loadingStatus = "Downloading Song..."
        elif loadingStatus == "Failed_YouTubeDownloader": ## YouTube Downloader Failed
            loadingPopup.close()
            popupMessage("YouTube Downloader", "The video download failed.\t\t\tPlease try again later.", "error")
            break
        elif loadingStatus == "Failed_MusicDownloaderYouTube": ## Music Downloader (YouTube Download) Failed
            loadingPopup.close()
            popupMessage("Music Downloader", "The audio download failed.\t\t\tPlease try again later.", "error")
            break
        elif "Done" in loadingStatus:
            loadingPopup.close()
            if loadingStatus == "Done_YouTubeDownloader": popupMessage("YouTube Downloader", "The video has been downloadeded successfully.", "success")
            elif loadingStatus == "Done_MusicDownloader":
                metadataInfo["metadataBurnLocation"], metadataInfo["metadataBurnLyrics"], metadataInfo["metadataMultipleArtistsValue"], metadataInfo["metadataNameChangeValue"] = audioSavedPath, arg3, arg4, arg5
                geniusMusicSearchList(youtubeTitle, "downloader")
                try: HomeWindow.Element('musicSearchPanel_songSearchInput').Update("")
                except: pass
                popupMessage("Music Downloader", "The song has been downloadeded successfully.", "success")
            break

def popupMessage(popupMessageTitle, popupMessageText, popupMessageIcon, popupTimer=0):
    popupMessageText = '\n'.join((textwrap.TextWrapper(width=45, max_lines=6, placeholder='...')).wrap(popupMessageText))
    if "New Update Available" in popupMessageTitle: alpha, messagePopup, timeOpened = 0.9, sg.Window("", [[sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\Popup icons\\" + popupMessageIcon + ".png", background_color='#1b2838', key='loadingGIFImage')], [sg.Text(popupMessageTitle, font='Any 24 bold', background_color='#1b2838', key='messagePopupTitle')], [sg.Text(popupMessageText, font='Any 13', background_color='#1b2838', key='messagePopupMessage')], [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\Popup icons\\yes.png', border_width=0, button_color='#1B2838', key='messagePopupExitButton', tooltip="Install Update Now"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\Popup icons\\nextWeek.png', border_width=0, button_color='#1B2838', key='messagePopupRemindButton', tooltip="Remind Me Next Week"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\Popup icons\\no.png', border_width=0, button_color='#1B2838', key='messagePopupCancelButton', tooltip="Don't Install Update")]], background_color='#1b2838', element_justification='c', text_justification='c', no_titlebar=True, keep_on_top=True, finalize=True), 0
    elif "Confirmation" in popupMessageTitle: alpha, messagePopup, timeOpened = 0.9, sg.Window("", [[sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\Popup icons\\" + popupMessageIcon + ".png", background_color='#1b2838', key='loadingGIFImage')], [sg.Text(popupMessageTitle, font='Any 24 bold', background_color='#1b2838', key='messagePopupTitle')], [sg.Text(popupMessageText, font='Any 13', background_color='#1b2838', key='messagePopupMessage')], [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\Popup icons\\yes.png', border_width=0, button_color='#1B2838', key='messagePopupExitButton', tooltip="Accept"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\Popup icons\\no.png', border_width=0, button_color='#1B2838', key='messagePopupCancelButton', tooltip="Cancel")]], background_color='#1b2838', element_justification='c', text_justification='c', no_titlebar=True, keep_on_top=True, finalize=True), 0
    else: alpha, messagePopup, timeOpened = 0.9, sg.Window("", [[sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\Popup icons\\" + popupMessageIcon + ".png", background_color='#1b2838', key='loadingGIFImage')], [sg.Text(popupMessageTitle, font='Any 24 bold', background_color='#1b2838', key='messagePopupTitle')], [sg.Text(popupMessageText, font='Any 13', background_color='#1b2838', key='messagePopupMessage')], [sg.Button("OK", font=('Any 12'), button_color=('white','#5A6E80'), key='messagePopupExitButton')]], background_color='#1b2838', element_justification='c', text_justification='c', no_titlebar=True, keep_on_top=True, finalize=True), 0
    messagePopup.hide()
    try: messagePopup.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - messagePopup.size[0] // 2, HomeWindow.TKroot.winfo_y() + HomeWindow.TKroot.winfo_height() // 2 - messagePopup.size[1] // 2)
    except: pass
    messagePopup.un_hide()
    messagePopup.force_focus()
    ## Window Shortcuts
    messagePopup.bind('<FocusOut>', '_FocusOut')        ## Window Focus Out
    messagePopup.bind('<Delete>', '_Delete')            ## Close Window shortcut
    messagePopup.bind('<Return>', '_Enter')             ## Enter Window shortcut
    messagePopup['messagePopupExitButton'].Widget.config(cursor="hand2") ## Hover icons
    while True:
        event, values = messagePopup.read(timeout=100)
        try: messagePopup.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - messagePopup.size[0] // 2, HomeWindow.TKroot.winfo_y() + HomeWindow.TKroot.winfo_height() // 2 - messagePopup.size[1] // 2)
        except: pass
        if messagePopup.CurrentLocation()[1] < 200: messagePopup.move(messagePopup.CurrentLocation()[0], 100) ## Fix Over Top
        if event == sg.WIN_CLOSED or event == 'messagePopupExitButton' or (event == '_Delete' and "Confirmation" not in popupMessageTitle) or (event == '_Enter') or (event == '_FocusOut' and popupTimer != 0 and timeOpened >= 100):
            messagePopup.close()
            return True
        elif event == 'messagePopupRemindButton':
            messagePopup.close()
            return "Week"
        elif event == 'messagePopupCancelButton' or (event == '_Delete' and "Confirmation" in popupMessageTitle) or (event == '_Delete' and "New Update Available" in popupMessageTitle):
            messagePopup.close()
            return False
        elif popupTimer != 0 and timeOpened >= popupTimer: ## Fade Out Window (3000)
            for i in range(int(alpha*100),1,-1): ## Start Fade Out
                try: messagePopup.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - messagePopup.size[0] // 2, HomeWindow.TKroot.winfo_y() + HomeWindow.TKroot.winfo_height() // 2 - messagePopup.size[1] // 2)
                except: pass
                if messagePopup.CurrentLocation()[1] < 200: messagePopup.move(messagePopup.CurrentLocation()[0], 100) ## Fix Over Top
                messagePopup.set_alpha(i/150)
                event, values = messagePopup.read(timeout=20)
                if event != sg.TIMEOUT_KEY: break
            messagePopup.close()
            break
        timeOpened += 100

## Music Tools

def downloadYouTubeOLD(youtubeLink, downloadLocation, audioFileNeeded, videoFileNeeded, renameFile):
    global audioSavedPath, loadingStatus, youtubeTitle
    try:
        print(f"[INFO]: Downloading YouTube: {youtubeLink}, downloadLocation: {downloadLocation}, ({audioFileNeeded}, {videoFileNeeded}, {renameFile})")
        stream = YouTube(youtubeLink).streams.filter(file_extension="mp4").get_highest_resolution()
        youtubeTitle = stream.default_filename
        if os.path.exists(os.path.join(downloadLocation, youtubeTitle)) or os.path.exists(os.path.join(downloadLocation, youtubeTitle[:youtubeTitle.rfind(".mp4")] + ".mp3")): ## Check if the file already exists
            base, ext = os.path.splitext(youtubeTitle)
            index = 1
            while os.path.exists(os.path.join(downloadLocation, f"{base} ({index}){ext}")) or os.path.exists(os.path.join(downloadLocation, f"{base} ({index}).mp3")): index += 1
            youtubeTitle = f"{base} ({index}){ext}"
        stream.download(downloadLocation, filename=youtubeTitle) ## Download the video
        youtubeTitle = youtubeTitle[:youtubeTitle.rfind(".mp4")]
    except Exception as error:
        try: print(f"[ERROR]: Retrieved title: {youtubeTitle}")
        except: print(f"[ERROR]: Retrieved title: {error}")
        loadingStatus = "Failed_YouTubeDownloader"
        return
    if audioFileNeeded: ## Convert MP4 Video to MP3 Audio
        audioSavedPath, loadingStatus = downloadLocation + "\\" + youtubeTitle + ".mp3", "Downloading Audio File..." ## MP3 File Name
        try: videoFile = VideoFileClip(downloadLocation + "\\" + youtubeTitle + ".mp4")
        except:
            print(f"[ERROR]: Failed to convert to .MP3")
            loadingStatus = "Failed_YouTubeDownloader"
            return
        audioFile = videoFile.audio
        audioFile.write_audiofile(audioSavedPath)
        audioFile.close()
        videoFile.close()
        if renameFile != False: ## Rename MP3 File
            loadingStatus = "Renaming Audio File..."
            try: os.rename(audioSavedPath, audioSavedPath.replace(audioSavedPath.rsplit('\\', 1)[1], "") + "\\" + renameFile + "." + audioSavedPath.rsplit('.', 1)[1]) ## Rename MP3 to Chosen Name
            except: print(f"[ERROR]: Failed to rename to {renameFile} for audio file")
    if renameFile != False: ## Rename MP4 File
        loadingStatus = "Renaming Video File..."
        videoSavedLocation = downloadLocation + "\\" + youtubeTitle + ".mp4"
        try: os.rename(videoSavedLocation, videoSavedLocation.replace(videoSavedLocation.rsplit('\\', 1)[1], "") + "\\" + renameFile + "." + videoSavedLocation.rsplit('.', 1)[1]) ## Rename MP4 to Chosen Name
        except: print(f"[ERROR]: Failed to rename to {renameFile} for video file")
    if videoFileNeeded == False: ## Delete video file if audio is only needed
        try: os.remove(downloadLocation + "\\" + youtubeTitle + ".mp4")
        except: print(f"[ERROR]: Failed to remove to {downloadLocation} + \\ + {youtubeTitle}, video file")
    loadingStatus = "Done_YouTubeDownloader"



def generate_unique_filename(filepath):
    """
    Generate a unique file name by appending a numeric suffix if the file already exists.
    """
    if not os.path.exists(filepath):
        return filepath

    base, ext = os.path.splitext(filepath)
    counter = 1
    while os.path.exists(f"{base} ({counter}){ext}"):
        counter += 1
    return f"{base} ({counter}){ext}"

def downloadYouTube(youtubeLink, downloadLocation, audioFileNeeded, videoFileNeeded, renameFile):
    global audioSavedPath, loadingStatus, youtubeTitle
    try:
        print(f"[INFO]: Downloading YouTube: {youtubeLink}, downloadLocation: {downloadLocation}, ({audioFileNeeded}, {videoFileNeeded}, {renameFile})")
        with yt_dlp.YoutubeDL({'format': 'best[ext=mp4]', 'outtmpl': os.path.join(downloadLocation, '%(title)s.%(ext)s'), 'noplaylist': True,}) as ydl:
            info_dict = ydl.extract_info(youtubeLink, download=True)
            youtubeTitle = ydl.prepare_filename(info_dict)
        youtubeTitle = os.path.basename(youtubeTitle)
        videoSavedLocation = os.path.join(downloadLocation, youtubeTitle)

        # Handle video file naming
        if renameFile:
            new_video_path = os.path.join(downloadLocation, f"{renameFile}.mp4")
            if os.path.exists(new_video_path):
                new_video_path = generate_unique_filename(new_video_path)
        else:
            new_video_path = videoSavedLocation
            if os.path.exists(new_video_path):
                new_video_path = generate_unique_filename(new_video_path)
        
        os.rename(videoSavedLocation, new_video_path)
        youtubeTitle = os.path.basename(new_video_path).replace('.mp4', '')

    except Exception as error:
        try:
            print(f"[ERROR]: Retrieved title: {youtubeTitle}")
        except:
            print(f"[ERROR]: MAJOR ERROR: {error}")
        loadingStatus = "Failed_YouTubeDownloader"
        return

    if audioFileNeeded:  # Convert MP4 Video to MP3 Audio
        audioSavedPath = os.path.join(downloadLocation, youtubeTitle + ".mp3")
        loadingStatus = "Downloading Audio File..."  # MP3 File Name
        try:
            videoFile = VideoFileClip(new_video_path)
        except:
            print(f"[ERROR]: Failed to convert to .MP3")
            loadingStatus = "Failed_YouTubeDownloader"
            return
        audioFile = videoFile.audio
        audioFile.write_audiofile(audioSavedPath)
        audioFile.close()
        videoFile.close()

        # Handle audio file renaming if necessary
        if renameFile:
            new_audio_path = os.path.join(downloadLocation, f"{renameFile}.mp3")
            if os.path.exists(new_audio_path):
                new_audio_path = generate_unique_filename(new_audio_path)
            os.rename(audioSavedPath, new_audio_path)
            audioSavedPath = new_audio_path
        else:
            if os.path.exists(audioSavedPath):
                new_audio_path = generate_unique_filename(audioSavedPath)
                os.rename(audioSavedPath, new_audio_path)
                audioSavedPath = new_audio_path

    if not videoFileNeeded:  # Delete video file if only audio is needed
        try:
            os.remove(new_video_path)
        except:
            print(f"[ERROR]: Failed to remove {new_video_path}, video file")
    
    loadingStatus = "Done_YouTubeDownloader"



def downloadAudio(youtubeLink, downloadLocation):
    global audioSavedPath, loadingStatus, youtubeTitle
    try:
        print(f"[INFO]: Downloading Audio: {youtubeLink}, downloadLocation: {downloadLocation}")
        stream = YouTube(youtubeLink).streams.filter(file_extension="mp4").get_highest_resolution()
        youtubeTitle = stream.default_filename
        if os.path.exists(os.path.join(downloadLocation, youtubeTitle)) or os.path.exists(os.path.join(downloadLocation, youtubeTitle[:youtubeTitle.rfind(".mp4")] + ".mp3")): ## Check if the file already exists
            base, ext = os.path.splitext(youtubeTitle)
            index = 1
            while os.path.exists(os.path.join(downloadLocation, f"{base} ({index}){ext}")) or os.path.exists(os.path.join(downloadLocation, f"{base} ({index}).mp3")): index += 1
            youtubeTitle = f"{base} ({index}){ext}"
        stream.download(downloadLocation, filename=youtubeTitle) ## Download the video
        youtubeTitle = youtubeTitle[:youtubeTitle.rfind(".mp4")]
    except Exception as error:
        try: print(f"[ERROR]: Retrieved title: {youtubeTitle}")
        except: print(f"[ERROR]: Retrieved title: {error}")
        loadingStatus = "Failed_MusicDownloaderYouTube"
        return
    audioSavedPath, loadingStatus = downloadLocation + "\\" + youtubeTitle + ".mp3", "Downloading Audio File..." ## MP3 File Name
    try: videoFile = VideoFileClip(downloadLocation + "\\" + youtubeTitle + ".mp4")
    except:
        print(f"[ERROR]: Failed to convert to .MP3")
        loadingStatus = "Failed_MusicDownloaderYouTube"
        return
    audioFile = videoFile.audio
    audioFile.write_audiofile(audioSavedPath)
    audioFile.close()
    videoFile.close()
    try: os.remove(downloadLocation + "\\" + youtubeTitle + ".mp4") ## Delete video file
    except: print(f"[ERROR]: Failed to remove to {downloadLocation} + \\ + {youtubeTitle}, video file")
    ## Remove extra characters from YouTube title for Music Search
    youtubeTitle = re.sub(r'\([^)]*\)', '', youtubeTitle)
    loadingStatus = "Done_MusicDownloader"

def loadGeniusMusic(userInput, forceResult):
    global loadingAction, musicSearchResultData
    print(f"[INFO]: Music Search: {userInput}, forceResult: {forceResult}")
    artistSearch, goodResult, hitsFound, musicSearchResultData, resultCount = False, False, 1, {}, 0
    if forceResult != "refresh": ## Read from Cache
        try:
            with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Music Search", "Music Search Info", userInput.lower().replace(" ", "").rsplit('/', 1)[-1] + ".json"), 'r') as file:
                musicSearchResultData = json.load(file)
            if datetime.datetime.strptime(musicSearchResultData["geniusMusicSearchExpireDate"], '%Y-%m-%d') > datetime.datetime.now(): ## Cache Expired
                if musicSearchResultData["lyricsListFinal"] != None: musicSearchResultData["lyrics"] = "Cached"
                ## Look in Cache for Artwork
                pil_image = Image.open(str(os.getenv('APPDATA')) + "\\Oszust Industries\\Oszust OS Music Tools\\Cache\\Music Search\\Artworks\\" + str(musicSearchResultData["song_art_image_url"]).split(".com/",1)[1].split(".",1)[0] + ".png")
                png_bio = io.BytesIO()
                pil_image.save(png_bio, format="PNG")
                png_data = png_bio.getvalue()
                musicSearchResultData["png_data_location"] = str(os.getenv('APPDATA')) + "\\Oszust Industries\\Oszust OS Music Tools\\Cache\\Music Search\\Artworks\\" + str(musicSearchResultData["song_art_image_url"]).split(".com/",1)[1].split(".",1)[0] + ".png"
                musicSearchResultData["png_data"] = png_data
                loadingAction = "Search_Finished"
                return
            else: os.remove(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Music Search", "Music Search Info", userInput.lower().replace(" ", "").rsplit('/', 1)[-1] + ".json"))
        except: pass
    ## Load from Online
    if "genius.com" in userInput: userInput = userInput.split("https://genius.com/",1)[1].split("-lyrics",1)[0] ## Genius Website URL
    if "/songs/" in userInput: request = urllib.request.Request("http://api.genius.com" + userInput) ## Song ID Search
    else: request = urllib.request.Request("http://api.genius.com/search?q=" + urllib.request.quote(userInput.lower().replace(" by ", "-").replace("@","").replace(":","").split("-featuring")[0]) + "&lang=en&type=song&page=1")
    request.add_header("Authorization", "Bearer " + "ThgJU2pTawXV60l2g2jQXNEYT-b3MP7KDRd51BD-kLL7K5Eg8-UzrEGY96L3Z1c4")   
    request.add_header("User-Agent", "curl/7.9.8 (i686-pc-linux-gnu) libcurl 7.9.8 (OpenSSL 0.9.6b) (ipv6 enabled)")
    try: raw = (urllib.request.urlopen(request, timeout=10)).read()
    except Exception as Argument:
        if "Error 403" in str(Argument):
            print(f"[ERROR]: Music Search: Robot check failed")
            loadingAction = "Genius_Robot_Check"
            return
        else:
            print(f"[ERROR]: Music Search: Genius down")
            loadingAction = "Genius_Page_Down:" + str(Argument)
            return
    try:
        musicSearchApiBody = [result for result in (json.loads(raw)["response"]["hits"]) if "song" in result["type"] and not any(tag in result["result"]["title"].lower() for tag in ["instrumental", "radio edit", "slow", "sped", "version", "acapella", "acoustic", "log", "transcriptions"]) and not any(tag in result["result"]["artist_names"].lower() for tag in ["genius", "siriusxm", "fortnite"])]
        if len(musicSearchApiBody) > 0: musicSearchApiBodyPath = musicSearchApiBody[0]["result"]
    except: musicSearchApiBody, musicSearchApiBodyPath = json.loads(raw)["response"]["song"], json.loads(raw)["response"]["song"]
    hitsFound = len(musicSearchApiBody)
    if hitsFound == 0: ## Check if Result Found
        print(f"[ERROR]: Music Search: No results found")
        loadingAction = "No_Result_Found"
        return
    while goodResult == False:
        if artistSearch == False or str(musicSearchApiBodyPath["artist_names"]).replace("\u200b","").replace(" ", "-").split('(')[0].lower() == userInput: ## Check if Search is Artist
            if forceResult == False and str(musicSearchApiBodyPath["artist_names"]).replace(" ", "-").lower() == userInput.replace(" ", "-").lower(): ## Change to Artist Search
                print(f"[ERROR]: Music Search: Artist check detected")
                loadingAction = "Artist_Search"
                return
            ## Finish Normal Search
            try: musicSearchResultData["geniusMusicSearchArtists"] = str(musicSearchApiBodyPath["artist_names"]).replace("(Rock)", "") ## Song Artists
            except: ## No Results Left
                print(f"[ERROR]: Music Search: No results found")
                loadingAction = "No_Result_Found"
                return
            musicSearchResultData["geniusMusicSearchPrimeArtist"] = str(musicSearchApiBodyPath["primary_artist"]["name"]).split('(')[0] ## Song Main Artist
            musicSearchResultData["geniusMusicSearchDate"] = str(musicSearchApiBodyPath["release_date_for_display"]) ## Song Release Date
            if musicSearchResultData["geniusMusicSearchDate"] == "None": musicSearchResultData["geniusMusicSearchDate"] = None ## Fix Release Date if None Found
            musicSearchResultData["geniusMusicSearchSongNameInfo"] = str(musicSearchApiBodyPath["title_with_featured"]) ## Song Full Title
            musicSearchResultData["geniusMusicSearchArtistURL"] = str(musicSearchApiBodyPath["primary_artist"]["url"])
            musicSearchResultData["geniusMusicSearchGeniusURL"] = str(musicSearchApiBodyPath["url"]) ## Song Genius URL
            musicSearchResultData["geniusMusicSearchSongName"] = str(musicSearchApiBodyPath["title"]) ## Song Title
            ## Song Artwork
            try:
                geniusMusicSearchArtworkURL, musicSearchResultData["png_data_location"] = str(musicSearchApiBodyPath["song_art_image_url"]), None
                if "https://assets.genius.com/images/default_cover_image.png" in geniusMusicSearchArtworkURL: png_data = str(pathlib.Path(__file__).resolve().parent) + "\\data\\icons\\defaultMusicArtwork.png"
                else:
                    musicSearchResultData["song_art_image_url"] = geniusMusicSearchArtworkURL
                    try: ## Look in Cache for Artwork
                        pil_image = Image.open(str(os.getenv('APPDATA')) + "\\Oszust Industries\\Oszust OS Music Tools\\Cache\\Music Search\\Artworks\\" + str(musicSearchApiBodyPath["song_art_image_url"]).split(".com/",1)[1].split(".",1)[0] + ".png")
                        png_bio = io.BytesIO()
                        pil_image.save(png_bio, format="PNG")
                        png_data = png_bio.getvalue()
                        musicSearchResultData["png_data_location"] = str(os.getenv('APPDATA')) + "\\Oszust Industries\\Oszust OS Music Tools\\Cache\\Music Search\\Artworks\\" + str(musicSearchApiBodyPath["song_art_image_url"]).split(".com/",1)[1].split(".",1)[0] + ".png"
                    except: ## Download Artwork From Online
                        jpg_data = (cloudscraper.create_scraper(browser={"browser": "firefox", "platform": "windows", "mobile": False}).get(geniusMusicSearchArtworkURL).content)
                        pil_image = Image.open(io.BytesIO(jpg_data))
                        pil_image = pil_image.resize((200, 200)) ## Artwork Size
                        png_bio = io.BytesIO()
                        pil_image.save(png_bio, format="PNG")
                        try: ## Save Artwork to Cache PNG
                            pathlib.Path(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Music Search", "Artworks")).mkdir(parents=True, exist_ok=True) ## Create Music Cache Folder
                            with open(os.path.join(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Music Search", "Artworks"), str(musicSearchApiBodyPath["song_art_image_url"]).split(".com/", 1)[1].split(".", 1)[0] + ".png"), "wb") as f: f.write(png_bio.getbuffer())
                        except: pass
                        png_data = png_bio.getvalue()
                        musicSearchResultData["png_data_location"] = str(os.getenv('APPDATA')) + "\\Oszust Industries\\Oszust OS Music Tools\\Cache\\Music Search\\Artworks\\" + str(musicSearchApiBodyPath["song_art_image_url"]).split(".com/",1)[1].split(".",1)[0] + ".png"
            except: png_data = str(pathlib.Path(__file__).resolve().parent) + "\\data\\icons\\defaultMusicArtwork.png"
            ## Album, Album List, Genre, and Label
            try: html = bs4.BeautifulSoup((requests.get(musicSearchResultData["geniusMusicSearchGeniusURL"])).text, "html.parser") # Scrape the info from the HTML
            except:
                print(f"[ERROR]: Music Search: Genius down")
                loadingAction = "Genius_Page_Down"
                return
            if "Genius is down for a quick minute!" in str(html): ## Check if Genius's Service is Down
                print(f"[ERROR]: Music Search: Genius down")
                loadingAction = "Genius_Page_Down"
                return
            elif "make sure you're a human" in str(html): ## Check if Genius thinks Robot
                print(f"[ERROR]: Music Search: Robot check failed")
                loadingAction = "Genius_Robot_Check"
                return
            try: ## Album
                songScrapedInfo = html.select("div[class*=PrimaryAlbum__AlbumDetails]") ## Album Container
                musicSearchResultData["geniusMusicSearchAlbum"] = ((re.sub(r'<.+?>', '', str(songScrapedInfo))).replace("[", "").replace("]", "").replace("&amp;", "&")).split(" (")[0] ## Song Album
                if len(musicSearchResultData["geniusMusicSearchAlbum"]) == 0: musicSearchResultData["geniusMusicSearchAlbum"] = None ## No Album Found
            except: musicSearchResultData["geniusMusicSearchAlbum"] = None
            try: ## Album List
                songScrapedInfo, albumList, musicSearchResultData["geniusMusicSearchAlbumCurrent"] = str(html.select("div[class*=AlbumTracklist__Track]")).split('</a>'), [], None ## Song's Album List
                for song in songScrapedInfo:
                    match = re.search(r"<div class=\"AlbumTracklist__TrackNumber-sc-123giuo-3 epTVob\">(\d+)\. </div>" + musicSearchResultData["geniusMusicSearchSongNameInfo"], song)
                    if match: musicSearchResultData["geniusMusicSearchAlbumCurrent"] = match.group(1)
                    albumList.append(song)
                albumList = [(song.text).split(". ")[1].replace("\\u200b", "").replace("', '", "") for song in bs4.BeautifulSoup(str(albumList), 'html.parser').find_all('div', class_='AlbumTracklist__TrackName-sc-123giuo-2')]
                musicSearchResultData["geniusMusicSearchAlbumList"] = albumList
                musicSearchResultData["geniusMusicSearchAlbumLength"] = len(albumList)
                if len(albumList) <= 1:
                    musicSearchResultData["geniusMusicSearchAlbumCurrent"], musicSearchResultData["geniusMusicSearchAlbum"], musicSearchResultData["geniusMusicSearchAlbumList"] = 1, musicSearchResultData["geniusMusicSearchSongName"] + " - Single", None
            except: musicSearchResultData["geniusMusicSearchAlbumCurrent"], musicSearchResultData["geniusMusicSearchAlbumLength"], musicSearchResultData["geniusMusicSearchAlbumList"] = None, None, None
            try: ## Song's Genre
                infoList = str(html.select("div[class*=SongTags__Container]")).split('</a>') ## Song Genre Container
                musicSearchResultData["geniusMusicSearchGenre"] = (re.sub(r'<.+?>', '', str(infoList[0]))).replace("[", "").replace("]", "").replace("&amp;", "&") ## Song Genre
            except: musicSearchResultData["geniusMusicSearchGenre"] = None
            musicSearchResultData["geniusMusicSearchSongLength"] = None ## Song's Length
            try: ## Record Label
                songScrapedInfo = '<div class="SongInfo__Credit">Label</div><div>Republic Records</div>'
                labelsText = (re.search(r'<div.*?>Label</div><div>(.*?)</div>', songScrapedInfo)).group(1)
                musicSearchResultData["geniusMusicSearchLabels"] = [label.strip().replace(" & ", ",") for label in re.split(r',\s*', labelsText)]
                if len(musicSearchResultData["geniusMusicSearchLabels"]) > 3: musicSearchResultData["geniusMusicSearchLabels"] = musicSearchResultData["geniusMusicSearchLabels"][:3] ## Shorten Labels List
            except: musicSearchResultData["geniusMusicSearchLabels"] = None
            ## Song Lyrics
            if str(musicSearchApiBodyPath["lyrics_state"]).lower() == "complete":
                try:
                    lyrics, lyricsListFinal, count = html.select("div[class*=Lyrics__Container]"), [], 1
                    lyricsList = str(lyrics).split('<br/>')
                    for line in lyricsList:
                        oldLyricLine = line ## Save Unedited Lyric Line
                        if "[" not in line and "]" not in line and "{" not in line and "}" not in line: ## Test if Line has [] in it
                            if "InreadContainer__Container" in line: lyricsListFinal.append("")
                            line = re.sub(r'<.+?>', '', str(line))
                            if len(line) > 0 and line[0] == ",": ## Leftover Start Comma
                                lyricsListFinal.append("")
                                line = line[2:]
                            elif len(line) == 0 and len(lyricsListFinal) > 0 and lyricsListFinal[len(lyricsListFinal)-1] != "": lyricsListFinal.append("")
                            elif ("[" in line and line == lyricsList[0]) or ("[" not in line and len(line) > 0): lyricsListFinal.append(line.replace("</div>]", "").replace("]", "")) ## Line is Good
                            elif any(word in line.lower() for word in ["instrumental", "guitar solo", "mandolin solo", "produced by", "refrain"]) == False and any(word in lyricsList[lyricsList.index(oldLyricLine)-1].lower() for word in ["instrumental", "guitar solo", "mandolin solo", "refrain"]) == False and len(lyricsListFinal) > 1 and lyricsListFinal[len(lyricsListFinal)-1] != "": lyricsListFinal.append("") ## Replace Different [] Messages
                        elif line != str(lyricsList[0]) and "container" in line.lower() and any(word in line.lower() for word in ["instrumental", "guitar solo", "mandolin solo", "produced by", "refrain"]) == False and lyricsListFinal[len(lyricsListFinal)-1] != "": lyricsListFinal.append("") ## Fix for Two Transcribed With Space in Middle
                        elif (line == str(lyricsList[0]) or line == str(lyricsList[len(lyricsList)-1])) and any(word in line.lower() for word in ["verse", "verse 1", "intro", "instrumental", "guitar solo", "mandolin solo", "produced by", "chorus", "refrain"]) == False: ## Fix for First/Last Line
                            line = re.sub(r'<.+?>', '', str(line))
                            lyricsListFinal.append(line.replace("[", "").replace("]", "").replace("{", "").replace("}", ""))
                        count += 1
                except: lyrics = None ## Lyrics Failed to Load
            else: lyrics = None ## Lyrics Aren't Complete
            if lyrics == None: lyricsListFinal = None
            # Add the collected data to the dictionary
            musicSearchResultData["hitsFound"] = hitsFound
            musicSearchResultData["lyrics"] = lyrics
            musicSearchResultData["lyricsListFinal"] = lyricsListFinal
            musicSearchResultData["png_data"] = png_data
            musicSearchResultData["geniusMusicSearchCDCurrent"] = 1
            musicSearchResultData["geniusMusicSearchCDLength"] = 1
            if "/songs/" in userInput or musicSearchResultData["geniusMusicSearchArtists"].lower() not in ["spotify", "genius"]: goodResult = True ## Good Result Found
            elif resultCount < hitsFound: resultCount += 1 ## Move to Next Result
            else:
                print(f"[ERROR]: Music Search: No good result found")
                loadingAction = "No_Result_Found" ## No Good Result Found
                return
    try: ## Save Info to Cache
        musicSearchResultData["geniusMusicSearchExpireDate"] = str(datetime.date.today() + datetime.timedelta(days=10))
        pathlib.Path(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Music Search", "Music Search Info")).mkdir(parents=True, exist_ok=True) ## Create Music Search Info Cache Folder
        with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Music Search", "Music Search Info", userInput.lower().replace(" ", "").rsplit('/', 1)[-1] + ".json"), 'w') as file:
            json.dump({k: v for k, v in musicSearchResultData.items() if k not in ["lyrics", "png_data"]}, file)
    except: pass
    print(f"[INFO]: Music Search: Finished:")
    for key, value in musicSearchResultData.items():
        if key not in ["png_data", "lyrics"]: print(f"{key}: {re.sub('[^A-z0-9 -]', '', str(value)).replace(" ", " ")}")
    loadingAction = "Search_Finished"

def geniusMusicSearch(userInput, forceResult, searchType="search"):
    global appSelected, MusicSearchSongWindow, loadingAction, metadataInfo, musicSearchResultData
    ## Set Local Variables
    try: musicSub = userSettingsData["musicService"]
    except: musicSub = "Apple Music"
    ## Loading Screen
    loadingPopup, loadingAction = sg.Window("", [[sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", background_color='#1b2838', key='loadingGIFImage')]], background_color='#1b2838', element_justification='c', no_titlebar=True, keep_on_top=True, finalize=True), "Start"
    loadingPopup.hide()
    loadingPopup.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - loadingPopup.size[0] // 2, HomeWindow.TKroot.winfo_y() + HomeWindow.TKroot.winfo_height() // 2 - loadingPopup.size[1] // 2)
    loadingPopup.un_hide()
    loadingPopup["loadingGIFImage"].UpdateAnimation(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", time_between_frames=10) ## Load Loading GIF
    while True:
        event, values = loadingPopup.read(timeout=10)
        loadingPopup["loadingGIFImage"].UpdateAnimation(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", time_between_frames=30) ## Load Loading GIF
        ## Actions from Thread
        if loadingAction == "Start": ## Start Music Search Thread
            loadGeniusMusicThread = threading.Thread(name="loadGeniusMusic", target=loadGeniusMusic, args=(userInput,forceResult,))
            loadGeniusMusicThread.start()
            loadingAction = "Running"
        elif loadingAction == "No_Result_Found": ## No Music Search Result Found
            loadingPopup.close() ## Close Loading Popup
            popupMessage("No Search Result", "", "fail")
            return
        elif "Genius_Page_Down:" in loadingAction: ## Genius's Service is Down (Special Error)
            loadingPopup.close() ## Close Loading Popup
            popupMessage("Music Search Error", loadingAction.split("Genius_Page_Down:",1)[1] + "\t\t\t\t\tPlease try again later.", "error")
            return
        elif loadingAction == "Genius_Page_Down": ## Genius's Service is Down
            loadingPopup.close() ## Close Loading Popup
            popupMessage("Music Search Error", "Genius is currently unavailable.\t\t\t\t\tPlease try again later.", "error")
            return
        elif loadingAction == "Genius_Robot_Check": ## Genius is Checking Robot
            loadingPopup.close() ## Close Loading Popup
            popupMessage("Music Search Error", "Genius suspects automated activity.\t\t\t\t\tPlease disable your VPN.", "error")
            return
        elif loadingAction == "Artist_Search": ## Start Artist Search
            loadingPopup.close()
            geniusMusicSearchList(userInput)
            return
        elif loadingAction == "Search_Finished": ## Show Music Search Window
            loadingPopup.close()
            break
    ## Shorten Results
    musicSearchResultData["extendedSongInfo"] = [musicSearchResultData["geniusMusicSearchSongNameInfo"], musicSearchResultData["geniusMusicSearchArtists"], musicSearchResultData["geniusMusicSearchAlbum"]]
    if musicSearchResultData["geniusMusicSearchSongNameInfo"] != None and len(musicSearchResultData["geniusMusicSearchSongNameInfo"]) > 42: musicSearchResultData["geniusMusicSearchSongNameInfo"] = musicSearchResultData["geniusMusicSearchSongNameInfo"][:39] + "..." ## Shorten Song Name
    if musicSearchResultData["geniusMusicSearchArtists"] != None and len(musicSearchResultData["geniusMusicSearchArtists"]) > 45: musicSearchResultData["geniusMusicSearchArtists"] = musicSearchResultData["geniusMusicSearchArtists"][:42] + "..." ## Shorten Artists Names
    if musicSearchResultData["geniusMusicSearchAlbum"] != None and len(musicSearchResultData["geniusMusicSearchAlbum"]) > 45: musicSearchResultData["geniusMusicSearchAlbum"] = musicSearchResultData["geniusMusicSearchAlbum"][:42] + "..." ## Shorten Album Name
    ## Music Downloader Burner
    if searchType == "downloader":
        if metadataInfo["metadataBurnLyrics"] == False: musicSearchResultData["lyrics"] = None ## Don't Burn Lyrics
        if metadataInfo["metadataNameChangeValue"] != False: burnAudioData(metadataInfo["metadataBurnLocation"], False, metadataInfo["metadataMultipleArtistsValue"], metadataInfo["metadataNameChangeValue"], False)
        else: burnAudioData(metadataInfo["metadataBurnLocation"], False, metadataInfo["metadataMultipleArtistsValue"], musicSearchResultData["extendedSongInfo"][0], False)
        return
    ## Song Window
    if musicSearchResultData["lyrics"] != None: lyricsRightClickMenu = ['', ['Copy', 'Lookup Definition', 'Add to Profanity Engine', 'Remove from Profanity Engine']] ## Lyrics Right Click Menu - Profanity Engine
    else: lyricsRightClickMenu = ['', ['Copy', 'Lookup Definition']] ## Lyrics Right Click Menu - No Profanity Engine
    if musicSearchResultData["hitsFound"] > 1 and musicSearchResultData["geniusMusicSearchAlbumList"] != None: layout = [[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchMenu.png', border_width=0, button_color='#2B475D', key='musicSearchResultsMenu', tooltip="All Results"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\personSearch.png', border_width=0, button_color='#2B475D', key='musicSearchArtistResultsMenu', tooltip="Search Artist"), sg.Push(background_color='#2B475D'), sg.Text("Music Search Result", font='Any 20', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchAlbum.png', border_width=0, button_color='#2B475D', key='musicSearchAlbumResultsMenu', tooltip="Open Album"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchMP3Opener.png', border_width=0, button_color='#2B475D', key='downloadMetadataMp3Button', tooltip="Burn Metadata to MP3")]]
    elif musicSearchResultData["hitsFound"] > 1: layout = [[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchMenu.png', border_width=0, button_color='#2B475D', key='musicSearchResultsMenu', tooltip="All Results"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\personSearch.png', border_width=0, button_color='#2B475D', key='musicSearchArtistResultsMenu', tooltip="Search Artist"), sg.Push(background_color='#2B475D'), sg.Text("Music Search Result", font='Any 20', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchMP3Opener.png', border_width=0, button_color='#2B475D', key='downloadMetadataMp3Button', tooltip="Burn Metadata to MP3")]]
    elif musicSearchResultData["geniusMusicSearchAlbumList"] != None: layout = [[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\personSearch.png', border_width=0, button_color='#2B475D', key='musicSearchArtistResultsMenu', tooltip="Search Artist"), sg.Push(background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Text("Music Search Result", font='Any 20', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchAlbum.png', border_width=0, button_color='#2B475D', key='musicSearchAlbumResultsMenu', tooltip="Open Album"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchMP3Opener.png', border_width=0, button_color='#2B475D', key='downloadMetadataMp3Button', tooltip="Burn Metadata to MP3")]]
    else: layout = [[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\personSearch.png', border_width=0, button_color='#2B475D', key='musicSearchArtistResultsMenu', tooltip="Search Artist"), sg.Push(background_color='#2B475D'), sg.Text("Music Search Result", font='Any 20', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchMP3Opener.png', border_width=0, button_color='#2B475D', key='downloadMetadataMp3Button', tooltip="Burn Metadata to MP3")]]
    if musicSub == "Apple Music": layout += [[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchArtist.png', border_width=0, button_color='#2B475D', key='musicSearchArtistButton', tooltip="Open Artist page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchGenius.png', border_width=0, button_color='#2B475D', key='searchmusicSearchGenius', tooltip="Open Genius Lyrics page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchListenApple.png', border_width=0, button_color='#2B475D', key='musicSearchListenButton', tooltip="Play Song - Apple Music")]]
    elif musicSub == "Spotify": layout += [[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchArtist.png', border_width=0, button_color='#2B475D', key='musicSearchArtistButton', tooltip="Open Artist page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchGenius.png', border_width=0, button_color='#2B475D', key='searchmusicSearchGenius', tooltip="Open Genius Lyrics page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchListenSpotify.png', border_width=0, button_color='#2B475D', key='musicSearchListenButton', tooltip="Play Song - Spotify")]]
    if musicSearchResultData["geniusMusicSearchAlbum"] != None and musicSearchResultData["geniusMusicSearchDate"] != None: layout += [[sg.Image(musicSearchResultData["png_data"])], [sg.Text(musicSearchResultData["geniusMusicSearchSongNameInfo"], font='Any 20 bold', background_color='#2B475D', enable_events=True, key='geniusMusicSearchSongNameInfoText', tooltip=musicSearchResultData["extendedSongInfo"][0])], [sg.Text(musicSearchResultData["geniusMusicSearchAlbum"], font='Any 18', background_color='#2B475D', enable_events=True, key='geniusMusicSearchAlbumText', tooltip=musicSearchResultData["extendedSongInfo"][2])], [sg.Text(musicSearchResultData["geniusMusicSearchArtists"], font='Any 16', background_color='#2B475D', enable_events=True, key='geniusMusicSearchArtistsText', tooltip=musicSearchResultData["extendedSongInfo"][1])], [sg.Text(musicSearchResultData["geniusMusicSearchGenre"].upper() + " " + u"\N{Dot Operator}" + " " + musicSearchResultData["geniusMusicSearchDate"], font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchGenreText')]] ## Album Name Found
    elif musicSearchResultData["geniusMusicSearchAlbum"] != None and musicSearchResultData["geniusMusicSearchDate"] == None: layout += [[sg.Image(musicSearchResultData["png_data"])], [sg.Text(musicSearchResultData["geniusMusicSearchSongNameInfo"], font='Any 20 bold', background_color='#2B475D', enable_events=True, key='geniusMusicSearchSongNameInfoText', tooltip=musicSearchResultData["extendedSongInfo"][0])], [sg.Text(musicSearchResultData["geniusMusicSearchAlbum"], font='Any 18', background_color='#2B475D', enable_events=True, key='geniusMusicSearchAlbumText', tooltip=musicSearchResultData["extendedSongInfo"][2])], [sg.Text(musicSearchResultData["geniusMusicSearchArtists"], font='Any 16', background_color='#2B475D', enable_events=True, key='geniusMusicSearchArtistsText', tooltip=musicSearchResultData["extendedSongInfo"][1])], [sg.Text(musicSearchResultData["geniusMusicSearchGenre"].upper(), font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchGenreText')]] ## Album Name Found and No Release Date
    elif musicSearchResultData["geniusMusicSearchAlbum"] == None and musicSearchResultData["geniusMusicSearchDate"] != None: layout += [[sg.Image(musicSearchResultData["png_data"])], [sg.Text(musicSearchResultData["geniusMusicSearchSongNameInfo"], font='Any 20 bold', background_color='#2B475D', enable_events=True, key='geniusMusicSearchSongNameInfoText', tooltip=musicSearchResultData["extendedSongInfo"][0])], [sg.Text(musicSearchResultData["geniusMusicSearchArtists"], font='Any 16', background_color='#2B475D', enable_events=True, key='geniusMusicSearchArtistsText', tooltip=musicSearchResultData["extendedSongInfo"][1])], [sg.Text(musicSearchResultData["geniusMusicSearchGenre"].upper() + " " + u"\N{Dot Operator}" + " " + musicSearchResultData["geniusMusicSearchDate"], font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchGenreText')]] ## Album Name not Found
    else: layout += [[sg.Image(musicSearchResultData["png_data"])], [sg.Text(musicSearchResultData["geniusMusicSearchSongNameInfo"], font='Any 20 bold', background_color='#2B475D', enable_events=True, key='geniusMusicSearchSongNameInfoText', tooltip=musicSearchResultData["extendedSongInfo"][0])], [sg.Text(musicSearchResultData["geniusMusicSearchArtists"], font='Any 16', background_color='#2B475D', enable_events=True, key='geniusMusicSearchArtistsText', tooltip=musicSearchResultData["extendedSongInfo"][1])], [sg.Text(musicSearchResultData["geniusMusicSearchGenre"].upper(), font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchGenreText')]] ## No Album Name and No Release Date
    if musicSearchResultData["lyrics"] != None: layout += [[sg.Multiline("", size=(55,20), font='Any 11', autoscroll=False, disabled=True, right_click_menu=lyricsRightClickMenu, key='MusicSearchSongWindowLyrics')]] ## Add Empty Lyrics Box
    else: layout += [[sg.Text("Lyrics couldn't be found on Genius.", font='Any 12 bold', background_color='#2B475D')]] ## No Lyrics Found Message
    if musicSearchResultData["lyrics"] != None: layout += [[sg.Text("Profanity Engine: Not checked yet", font='Any 11', background_color='#2B475D', key='songUsableText')]] ## Default Profanity Engine Text
    if musicSearchResultData["geniusMusicSearchLabels"] != None and len(musicSearchResultData["geniusMusicSearchLabels"]) > 1: layout += [[sg.Text("Labels: " + str(musicSearchResultData["geniusMusicSearchLabels"]).replace("&amp;", "&").replace("[", "").replace("]", "").replace('"', "").replace("'", ""), font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchLabels')]] ## Song's Labels
    elif musicSearchResultData["geniusMusicSearchLabels"] != None and len(musicSearchResultData["geniusMusicSearchLabels"]) == 1: layout += [[sg.Text("Label: " + str(musicSearchResultData["geniusMusicSearchLabels"]).replace("&amp;", "&").replace("[", "").replace("]", "").replace('"', "").replace("'", ""), font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchLabels')]] ## Song's Label
    layout += [[sg.Text("Music Search powered by Genius", font='Any 11', background_color='#2B475D')]] ## Credits
    MusicSearchSongWindow = sg.Window("Music Search - Song", layout, background_color='#2B475D', resizable=True, finalize=True, keep_on_top=False, element_justification='c')
    if musicSearchResultData["lyrics"] != None:
        lyricsLine:sg.Multiline = MusicSearchSongWindow['MusicSearchSongWindowLyrics'] ## Lyrics Right Click Menu
        MusicSearchSongWindow.TKroot.minsize(580, 710)
    else: MusicSearchSongWindow.TKroot.minsize(580, 510)
    MusicSearchSongWindow.hide()
    MusicSearchSongWindow.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - MusicSearchSongWindow.size[0] // 2 -40, HomeWindow.TKroot.winfo_y() + HomeWindow.TKroot.winfo_height() // 2 - MusicSearchSongWindow.size[1] // 2)
    if MusicSearchSongWindow.CurrentLocation()[1] < 200: MusicSearchSongWindow.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - MusicSearchSongWindow.size[0] // 2 -40, 100) ## Fix Over Top
    MusicSearchSongWindow.un_hide()
    ## Window Shortcuts
    MusicSearchSongWindow.bind('<PageUp>', '_PageUp')      ## List Result shortcut
    MusicSearchSongWindow.bind('<PageDown>', '_PageDown')  ## Download Metadata shortcut
    MusicSearchSongWindow.bind('<Delete>', '_Delete')      ## Close Window shortcut
    MusicSearchSongWindow.bind('<Home>', '_Home')          ## Genius Lyrics shortcut
    MusicSearchSongWindow.bind('<End>', '_End')            ## Artist shortcut
    ## Mouse Icon Changes
    for key in ['downloadMetadataMp3Button', 'musicSearchArtistButton', 'musicSearchArtistResultsMenu', 'musicSearchListenButton', 'searchmusicSearchGenius']: MusicSearchSongWindow[key].Widget.config(cursor="hand2") ## Hover icons
    if musicSearchResultData["hitsFound"] > 1: MusicSearchSongWindow["musicSearchResultsMenu"].Widget.config(cursor="hand2")                                     ## List Search Results Hover icon
    if musicSearchResultData["geniusMusicSearchAlbumList"] != None: MusicSearchSongWindow["musicSearchAlbumResultsMenu"].Widget.config(cursor="hand2")           ## Album List Hover icon
    if musicSearchResultData["geniusMusicSearchSongNameInfo"] != None: MusicSearchSongWindow["geniusMusicSearchSongNameInfoText"].Widget.config(cursor="hand2")  ## Song Name Text Hover icon
    if musicSearchResultData["geniusMusicSearchAlbum"] != None: MusicSearchSongWindow["geniusMusicSearchAlbumText"].Widget.config(cursor="hand2")                ## Song Album Text Hover icon
    if musicSearchResultData["geniusMusicSearchArtists"] != None: MusicSearchSongWindow["geniusMusicSearchArtistsText"].Widget.config(cursor="hand2")            ## Song Artist Text Hover icon
    if musicSearchResultData["geniusMusicSearchGenre"] != None: MusicSearchSongWindow["geniusMusicSearchGenreText"].Widget.config(cursor="hand2")                ## Song Genre Text Hover icon
    if musicSearchResultData["geniusMusicSearchLabels"] != None: MusicSearchSongWindow["geniusMusicSearchLabels"].Widget.config(cursor="hand2")                  ## Song Label Hover icon
    ## Print Lyrics and Check for Profanity
    if musicSearchResultData["lyrics"] != None: musicSearchPrintSongLyrics("musicSearch", musicSearchResultData["lyricsListFinal"])
    while True:
        event, values = MusicSearchSongWindow.read()
        if event == sg.WIN_CLOSED or (event == '_Delete'): ## Window Closed
            MusicSearchSongWindow.close()
            try: HomeWindow.Element('musicSearchPanel_songSearchInput').Update("")
            except: pass
            break
        elif event == 'geniusMusicSearchSongNameInfoText': ## Click Song Title
            MusicSearchSongWindow.TKroot.clipboard_clear()
            MusicSearchSongWindow.TKroot.clipboard_append(musicSearchResultData["geniusMusicSearchSongNameInfo"])
        elif event == 'geniusMusicSearchAlbumText': ## Click Album Title
            MusicSearchSongWindow.TKroot.clipboard_clear()
            MusicSearchSongWindow.TKroot.clipboard_append(musicSearchResultData["geniusMusicSearchAlbum"])
        elif event == 'geniusMusicSearchArtistsText': ## Click Artist Name
            MusicSearchSongWindow.TKroot.clipboard_clear()
            MusicSearchSongWindow.TKroot.clipboard_append(musicSearchResultData["geniusMusicSearchArtists"])
        elif event == 'geniusMusicSearchGenreText': ## Click Song Genre
            MusicSearchSongWindow.TKroot.clipboard_clear()
            MusicSearchSongWindow.TKroot.clipboard_append(' '.join(word.capitalize() for word in (musicSearchResultData["geniusMusicSearchGenre"].lower()).split()))
        elif event == 'geniusMusicSearchLabels': ## Click Song Labels
            for label in musicSearchResultData["geniusMusicSearchLabels"]: webbrowser.open("https://en.wikipedia.org/wiki/" + label.replace("[", "").replace("]", "").replace('"', "").replace("'", "").replace(" ", "_"), new=2, autoraise=True)
        elif event in lyricsRightClickMenu[1]: ## Right Click Menu Actions
            try:
                if event == 'Copy': ## Copy Lyrics Text
                    try:
                        MusicSearchSongWindow.TKroot.clipboard_clear()
                        MusicSearchSongWindow.TKroot.clipboard_append(lyricsLine.Widget.selection_get())
                    except: pass
                elif event == 'Lookup Definition': webbrowser.open("https://www.dictionary.com/browse/" + (lyricsLine.Widget.selection_get().split(" ")[0]).replace(",", "").replace(".", "").replace("?", "").replace("!", "").replace(" ", "-"), new=2, autoraise=True)
                elif event == 'Add to Profanity Engine' and lyricsLine.Widget.selection_get().strip().replace("'", "~").lower() not in profanityEngineDefinitions: ## Add Text to Profanity Engine
                    try:
                        wordToAdd = re.sub(r'[\'"\.,!?;:]', '', (lyricsLine.Widget.selection_get()).strip().lower())
                        profanityEngineDefinitions.append(wordToAdd.replace("'", "~"))
                        saveProfanityEngine(profanityEngineDefinitions)
                        musicSearchPrintSongLyrics("musicSearch", musicSearchResultData["lyricsListFinal"]) ## Reload Music Search's Lyrics
                        popupMessage("Profanity Engine", '"' + wordToAdd + '"  has been successfully added to the Profanity Engine.', "saved", 3000) ## Show Success Message
                    except: popupMessage("Profanity Engine", 'Failed to add "' + wordToAdd + '" to the Profanity Engine.', "error", 3000) ## Show Error Message
                elif event == 'Remove from Profanity Engine': ## Remove Text from Profanity Engine
                    try:
                        wordToRemove = re.sub(r'[\'"\.,!?;:]', '', (lyricsLine.Widget.selection_get()).strip().lower())
                        try:
                            profanityEngineDefinitions.remove(wordToRemove.replace("'", "~"))
                            saveProfanityEngine(profanityEngineDefinitions)
                            musicSearchPrintSongLyrics("musicSearch", musicSearchResultData["lyricsListFinal"]) ## Reload Music Search's Lyrics
                            popupMessage("Profanity Engine", '"' + wordToRemove + '"  has been successfully added to the Profanity Engine.', "saved", 3000) ## Show Success Message
                        except: popupMessage("Profanity Engine", '"' + wordToRemove + '" is not in the Profanity Engine.', "fail", 3000) ## Show Fail Message
                    except: popupMessage("Profanity Engine", 'Failed to add "' + wordToRemove + '" to the Profanity Engine.', "error", 3000) ## Show Error Message
            except: pass
        elif event == 'musicSearchResultsMenu' or (event == '_PageUp'): ## Move Song to List Results
            MusicSearchSongWindow.close()
            if "/songs/" in userInput: geniusMusicSearchList(musicSearchResultData["geniusMusicSearchSongNameInfo"] + " - " + musicSearchResultData["geniusMusicSearchArtists"])
            else: geniusMusicSearchList(userInput)
            break
        elif event == 'musicSearchArtistResultsMenu': ## Move Artist to List Results
            MusicSearchSongWindow.close()
            geniusMusicSearchList(musicSearchResultData["geniusMusicSearchPrimeArtist"])
            break
        elif event == 'musicSearchAlbumResultsMenu': ## Album List
            MusicSearchSongWindow.close()
            geniusMusicSearchList(musicSearchResultData["geniusMusicSearchAlbumList"], "album")
            break
        elif event == 'downloadMetadataMp3Button' or (event == '_PageDown'):
            appSelected = "Metadata_Burner"
            try: HomeWindow.Element('musicSearchPanel_songSearchInput').Update("")
            except: pass
            HomeWindow['metadataBurnerPanel'].update(visible=True)
            HomeWindow['musicSearchPanel'].update(visible=False)
            HomeWindow.Element('metadataBurnerPanel_songLocationInput').Update("")
            if musicSearchResultData["geniusMusicSearchSongNameInfo"] != None: HomeWindow.Element('metadataBurnerPanel_songNameInput').Update(musicSearchResultData["geniusMusicSearchSongNameInfo"])
            if musicSearchResultData["geniusMusicSearchSongNameInfo"] != None: HomeWindow.Element('metadataBurnerPanel_songNameInput').Update(musicSearchResultData["geniusMusicSearchSongNameInfo"])
            if musicSearchResultData["geniusMusicSearchPrimeArtist"] != None: HomeWindow.Element('metadataBurnerPanel_songArtistInput').Update(musicSearchResultData["geniusMusicSearchPrimeArtist"])
            if musicSearchResultData["geniusMusicSearchAlbum"] != None: HomeWindow.Element('metadataBurnerPanel_songAlbumInput').Update(musicSearchResultData["geniusMusicSearchAlbum"])
            if musicSearchResultData["geniusMusicSearchDate"] != None: HomeWindow.Element('metadataBurnerPanel_songYearInput').Update(musicSearchResultData["geniusMusicSearchDate"])
            if musicSearchResultData["geniusMusicSearchGenre"] != None: HomeWindow.Element('metadataBurnerPanel_songGenreInput').Update(musicSearchResultData["geniusMusicSearchGenre"])
            if musicSearchResultData["geniusMusicSearchAlbumCurrent"] != None: HomeWindow.Element('metadataBurnerPanel_albumCurrentLengthInput').Update(musicSearchResultData["geniusMusicSearchAlbumCurrent"])
            if musicSearchResultData["geniusMusicSearchAlbumLength"] != None: HomeWindow.Element('metadataBurnerPanel_albumTotalLengthInput').Update(musicSearchResultData["geniusMusicSearchAlbumLength"])
            if musicSearchResultData["geniusMusicSearchCDCurrent"] != None: HomeWindow.Element('metadataBurnerPanel_cdCurrentLengthInput').Update(musicSearchResultData["geniusMusicSearchCDCurrent"])
            if musicSearchResultData["geniusMusicSearchCDLength"] != None: HomeWindow.Element('metadataBurnerPanel_cdTotalLengthInput').Update(musicSearchResultData["geniusMusicSearchCDLength"])
            if musicSearchResultData["geniusMusicSearchLabels"] != None: HomeWindow.Element('metadataBurnerPanel_songPublisherInput').Update(musicSearchResultData["geniusMusicSearchLabels"][0])
            if musicSearchResultData["png_data_location"] != None: HomeWindow.Element('metadataBurnerPanel_songArtworkInput').Update(musicSearchResultData["png_data_location"])
            HomeWindow.Element('metadataBurnerPanel_songArtworkBrowser').InitialFolder = os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Music Search", "Artworks")
            HomeWindow.Element('metadataBurnerPanel_lyricsInput').update("")
            if musicSearchResultData["lyricsListFinal"] != None:
                for i in range(len(musicSearchResultData["lyricsListFinal"])):
                    HomeWindow.Element('metadataBurnerPanel_lyricsInput').update(musicSearchResultData["lyricsListFinal"][i], autoscroll=False, append=True)
                    if i != len(musicSearchResultData["lyricsListFinal"]) - 1: HomeWindow.Element('metadataBurnerPanel_lyricsInput').update("\n", autoscroll=False, append=True)
            MusicSearchSongWindow.close()
            break
        elif event == 'musicSearchArtistButton' or (event == '_Home'): webbrowser.open(musicSearchResultData["geniusMusicSearchArtistURL"], new=2, autoraise=True)  ## Open Artist's Genius Page
        elif event == 'searchmusicSearchGenius' or (event == '_End'): webbrowser.open(musicSearchResultData["geniusMusicSearchGeniusURL"], new=2, autoraise=True) ## Open Genius Page
        elif event == 'musicSearchListenButton': ## Play Song Online
            if musicSub == "Apple Music": webbrowser.open("https://music.apple.com/us/search?term=" + musicSearchResultData["geniusMusicSearchPrimeArtist"].replace(" ", "%20") + "%20" + musicSearchResultData["geniusMusicSearchSongName"].replace(" ", "%20"), new=2, autoraise=True)
            elif musicSub == "Spotify": webbrowser.open("https://open.spotify.com/search/" + musicSearchResultData["geniusMusicSearchPrimeArtist"].replace(" ", "%20") + "%20" + musicSearchResultData["geniusMusicSearchSongName"].replace(" ", "%20"), new=2, autoraise=True)

def musicSearchPrintSongLyrics(lyricsLocation, lyricsListFinal):
    global profanityEngineDefinitions
    if lyricsLocation == "musicSearch": lyricsBox, lyricsText = MusicSearchSongWindow['MusicSearchSongWindowLyrics'], MusicSearchSongWindow['songUsableText']
    elif lyricsLocation == "lyricsCheck": lyricsBox, lyricsText = HomeWindow['lyricsCheckerPanel_lyricsInput'], HomeWindow['lyricsCheckerPanel_songUsableText']
    try:
        badWordCount, totalCount = 0, 0
        lyricsBox.update("", autoscroll=False)
        loadProfanityEngineDefinitions(False)
        profanityRegex = re.compile('|'.join([r'\b{}\b'.format(re.escape(phrase)) for phrase in [phrase.lower().replace("\n", "").replace("~", "'") for phrase in profanityEngineDefinitions]]), re.IGNORECASE)
        for lyric in lyricsListFinal:
            badLine, lastEnd = False, 0
            stripped_lyric = ''.join(char if char not in '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~' else ' ' for char in lyric) ## Create a version of the lyric without punctuation for matching
            matches = profanityRegex.finditer(stripped_lyric)
            for match in matches:
                start, end = match.span()
                actualStart = len(''.join(char if char not in '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~' else ' ' for char in lyric[:start])) 
                actualEnd = len(''.join(char if char not in '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~' else ' ' for char in lyric[:end]))
                lyricsBox.update(lyric[lastEnd:actualStart], autoscroll=False, append=True) ## Update the lyricsBox with the non-matching part in normal color
                lyricsBox.update(lyric[actualStart:actualEnd], autoscroll=False, text_color_for_value='Red', append=True) ## Update the lyricsBox with the matching part in red
                badLine, lastEnd = True, actualEnd
            lyricsBox.update(lyric[lastEnd:], autoscroll=False, append=True)
            if totalCount != len(lyricsListFinal) - 1: lyricsBox.update("\n", autoscroll=False, append=True)
            if badLine: badWordCount += 1
            totalCount += 1
    except: ## Profanity Engine Dictionary Failed to Load
        profanityEngineDefinitions = "Failed"
        lyricsBox.update("", autoscroll=False)
        lyricsBox.update('\n'.join(lyricsListFinal), autoscroll=False)
    ## Update Profanity Engine Text
    if lyricsListFinal != None and profanityEngineDefinitions != "Failed":
        lyricsText.update("Profanity Engine: Lyrics are " + str(round((1-(badWordCount/len(lyricsListFinal))) * 100)) + "% clean.")
        if round((1-(badWordCount/len(lyricsListFinal))) * 100) == 100: lyricsText.update(text_color='#00C957', font='Any 11')
        elif (round((1-(badWordCount/len(lyricsListFinal)))) * 100) >= 95: lyricsText.update(text_color='#FFD700', font='Any 11')
        elif (round((1-(badWordCount/len(lyricsListFinal)))) * 100) >= 90: lyricsText.update(text_color='#FF6103', font='Any 11')
        elif (round((1-(badWordCount/len(lyricsListFinal)))) * 100) < 90: lyricsText.update(text_color='#DC143C', font='Any 11')
    elif lyricsListFinal != None and profanityEngineDefinitions == "Failed": lyricsText.update("Profanity Engine failed to load.", font='Any 13 bold')

def burnAudioData(audioSavedPath, burnLyricsOnly, multipleArtists, renameFile, displayMessage=True):
    try:
        print(f"[INFO]: Metadata Burner: {musicSearchResultData}, location: {audioSavedPath}, ({burnLyricsOnly}, {multipleArtists}, {renameFile}, {displayMessage})")
        audiofile, lyricsText = eyed3.load(audioSavedPath), "" ## Load MP3
        try: print(f"[INFO] Testing metadata tags: {audiofile.tag}")
        except:
            try: audiofile.initTag(version=(2, 3, 0))
            except:
                print(f"[ERROR]: Metadata Burner can't write")
                popupMessage("Metadata Burner", "Can't write to file.", "error")
                return            
        for i in range(len(musicSearchResultData["lyricsListFinal"])): ## Get Lyrics
            if len(musicSearchResultData["lyricsListFinal"][i]) == 0: lyricsText += "\n"
            else: lyricsText += musicSearchResultData["lyricsListFinal"][i] + "\n"
        if musicSearchResultData["lyrics"] != None: audiofile.tag.lyrics.set(lyricsText) ## Save Lyrics
        if burnLyricsOnly:
            audiofile.tag.comments.set(u"Metadata: Oszust Industries") ## Comment
            audiofile.tag.save(version=(2, 3, 0)) ## Save File
            popupMessage("Metadata Burner", "Metadata has been successfully saved to " + renameFile + ".", "saved", 3000) ## Show Success Message
            return
        audiofile.tag.artist = musicSearchResultData["extendedSongInfo"][1] ## Artist
        if multipleArtists: audiofile.tag.album_artist = "Various Artists" ## Album's Artists (Various Artists)
        else: audiofile.tag.album_artist = musicSearchResultData["geniusMusicSearchPrimeArtist"] ## Album's Artists
        audiofile.tag.title = musicSearchResultData["extendedSongInfo"][0] ## Title
        if musicSearchResultData["geniusMusicSearchDate"] != None and musicSearchResultData["geniusMusicSearchDate"] != "Unknown Release Date": audiofile.tag.recording_date = musicSearchResultData["geniusMusicSearchDate"][-4:] ## Year
        if musicSearchResultData["geniusMusicSearchGenre"] != "Non-Music": audiofile.tag.genre = musicSearchResultData["geniusMusicSearchGenre"] ## Genre
        audiofile.tag.album = musicSearchResultData["extendedSongInfo"][2] ## Album
        if musicSearchResultData["geniusMusicSearchLabels"] != None and musicSearchResultData["geniusMusicSearchLabels"] != "": audiofile.tag.publisher = musicSearchResultData["geniusMusicSearchLabels"][0].replace("[", "").replace("]", "").replace("'", "") ## Label
        if musicSearchResultData["geniusMusicSearchAlbumCurrent"] != None and musicSearchResultData["geniusMusicSearchAlbumCurrent"] != "" and musicSearchResultData["geniusMusicSearchAlbumLength"] != None and musicSearchResultData["geniusMusicSearchAlbumLength"] != "": audiofile.tag.track_num = (musicSearchResultData["geniusMusicSearchAlbumCurrent"], musicSearchResultData["geniusMusicSearchAlbumLength"]) ## Current Song Position and Total Album
        elif musicSearchResultData["geniusMusicSearchAlbumCurrent"] != None and musicSearchResultData["geniusMusicSearchAlbumCurrent"] != "": audiofile.tag.track_num = musicSearchResultData["geniusMusicSearchAlbumCurrent"] ## Current Song Position
        if musicSearchResultData["geniusMusicSearchCDCurrent"] != None and musicSearchResultData["geniusMusicSearchCDCurrent"] != "" and musicSearchResultData["geniusMusicSearchCDLength"] != None and musicSearchResultData["geniusMusicSearchCDLength"] != "": audiofile.tag.disc_num = (musicSearchResultData["geniusMusicSearchCDCurrent"], musicSearchResultData["geniusMusicSearchCDLength"]) ## Current CD Position and Total CD
        elif musicSearchResultData["geniusMusicSearchCDCurrent"] != None and musicSearchResultData["geniusMusicSearchCDCurrent"] != "": audiofile.tag.disc_num = musicSearchResultData["geniusMusicSearchCDCurrent"] ## Current CD Position
        if musicSearchResultData["png_data"] != str(pathlib.Path(__file__).resolve().parent) + "\\data\\icons\\defaultMusicArtwork.png": 
            for artworkType in [4, 3, 0]: audiofile.tag.images.set(artworkType, musicSearchResultData["png_data"], "image/png") ## Artwork - Basic
            for artworkType in [4, 3, 0]: audiofile.tag.images.set(artworkType, musicSearchResultData["png_data"], "image/jpeg", "cover") ## Artwork - Higher Quality
        audiofile.tag.comments.set(u"Metadata: Oszust Industries") ## Comment
        audiofile.tag.save(version=(2, 3, 0)) ## Save File
        ## Change the audio file's name
        if renameFile != False:
            try: os.rename(audioSavedPath, audioSavedPath.replace(audioSavedPath.rsplit('/', 1)[1], "") + "\\" + renameFile.strip() + ".mp3") ## Rename MP3 to Song Name
            except:
                try: os.rename(audioSavedPath, audioSavedPath.replace(audioSavedPath.rsplit('\\', 1)[1], "") + "\\" + renameFile.strip() + ".mp3") ## Rename MP3 to Song Name Fix
                except: print(f"[ERROR]: Metadata Burner: Failed to rename to {renameFile}")
        if displayMessage: popupMessage("Metadata Burner", "Metadata has been successfully saved to " + renameFile + ".", "saved", 3000) ## Show Success Message
    except Exception as Argument:
        print(f"[ERROR]: Metadata Burner failed: {Argument}")
        popupMessage("Metadata Burner", "Failed to burn metadata.", "error")

def loadGeniusMusicList(userInput, forceResult):
    global musicListLayout, loadingAction, musicListResultData
    print(f"[INFO]: Music Search List: {userInput}")
    musicListResultData = {}
    ## Set Local Variables
    try: musicSub = userSettingsData["musicService"]
    except: musicSub = "Apple Music"
    if isinstance(userInput, list): userInputDisplay = musicSearchResultData["geniusMusicSearchAlbum"] + " - " + musicSearchResultData["geniusMusicSearchPrimeArtist"]
    else: userInputDisplay = userInput
    artistSearch, musicListResultData["geniusMusicSearchDate"], musicListResultData["geniusSongIDs"], musicListResultData["geniusURLs"], musicListResultData["longArtists"], musicListResultData["longSongNameInfo"], musicListResultData["lyricsHoverMessage"], musicListResultData["lyricsImage"], musicListResultData["musicListLayout"], resultColumns, resultNumber, musicListResultData["resultNumbers"], musicListResultData["songArtists"], musicListResultData["songNames"], musicListResultData["song_art_image_url"] = False, [], [], [], [], [], [], [], [[sg.Push(background_color='#657076'), sg.Text('Music Search Results:', font='Any 20', background_color='#657076'), sg.Push(background_color='#657076')], [sg.Push(background_color='#657076'), sg.Input(userInputDisplay, do_not_clear=True, size=(60,1), enable_events=True, key='geniusMusicListSearchInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\search.png', border_width=0, button_color='#657076', key='geniusMusicListSearchButton', tooltip="Search"), sg.Push(background_color='#657076')]], [], 0, [], [], [], []
    if forceResult != "refresh": ## Read from Cache
        try:
            with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Music Search", "Music Search List Info", userInput.lower().replace(" ", "").rsplit('/', 1)[-1] + ".json"), 'r') as file:
                musicListResultData = json.load(file)
            musicListResultData["musicListLayout"] = [[sg.Push(background_color='#657076'), sg.Text('Music Search Results:', font='Any 20', background_color='#657076'), sg.Push(background_color='#657076')], [sg.Push(background_color='#657076'), sg.Input(userInputDisplay, do_not_clear=True, size=(60,1), enable_events=True, key='geniusMusicListSearchInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\search.png', border_width=0, button_color='#657076', key='geniusMusicListSearchButton', tooltip="Search"), sg.Push(background_color='#657076')]]
            if datetime.datetime.strptime(musicListResultData["geniusMusicSearchExpireDate"], '%Y-%m-%d') > datetime.datetime.now(): ## Cache Expired
                for resultNumber in musicListResultData["resultNumbers"]:
                    ## Look in Cache for Artwork
                    try: ## Open Artwork PNG from Cache
                        pil_image = Image.open(str(os.getenv('APPDATA')) + "\\Oszust Industries\\Oszust OS Music Tools\\Cache\\Music Search\\Mini Artworks\\" + str(musicListResultData["song_art_image_url"][resultNumber]).split(".com/",1)[1].split(".",1)[0] + ".png") ## Open Artwork from Cache
                        png_bio = io.BytesIO()
                        pil_image.save(png_bio, format="PNG")
                        png_data = png_bio.getvalue()
                    except: png_data = str(pathlib.Path(__file__).resolve().parent) + "\\data\\icons\\defaultMusicArtwork.png"
                    ## Music Service
                    if musicSub == "Apple Music": musicServiceImage = "musicSearchListenApple" ## Set Listening Link to Apple
                    elif musicSub == "Spotify": musicServiceImage = "musicSearchListenSpotify" ## Set Listening Link to Spotify
                    ## Song Window
                    if musicListResultData["geniusMusicSearchDate"][resultNumber] != None: resultColumns += [[sg.Column([[sg.Image(png_data, background_color='#2b475d'), sg.Column([[sg.Text(str(musicListResultData["songNames"][resultNumber]), font='Any 16', background_color='#2b475d', tooltip=musicListResultData["longSongNameInfo"][resultNumber])], [sg.Text(str(musicListResultData["songArtists"][resultNumber]), font='Any 14', background_color='#2b475d', tooltip=musicListResultData["longArtists"][resultNumber])], [sg.Text(str(musicListResultData["geniusMusicSearchDate"][resultNumber]), font='Any 12', background_color='#2b475d')]], background_color='#2b475d', size=(400, 100)), sg.Push(background_color='#2b475d'), sg.Column([[sg.Image(str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\'+musicListResultData["lyricsImage"][resultNumber]+'.png', background_color='#2b475d', tooltip=musicListResultData["lyricsHoverMessage"][resultNumber]), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchGenius.png', border_width=0, button_color='#2b475d', key='searchmusicListSearchGenius_' + str(resultNumber), tooltip="Open Genius Page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\'+musicServiceImage+'.png', border_width=0, button_color='#2b475d', key='searchmusicListPlaySong_' + str(resultNumber), tooltip="Play Song"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\openView.png', border_width=0, button_color='#2b475d', key='searchMusicListOpenSong_' + str(resultNumber), tooltip="Open Result")]], background_color='#2b475d')]], background_color='#2b475d', size=(700, 100))]]
                    else: resultColumns += [[sg.Column([[sg.Image(png_data, background_color='#2b475d'), sg.Column([[sg.Text(str(musicListResultData["songNames"][resultNumber]), font='Any 16', background_color='#2b475d', tooltip=musicListResultData["longSongNameInfo"][resultNumber])], [sg.Text(str(musicListResultData["songArtists"][resultNumber]), font='Any 14', background_color='#2b475d', tooltip=musicListResultData["longArtists"][resultNumber])]], background_color='#2b475d', size=(400, 100)), sg.Push(background_color='#2b475d'), sg.Column([[sg.Image(str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\'+musicListResultData["lyricsImage"][resultNumber]+'.png', background_color='#2b475d', tooltip=musicListResultData["lyricsHoverMessage"][resultNumber]), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchGenius.png', border_width=0, button_color='#2b475d', key='searchmusicListSearchGenius_' + str(resultNumber), tooltip="Open Genius Page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\'+musicServiceImage+'.png', border_width=0, button_color='#2b475d', key='searchmusicListPlaySong_' + str(resultNumber), tooltip="Play Song"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\openView.png', border_width=0, button_color='#2b475d', key='searchMusicListOpenSong_' + str(resultNumber), tooltip="Open Result")]], background_color='#2b475d')]], background_color='#2b475d', size=(700, 100))]]
                if len(resultColumns) <= 8: musicListResultData["musicListLayout"] += [[sg.Column(resultColumns, scrollable=True, expand_x=True, background_color='#2b475d', vertical_scroll_only=True, size=(700, len(resultColumns)*110))]]
                else: musicListResultData["musicListLayout"] += [[sg.Column(resultColumns, scrollable=True, expand_x=True, background_color='#2b475d', vertical_scroll_only=True, size=(700, 880))]]
                musicListResultData["musicListLayout"] += [[sg.Push(background_color='#657076'), sg.Text("Music Search powered by Genius (" + str(len(resultColumns)) + " Results)", background_color='#657076', font='Any 11'), sg.Push(background_color='#657076')]] ## Credits
                loadingAction = "Search_Finished"
                return
            else: os.remove(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Music Search", "Music Search List Info", userInput.lower().replace(" ", "").rsplit('/', 1)[-1] + ".json"))
        except: pass
    ## Load from Online
    if isinstance(userInput, list):
        musicSearchApiBody, hitsFound = [], 0
        for song in userInput:
            request = urllib.request.Request("http://api.genius.com/search?q=" + urllib.request.quote(song.lower().replace(" by ", "-")).replace(" ", "-") + "-" + musicSearchResultData["geniusMusicSearchPrimeArtist"].lower().replace(" ", "-") + "&lang=en&type=song&page=1")
            request.add_header("Authorization", "Bearer " + "ThgJU2pTawXV60l2g2jQXNEYT-b3MP7KDRd51BD-kLL7K5Eg8-UzrEGY96L3Z1c4")   
            request.add_header("User-Agent", "curl/7.9.8 (i686-pc-linux-gnu) libcurl 7.9.8 (OpenSSL 0.9.6b) (ipv6 enabled)")
            try: raw = (urllib.request.urlopen(request, timeout=10)).read()
            except Exception as Argument:
                if "Error 403" in str(Argument):
                    print(f"[ERROR]: Music Search List: Robot check failed")
                    loadingAction = "Genius_Robot_Check"
                    return
                else:
                    print(f"[ERROR]: Music Search List: Genius down")
                    loadingAction = "Genius_Page_Down:" + str(Argument)
                    return
            ## Find Number of Hits
            musicSearchApiBodyTemp = [result for result in (json.loads(raw)["response"]["hits"]) if "song" in result["type"] and not any(tag in result["result"]["title"].lower() for tag in ["instrumental", "radio edit", "slow", "sped", "version", "acapella", "acoustic", "log", "transcriptions"]) and not any(tag in result["result"]["artist_names"].lower() for tag in ["genius", "siriusxm", "fortnite"])]
            try:
                musicSearchApiBody.append(musicSearchApiBodyTemp[0])
                hitsFound += len(musicSearchApiBody)
            except: pass
        if hitsFound == 0: ## Check if Result Found
            print(f"[ERROR]: Music Search List: No results found")
            loadingAction = "No_Result_Found"
            return
        else: userInput = "done"
    elif userInput != "done":
        if "genius.com" in userInput: userInput = userInput.split("https://genius.com/",1)[1].split("-lyrics",1)[0] ## Genius Website URL
        musicSearchApiBody, hitsFound, pageNumber = [], 0, 1 
        while pageNumber < 3:
            request = urllib.request.Request("http://api.genius.com/search?q=" + urllib.request.quote(userInput.lower().replace(" by ", "-")) + "&lang=en&type=song&page=" + str(pageNumber))
            request.add_header("Authorization", "Bearer " + "ThgJU2pTawXV60l2g2jQXNEYT-b3MP7KDRd51BD-kLL7K5Eg8-UzrEGY96L3Z1c4")   
            request.add_header("User-Agent", "curl/7.9.8 (i686-pc-linux-gnu) libcurl 7.9.8 (OpenSSL 0.9.6b) (ipv6 enabled)")
            try: raw = (urllib.request.urlopen(request, timeout=10)).read()
            except Exception as Argument:
                if "Error 403" in str(Argument):
                    print(f"[ERROR]: Music Search List: Robot check failed")
                    loadingAction = "Genius_Robot_Check"
                    return
                else:
                    print(f"[ERROR]: Music Search List: Genius down")
                    loadingAction = "Genius_Page_Down:" + str(Argument)
                    return
            ## Find Number of Hits
            musicSearchApiBodyTemp = [result for result in (json.loads(raw)["response"]["hits"]) if "song" in result["type"] and not any(tag in result["result"]["title"].lower() for tag in ["instrumental", "radio edit", "slow", "sped", "version", "acapella", "acoustic", "log", "transcriptions"]) and not any(tag in result["result"]["artist_names"].lower() for tag in ["genius", "siriusxm", "fortnite"])]
            try:
                for song in musicSearchApiBodyTemp: musicSearchApiBody.append(song)
                hitsFound += len(musicSearchApiBody)
            except: pass
            if len(musicSearchApiBody) > 0 and str(musicSearchApiBody[0]["result"]["primary_artist"]["name"]).lower() not in userInput.lower(): pageNumber += 1
            elif len(musicSearchApiBody) > 0 and str(musicSearchApiBody[0]["result"]["primary_artist"]["name"]).lower() == userInput.lower(): pageNumber += 1
            else: pageNumber = 6
        if hitsFound == 0: ## Check if Result Found
            print(f"[ERROR]: Music Search List: No results found")
            loadingAction = "No_Result_Found"
            return
    while hitsFound > 0 and resultNumber < len(musicSearchApiBody) and resultNumber < 20:
        geniusMusicSearchArtists = str(musicSearchApiBody[resultNumber]["result"]["artist_names"]).replace("(Rock)", "") ## Song Artists
        musicListResultData["songArtists"].append(geniusMusicSearchArtists) ## Add Artists to List 
        geniusMusicSearchPrimeArtist = str(musicSearchApiBody[resultNumber]["result"]["primary_artist"]["name"]).split('(')[0] ## Song Main Artist
        if str(musicSearchApiBody[0]["result"]["artist_names"]).replace(" ", "-").lower() == userInput.lower().replace(" ", "-"): artistSearch = True ## Find if Search is an Artist
        else: artistSearch = False
        musicListResultData["artistSearch"] = artistSearch
        geniusMusicSearchDate = str(musicSearchApiBody[resultNumber]["result"]["release_date_for_display"]) ## Result Release Date
        if geniusMusicSearchDate == "None": geniusMusicSearchDate = None ## Fix Release Date if None Found
        musicListResultData["geniusMusicSearchDate"].append(geniusMusicSearchDate) ## Add Release Date to List
        geniusMusicSearchSongNameInfo = str(musicSearchApiBody[resultNumber]["result"]["title_with_featured"]) ## Result Full Title
        musicListResultData["songNames"].append(geniusMusicSearchSongNameInfo) ## Add Song Full Title to List
        geniusMusicSearchGeniusURL = str(musicSearchApiBody[resultNumber]["result"]["url"]) ## Result Genius URL
        musicListResultData["geniusURLs"].append(geniusMusicSearchGeniusURL) ## Add Genius URL to List
        geniusMusicSearchGeniusSongID = str(musicSearchApiBody[resultNumber]["result"]["api_path"]) ## Song ID
        musicListResultData["geniusSongIDs"].append(geniusMusicSearchGeniusSongID) ## Add Song ID to List
        ## Shorten Results
        longSongNameInfo = geniusMusicSearchSongNameInfo
        musicListResultData["longSongNameInfo"].append(geniusMusicSearchSongNameInfo)
        longArtists = geniusMusicSearchArtists
        musicListResultData["longArtists"].append(geniusMusicSearchArtists)
        if len(geniusMusicSearchSongNameInfo) > 30: geniusMusicSearchSongNameInfo = geniusMusicSearchSongNameInfo[:29] + "..." ## Shorten Song Name
        if len(geniusMusicSearchArtists) > 30: geniusMusicSearchArtists = geniusMusicSearchArtists[:29] + "..." ## Shorten Artists Names
        ## Song Artwork
        try:
            geniusMusicSearchArtworkURL = str(musicSearchApiBody[resultNumber]["result"]["song_art_image_url"])
            if "https://assets.genius.com/images/default_cover_image.png" in geniusMusicSearchArtworkURL: png_data = str(pathlib.Path(__file__).resolve().parent) + "\\data\\icons\\defaultMusicArtwork.png"
            else:
                musicListResultData["song_art_image_url"].append(geniusMusicSearchArtworkURL)
                try: ## Look in Cache for Artwork
                    pil_image = Image.open(str(os.getenv('APPDATA')) + "\\Oszust Industries\\Oszust OS Music Tools\\Cache\\Music Search\\Mini Artworks\\" + str(musicSearchApiBody[resultNumber]["result"]["song_art_image_url"]).split(".com/",1)[1].split(".",1)[0] + ".png") ## Open Artwork from Cache
                    png_bio = io.BytesIO()
                    pil_image.save(png_bio, format="PNG")
                    png_data = png_bio.getvalue()
                except: ## Download Artwork From Online
                    jpg_data = (cloudscraper.create_scraper(browser={"browser": "firefox", "platform": "windows", "mobile": False}).get(geniusMusicSearchArtworkURL).content)
                    pil_image = Image.open(io.BytesIO(jpg_data))
                    pil_image = pil_image.resize((80, 80)) ## Artwork Size
                    png_bio = io.BytesIO()
                    pil_image.save(png_bio, format="PNG")
                    try: ## Save Artwork to Cache PNG
                        pathlib.Path(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Music Search", "Mini Artworks")).mkdir(parents=True, exist_ok=True) ## Create Music Cache Folder
                        with open(os.path.join(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Music Search", "Mini Artworks"), str(musicSearchApiBody[resultNumber]["result"]["song_art_image_url"]).split(".com/", 1)[1].split(".", 1)[0] + ".png"), "wb") as f: f.write(png_bio.getbuffer())
                    except: pass
                    png_data = png_bio.getvalue()
        except: png_data = str(pathlib.Path(__file__).resolve().parent) + "\\data\\icons\\defaultMusicArtwork.png" ## Default Artwork if Retrieval Fails
        ## Song Lyrics
        geniusMusicSearchLyricsState = str(musicSearchApiBody[resultNumber]["result"]["lyrics_state"]) ## Result Song Lyrics
        if geniusMusicSearchLyricsState.lower() == "complete": lyricsImage, lyricsHoverMessage = "checked", "Lyrics Found" ## Lyrics Found
        else: lyricsImage, lyricsHoverMessage = "checkFailed", "Lyrics Not Found" ## No Lyrics Found
        musicListResultData["lyricsImage"].append(lyricsImage) ## Add Lyrics Image to List
        musicListResultData["lyricsHoverMessage"].append(lyricsHoverMessage) ## Add Lyrics Message to List
        ## Music Service
        if musicSub == "Apple Music": musicServiceImage = "musicSearchListenApple" ## Set Listening Link to Apple
        elif musicSub == "Spotify": musicServiceImage = "musicSearchListenSpotify" ## Set Listening Link to Spotify
        ## Song Window
        if (artistSearch == False or (artistSearch == True and geniusMusicSearchPrimeArtist.replace(" ", "-").split('(')[0].lower() == userInput.replace(" ", "-").split('(')[0].lower())) and geniusMusicSearchArtists.lower() not in ["spotify", "genius", "siriusxm the highway"] and "genius" not in geniusMusicSearchArtists.lower():
            if geniusMusicSearchDate != None: resultColumns += [[sg.Column([[sg.Image(png_data, background_color='#2b475d'), sg.Column([[sg.Text(str(geniusMusicSearchSongNameInfo), font='Any 16', background_color='#2b475d', tooltip=longSongNameInfo)], [sg.Text(str(geniusMusicSearchArtists), font='Any 14', background_color='#2b475d', tooltip=longArtists)], [sg.Text(str(geniusMusicSearchDate), font='Any 12', background_color='#2b475d')]], background_color='#2b475d', size=(400, 100)), sg.Push(background_color='#2b475d'), sg.Column([[sg.Image(str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\'+lyricsImage+'.png', background_color='#2b475d', tooltip=lyricsHoverMessage), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchGenius.png', border_width=0, button_color='#2b475d', key='searchmusicListSearchGenius_' + str(resultNumber), tooltip="Open Genius Page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\'+musicServiceImage+'.png', border_width=0, button_color='#2b475d', key='searchmusicListPlaySong_' + str(resultNumber), tooltip="Play Song"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\openView.png', border_width=0, button_color='#2b475d', key='searchMusicListOpenSong_' + str(resultNumber), tooltip="Open Result")]], background_color='#2b475d')]], background_color='#2b475d', size=(700, 100))]]
            else: resultColumns += [[sg.Column([[sg.Image(png_data, background_color='#2b475d'), sg.Column([[sg.Text(str(geniusMusicSearchSongNameInfo), font='Any 16', background_color='#2b475d', tooltip=longSongNameInfo)], [sg.Text(str(geniusMusicSearchArtists), font='Any 14', background_color='#2b475d', tooltip=longArtists)]], background_color='#2b475d', size=(400, 100)), sg.Push(background_color='#2b475d'), sg.Column([[sg.Image(str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\'+lyricsImage+'.png', background_color='#2b475d', tooltip=lyricsHoverMessage), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchGenius.png', border_width=0, button_color='#2b475d', key='searchmusicListSearchGenius_' + str(resultNumber), tooltip="Open Genius Page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\'+musicServiceImage+'.png', border_width=0, button_color='#2b475d', key='searchmusicListPlaySong_' + str(resultNumber), tooltip="Play Song"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\openView.png', border_width=0, button_color='#2b475d', key='searchMusicListOpenSong_' + str(resultNumber), tooltip="Open Result")]], background_color='#2b475d')]], background_color='#2b475d', size=(700, 100))]]
            musicListResultData["resultNumbers"].append(resultNumber)
        resultNumber += 1
        hitsFound -= 1
    if len(resultColumns) <= 8: musicListResultData["musicListLayout"] += [[sg.Column(resultColumns, scrollable=True, expand_x=True, background_color='#2b475d', vertical_scroll_only=True, size=(700, len(resultColumns)*110))]]
    else: musicListResultData["musicListLayout"] += [[sg.Column(resultColumns, scrollable=True, expand_x=True, background_color='#2b475d', vertical_scroll_only=True, size=(700, 880))]]
    musicListResultData["musicListLayout"] += [[sg.Push(background_color='#657076'), sg.Text("Music Search powered by Genius (" + str(len(resultColumns)) + " Results)", background_color='#657076', font='Any 11'), sg.Push(background_color='#657076')]] ## Credits
    ## Check if Any Good Results Found
    if len(musicListResultData["resultNumbers"]) == 0:
        print(f"[ERROR]: Music Search List: No results found")
        loadingAction = "No_Result_Found"
    elif len(musicListResultData["resultNumbers"]) == 1:
        print(f"[ERROR]: Music Search List: Only one result found")
        loadingAction = "Only_One_Result"
    else:
        try: ## Save Info to Cache
            musicListResultData["geniusMusicSearchExpireDate"] = str(datetime.date.today() + datetime.timedelta(days=10))
            pathlib.Path(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Music Search", "Music Search List Info")).mkdir(parents=True, exist_ok=True) ## Create Music Search List Info Cache Folder
            with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Cache", "Music Search", "Music Search List Info", userInput.lower().replace(" ", "").rsplit('/', 1)[-1] + ".json"), 'w') as file:
                json.dump({k: v for k, v in musicListResultData.items() if k not in ["musicListLayout"]}, file)
        except: pass
        print(f"[INFO]: Music Search List: Finished:")
        for key, value in musicListResultData.items():
            if key != "musicListLayout": print(f"{key}: {re.sub('[^A-z0-9 -]', '', str(value)).replace(" ", " ")}")
        loadingAction = "Search_Finished"

def geniusMusicSearchList(userInput, searchType="search"):
    global appSelected, loadingAction
    ## Set Local Variables
    try: musicSub = userSettingsData["musicService"]
    except: musicSub = "Apple Music"
    ## Loading Screen
    loadingPopup, loadingAction = sg.Window("", [[sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", background_color='#1b2838', key='loadingGIFImage')]], background_color='#1b2838', element_justification='c', no_titlebar=True, keep_on_top=True, finalize=True), "Start"
    loadingPopup.hide()
    loadingPopup.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - loadingPopup.size[0] // 2, HomeWindow.TKroot.winfo_y() + HomeWindow.TKroot.winfo_height() // 2 - loadingPopup.size[1] // 2)
    loadingPopup.un_hide()
    loadingPopup["loadingGIFImage"].UpdateAnimation(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", time_between_frames=10) ## Load Loading GIF
    while True:
        event, values = loadingPopup.read(timeout=10)
        loadingPopup["loadingGIFImage"].UpdateAnimation(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", time_between_frames=30) ## Load Loading GIF
        ## Actions from Thread
        if loadingAction == "Start": ## Start Music Search List Thread
            if searchType == "downloader": forceResult = "refresh"
            else: forceResult = False
            loadGeniusMusicListThread = threading.Thread(name="loadGeniusMusicList", target=loadGeniusMusicList, args=(userInput,forceResult,))
            loadGeniusMusicListThread.start()
            loadingAction = "Running"
        elif loadingAction == "No_Result_Found" and searchType == "downloader": ## No Music Search Result Found and Downloader
            musicListResultData["musicListLayout"] += [[sg.Column([[sg.Push(background_color='#2b475d'), sg.Text("No results were found!", background_color='#2b475d', font='Any 16 bold'), sg.Push(background_color='#2b475d')], [sg.Push(background_color='#2b475d'), sg.Text("Please enter a new search query in the search bar or close the window to not burn metadata to your song.", background_color='#2b475d', font='Any 12'), sg.Push(background_color='#2b475d')]], background_color='#2b475d', expand_x=True)]]
            musicListResultData["musicListLayout"] += [[sg.Column([[sg.Push(background_color='#2b475d'), sg.Text("Burn your own metadata:", background_color='#2b475d', font='Any 16 bold'), sg.Push(background_color='#2b475d')], [sg.Push(background_color='#2b475d'), sg.Button("Open Metadata Burner app", button_color='#2b475d', font='Any 12', key='openMetadataBurnerApp'), sg.Push(background_color='#2b475d')]], background_color='#2b475d', expand_x=True)]]
            loadingPopup.close() ## Close Loading Popup
            break
        elif loadingAction == "No_Result_Found": ## No Music Search Result Found
            loadingPopup.close() ## Close Loading Popup
            popupMessage("No Search Result", "", "fail")
            return
        elif "Genius_Page_Down:" in loadingAction: ## Genius's Service is Down (Special Error)
            loadingPopup.close() ## Close Loading Popup
            popupMessage("Music Search Error", loadingAction.split("Genius_Page_Down:",1)[1] + "\t\t\t\t\tPlease try again later.", "error")
            return
        elif loadingAction == "Genius_Page_Down": ## Genius's Service is Down
            loadingPopup.close() ## Close Loading Popup
            popupMessage("Music Search Error", "Genius is currently unavailable.\t\t\t\t\tPlease try again later.", "error")
            return
        elif loadingAction == "Genius_Robot_Check": ## Genius is Checking Robot
            loadingPopup.close() ## Close Loading Popup
            popupMessage("Music Search Error", "Genius suspects automated activity.\t\t\t\t\tPlease disable your VPN.", "error")
            return
        elif loadingAction == "Only_One_Result": ## Only One Result Found, Open It
            loadingPopup.close()
            geniusMusicSearch(musicListResultData["geniusSongIDs"][0], True, searchType)
            return
        elif loadingAction == "Search_Finished": ## Show Music Search List Window
            loadingPopup.close()
            break
    MusicSearchListWindow = sg.Window("Music Search - List Results", musicListResultData["musicListLayout"], background_color='#657076', finalize=True, resizable=True, keep_on_top=False, element_justification='l')
    MusicSearchListWindow.TKroot.minsize(700, 310)
    MusicSearchListWindow.hide()
    MusicSearchListWindow.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - MusicSearchListWindow.size[0] // 2, HomeWindow.TKroot.winfo_y() + HomeWindow.TKroot.winfo_height() // 2 - MusicSearchListWindow.size[1] // 2)
    if MusicSearchListWindow.CurrentLocation()[1] < 200: MusicSearchListWindow.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - MusicSearchListWindow.size[0] // 2, 25) ## Fix Over Top
    MusicSearchListWindow.un_hide()
    ## Window Shortcuts
    MusicSearchListWindow.bind('<Delete>', '_Delete')                               ## Close Window shortcut
    MusicSearchListWindow['geniusMusicListSearchInput'].bind('<Return>', '_Enter')  ## Enter on Song Search
    ## Mouse Icon Changes
    MusicSearchListWindow["geniusMusicListSearchButton"].Widget.config(cursor="hand2")  ## Change Search Button Hover icon
    for resultNumber in musicListResultData["resultNumbers"]:
        MusicSearchListWindow["searchmusicListSearchGenius_" + str(resultNumber)].Widget.config(cursor="hand2")  ## Genius Page Hover icon
        MusicSearchListWindow["searchmusicListPlaySong_" + str(resultNumber)].Widget.config(cursor="hand2")      ## Listen Music Hover icon
        MusicSearchListWindow["searchMusicListOpenSong_" + str(resultNumber)].Widget.config(cursor="hand2")      ## Open Song Hover icon
    while True:
        event, values = MusicSearchListWindow.read()
        if event == sg.WIN_CLOSED or (event == '_Delete'): ## Window Closed
            MusicSearchListWindow.close()
            break
        elif (event == 'geniusMusicListSearchButton' or (event == 'geniusMusicListSearchInput' + '_Enter')) and values['geniusMusicListSearchInput'].replace(" ", "-") != userInput: ## Change Search
            MusicSearchListWindow.close()
            geniusMusicSearchList(values['geniusMusicListSearchInput'].lower().replace(" by ", "-"), searchType)
            break
        elif 'searchmusicListSearchGenius' in event: webbrowser.open(musicListResultData["geniusURLs"][int(event.split("_")[-1])], new=2, autoraise=True) ## Open Genius Page
        elif 'searchmusicListPlaySong_' in event: ## Play Song Online
            if musicSub == "Apple Music": webbrowser.open("https://music.apple.com/us/search?term=" + musicListResultData["songArtists"][int(event.split("_")[-1])].replace(" ", "%20") + "%20" + musicListResultData["songNames"][int(event.split("_")[-1])].replace(" ", "%20"), new=2, autoraise=True)
            elif musicSub == "Spotify": webbrowser.open("https://open.spotify.com/search/" + musicListResultData["songArtists"][int(event.split("_")[-1])].replace(" ", "%20") + "%20" + musicListResultData["songNames"][int(event.split("_")[-1])].replace(" ", "%20"), new=2, autoraise=True)
        elif 'searchMusicListOpenSong' in event: ## Open Song in Music Search
            try: HomeWindow.Element('musicSearchPanel_songSearchInput').Update(musicListResultData["songNames"][int(event.split("_")[-1])] + " - " + musicListResultData["songArtists"][int(event.split("_")[-1])])
            except: pass
            MusicSearchListWindow.close()
            geniusMusicSearch(musicListResultData["geniusSongIDs"][int(event.split("_")[-1])], True, searchType)
            break
        elif event == 'openMetadataBurnerApp':
            appSelected = "Metadata_Burner"
            HomeWindow['metadataBurnerPanel'].update(visible=True)
            HomeWindow['musicDownloaderPanel'].update(visible=False)
            HomeWindow.Element('metadataBurnerPanel_songLocationInput').Update(metadataInfo["metadataBurnLocation"])
            for key in ['metadataBurnerPanel_songNameInput', 'metadataBurnerPanel_songArtistInput', 'metadataBurnerPanel_songAlbumInput', 'metadataBurnerPanel_songYearInput', 'metadataBurnerPanel_songGenreInput', 'metadataBurnerPanel_albumCurrentLengthInput', 'metadataBurnerPanel_albumTotalLengthInput', 'metadataBurnerPanel_songPublisherInput', 'metadataBurnerPanel_songArtworkInput', 'metadataBurnerPanel_lyricsInput']: HomeWindow.Element(key).Update("")
            MusicSearchListWindow.close()
            break


## Start System       
if filesVerified:     
    try: softwareSetup()
    except Exception as Argument: crashMessage("Error 00: " + str(Argument))