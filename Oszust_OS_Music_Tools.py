## Oszust OS Music Tools - Oszust Industries
## Created on: 1-02-23 - Last update: 5-17-24
softwareVersion = "v1.2.2"
systemName, systemBuild = "Oszust OS Music Tools", "dev"
import bs4, cloudscraper, ctypes, datetime, eyed3, io, json, math, os, pathlib, platform, psutil, pyuac, re, requests, textwrap, threading, time, urllib.request, webbrowser, win32clipboard
from moviepy.editor import *
from PIL import Image
from pytube import YouTube
import PySimpleGUI as sg
import AutoUpdater

def softwareConfig():
    ## System Configuration
    global userSettingsData
    try: ## Try opening exisiting setting file
        with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Settings.json"), 'r') as file: userSettingsData = json.load(file)
        if userSettingsData["firstSoftwareUse"] != None: pass
    except: ## Create new file and assign default values
        userSettingsData = { ## Default Data
            "firstSoftwareUse": True, ## First use of Music Tools
            "musicSearchContract": False, ## Has the user accepted the Music Downloader contract
            "musicService": "Apple Music", ## User's preferred music service
        }
        with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Settings.json"), 'w') as file: json.dump(userSettingsData, file)

def softwareSetup():
    global topSongsList
    ## Setup Commands
    print("Loading...\nLaunching Interface...")
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0) ## Hides the console
    pathlib.Path(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "cache")).mkdir(parents=True, exist_ok=True) ## Create cache folder in appdata
    if systemBuild != "dev": ## Redirects the output to a txt file
        try: os.remove(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "outputLog.txt"))
        except: pass
        output = open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "outputLog.txt"), "wt")
        sys.stdout = output
        sys.stderr = output
    ## Get User's Configs
    softwareConfig() 
    ## Check WIFI
    checkInternetstatusThread = threading.Thread(name="checkInternetstatus", target=checkInternetstatus)
    checkInternetstatusThread.start()
    ## Billboard Top 100 Hits from Cache
    try:
        billboardCache, index, topSongsList = (open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "cache", "Billboard.txt"), "r")).read().split("\n"), 1, []
        if datetime.datetime.strptime(billboardCache[0], '%Y-%m-%d') + datetime.timedelta(days=7) >= datetime.datetime.now(): ## Check if cache is >= week
            if billboardCache[2][0] == "2": loadingScreen("Billboard_List_Download", False) ## Old Billboard Data
            while index < len(billboardCache):
                if index + 1 < len(billboardCache):
                    topSongsList.append([billboardCache[index].strip(), billboardCache[index + 1].strip()])
                    index += 2
                else: break ## Get list from cache
        else: loadingScreen("Billboard_List_Download", False) ## Download Billboard Data
    except: loadingScreen("Billboard_List_Download", False) ## Download Billboard Data
    ## Retrieve Profanity Engine Definitions
    loadProfanityEngineDefinitions(False)
    ## AutoUpdater
    checkAutoUpdater("setup")

def crashMessage(message):
    RightClickMenu = ['', ['Copy']] ## Right Click Menu - Crash Message
    errorWindow = sg.Window(message.split(':')[0], [[sg.Text(systemName + " has crashed.", font=("Any", 13))], [sg.Multiline(message, size=(50,5), font=("Any", 13), disabled=True, autoscroll=False, right_click_menu=RightClickMenu, key='crashMessageErrorCodeText')], [sg.Button("Report Error", button_color=("White", "Blue"), key='Report'), sg.Button("Quit", button_color=("White", "Red"), key='Quit')]], resizable=False, finalize=True, keep_on_top=True, element_justification='c')
    errorLine:sg.Multiline = errorWindow['crashMessageErrorCodeText']
    ## Window Shortcuts
    errorWindow.bind('<Insert>', '_Insert')  ## Report Error shortcut
    errorWindow.bind('<Delete>', '_Delete')  ## Close Window shortcut
    ## Mouse Icon Changes
    for key in ['Report', 'Quit']: errorWindow[key].Widget.config(cursor="hand2") ## Hover icons
    while True:
        event, values = errorWindow.read(timeout=10)
        if event == sg.WIN_CLOSED or event == 'Quit' or (event == '_Delete'): break
        elif event == 'Report' or (event == '_Insert'): webbrowser.open("https://github.com/Oszust-Industries/" + systemName.replace(" ", "-") + "/issues/new", new=2, autoraise=True)
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
            wifiStatus = True
            urllib.request.urlopen("http://google.com", timeout=3)
        except: wifiStatus = False
        time.sleep(10)

def downloadTop100Songs():
    global loadingStatus, topSongsList
    try:
        import billboard
        chart, topSongsList = billboard.ChartData('hot-100', fetch=True, max_retries=3, timeout=25), []
        for position, song in enumerate(chart):
            try:
                if song.weeks == 1: topSongsList.append([f"{position + 1}. {song.title} - {song.artist}", "NEW"])
                elif song.lastPos > song.rank: topSongsList.append([f"{position + 1}. {song.title} -  {song.artist}", str(song.weeks) + ("     ^" if song.weeks <= 9 else "   ^")])
                elif song.lastPos == song.rank: topSongsList.append([f"{position + 1}. {song.title} -  {song.artist}", str(song.weeks) + ("     ^" if song.weeks <= 9 else "   -")])
                elif song.lastPos < song.rank: topSongsList.append([f"{position + 1}. {song.title} -  {song.artist}", str(song.weeks) + ("     ^" if song.weeks <= 9 else "   v")])
            except: topSongsList.append(f"{position + 1}. Result Failed to Load.", "N/A")
        try: ## Cache the List
            with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "cache", "Billboard.txt"), "w") as billboardTextFile:  # Create Cache File
                lastTuesday = datetime.date.today() - datetime.timedelta(days=(datetime.date.today().weekday() - 1) % 7)  # Data is fresh on Tuesday
                billboardTextFile.write(str(lastTuesday))
                for sublist in topSongsList:
                    for item in sublist: billboardTextFile.write("\n" + item)
        except: pass
    except: topSongsList = [["Billboard Top 100 Failed to Load.", "N/A"]]
    loadingStatus = "Done"

def loadProfanityEngineDefinitions(downloadList):
    global profanityEngineDefinitions
    try:
        if downloadList:
            profanityEngineDefinitions = []
            try:
                pathlib.Path(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "cache", "Profanity Engine")).mkdir(parents=True, exist_ok=True) ## Create Profanity Engine Cache Folder
                ## Read default Profanity Engine Definitions
                with open(os.path.join(pathlib.Path(__file__).resolve().parent, "data", "Default data", "profanityEngineDefaults.json"), 'r') as file: data = json.load(file)
                for category, value in data['categories'].items(): profanityEngineDefinitions.extend(value)
                ## Write Definitions to User save
                try:
                    with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "cache", "Profanity Engine", "userDefinitions.txt"), 'w') as file:
                        for item in profanityEngineDefinitions: file.write(item + '\n')
                except: pass
            except: profanityEngineDefinitions = "Failed"
        else:
            try:
                with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "cache", "Profanity Engine", "userDefinitions.txt"), 'r') as file: lines = file.readlines()
                profanityEngineDefinitions = [line.strip() for line in lines]
                if len(profanityEngineDefinitions) == 0: loadProfanityEngineDefinitions(True)
            except: loadProfanityEngineDefinitions(True)
    except: profanityEngineDefinitions = "Failed"

def checkAutoUpdater(command):
    try: AutoUpdaterDate = (open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "cache", "AutoUpdaterDate.txt"), "r")).read().split("\n")
    except: AutoUpdaterDate = [str(datetime.date.today() - datetime.timedelta(days=3)), "Missing File"]
    if (datetime.datetime.strptime(AutoUpdaterDate[0], '%Y-%m-%d') <= datetime.datetime.now() and systemBuild.lower() not in ["dev", "main"] and wifiStatus) or (command == "check" and wifiStatus):
        try: newestVersion = ((requests.get("https://api.github.com/repos/Oszust-Industries/" + systemName.replace(" ", "-") + "/releases/latest")).json())['tag_name']
        except: newestVersion = "Failed"
        if newestVersion != softwareVersion and newestVersion != "Failed":
            if not pyuac.isUserAdmin():
                response = popupMessage("New Update Available", "A new version " + newestVersion + " is now available for " + systemName + ". Would you like to update now?", "downloaded")
                if response == True:
                    try:
                        try:
                            os.remove(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "cache", "AutoUpdaterDate.txt"))
                            HomeWindow.close()
                        except: pass
                        pyuac.runAsAdmin()
                    except:
                        if command == "check": popupMessage("AutoUpdater", "Failed to launch the software with administrator privileges.", "error")
                        else: homeScreen()
                else:
                    try: ## Cache the Next Date
                        with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "cache", "AutoUpdaterDate.txt"), "w") as AutoUpdaterDateFile: ## Create Cache File
                            if response == "Week": AutoUpdaterDateFile.write(str(datetime.date.today() + datetime.timedelta(days=7)))
                            else: AutoUpdaterDateFile.write(str(datetime.date.today() + datetime.timedelta(days=1)))
                            AutoUpdaterDateFile.close()
                    except: pass
                    if command == "check": pass
                    else: homeScreen()
            else:
                AutoUpdater.main(systemName, systemBuild, softwareVersion, newestVersion)
        elif newestVersion == "Failed" and command == "check": ## GitHub Error
            popupMessage("AutoUpdater", "There was an error while trying to fetch the latest version of  " + systemName + ".", "error")
            homeScreen()
        else: ## On Newest Version
            try: ## Cache the Next Date
                with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "cache", "AutoUpdaterDate.txt"), "w") as AutoUpdaterDateFile: ## Create Cache File
                    AutoUpdaterDateFile.write(str(datetime.date.today() + datetime.timedelta(days=1)))
                    AutoUpdaterDateFile.close()
            except: pass
            if command == "check": popupMessage("AutoUpdater", "You are already using the latest version of " + systemName + ".", "success")
            else: homeScreen()
    else: homeScreen()
    
def homeScreenAppPanels():
    ## Extra Apps Panel Creator
    global toolPanelApps
    ## Set Local Variables
    try: musicSub = userSettingsData["musicService"]
    except: musicSub = "Apple Music"
    if wifiStatus: toolsPanel, toolPanelAppLocation, toolPanelApps, toolsPanelRow = [[]], 0, ["Music Search", "Music Downloader", "Youtube Downloader", "Lyrics Checker", "Profanity Engine", "Settings"], []
    else: toolsPanel, toolPanelAppLocation, toolPanelApps, toolsPanelRow = [[]], 0, ["Lyrics Checker", "Profanity Engine", "Settings"], []
    #["Music Search", "Music Downloader", "Youtube Downloader", "Metadata Burner", "CD Burner", "Music Player", "Lyrics Checker", "Profanity Engine", "Settings"] ## Future toolPanelApps
    for toolsPanelRowNumber in range(math.ceil(len(toolPanelApps)/6)):
        try:
            for app in range(toolPanelAppLocation, 6*(toolsPanelRowNumber+1)): toolsPanelRow.append(toolPanelApps[app])
        except: pass
        toolsPanel += [[sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\Tool icons\\' + app[0].lower() + app[1:].replace(" ", "") + '.png', border_width=0, button_color='#657076', key='musicTool_' + app.replace(" ", "_"), tooltip="Open " + app)]], background_color='#657076', pad=((10,10), (10, 10))) for app in toolsPanelRow]]
        toolsPanelRow = []
        toolPanelAppLocation += 6
    ## Listboxes
    topSongsListBoxed = [[sg.Table(values=topSongsList, headings=('Songs' + " "*39, 'Weeks'), num_rows=16, auto_size_columns=True, enable_events=True, background_color='white', text_color='black', justification='l', key='musicSearchPanel_billboardTopSongsList')]]
    profanityEngineListBoxed = [[sg.Listbox([item.replace("~", "'") for item in profanityEngineDefinitions], size=(25, 17), horizontal_scroll=True, select_mode=None, enable_events=True, highlight_background_color='blue', highlight_text_color='white', key='profanityEnginePanel_definitionsList')]]
    ## Music Search Panel [Default]
    return [[sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("Music Search:", font='Any 20 bold', justification='c', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Text("Search:", font='Any 16', background_color='#2B475D'), sg.Input(do_not_clear=True, size=(45,1), font='Any 11', enable_events=True, key='musicSearchPanel_songSearchInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\search.png', border_width=0, button_color='#2B475D', key='musicSearchPanel_normalSongSearchButton', tooltip="Search Music"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\listSearch.png', border_width=0, button_color='#2B475D', key='musicSearchPanel_listSongSearchButton', tooltip="Music Search - All Results"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clearInput.png', border_width=0, button_color='#2B475D', key='musicSearchPanel_clearSongSearchInputButton', tooltip="Clear Search")],
    [sg.Frame("The Billboard Hot 100", topSongsListBoxed, relief='flat', background_color='#2B475D', key='topSongsListFrame'), sg.Push(background_color='#2B475D')]], pad=((0,0), (0, 0)), background_color='#2B475D', visible=True, key='musicSearchPanel'),
    ## Music Downloader Panel
     sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\help.png', border_width=0, button_color='#2B475D', key='musicDownloaderPanel_helpButton'), sg.Push(background_color='#2B475D'), sg.Text("Music Downloader:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Text("", size=(5, 1), background_color='#2B475D')],
    [sg.Text("YouTube Link:", font='Any 13', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(48,1), enable_events=True, key='musicDownloaderPanel_youtubeUrlInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clipboard.png', border_width=0, button_color='#2B475D', key='musicDownloaderPanel_pasteClipboardButton', tooltip="Paste Link"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\openYoutube.png', border_width=0, button_color='#2B475D', key='musicDownloaderPanel_openYoutubeButton', tooltip="Open YouTube")],
    [sg.Text("Download Location:", font='Any 13', background_color='#2B475D'), sg.Input(str(pathlib.Path.home() / "Downloads"), do_not_clear=True, size=(50,1), enable_events=True, key='musicDownloaderPanel_downloadLocationInput'), sg.FolderBrowse(key='musicDownloaderPanel_fileBrowseButton')],
    [sg.HorizontalSeparator()], [sg.Push(background_color='#2B475D'), sg.Text("Downloader Settings:", font='Any 15', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\reset.png', border_width=0, button_color='#2B475D', key='musicDownloaderPanel_resetSettings', tooltip="Reset Settings")],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\true.png', border_width=0, button_color='#2B475D', key='musicDownloaderPanel_burnLyricsCheckbox'), sg.Text("Burn lyrics to the audio file", font='Any 14', background_color='#2B475D')],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\false.png', border_width=0, button_color='#2B475D', key='musicDownloaderPanel_compilationCheckbox'), sg.Text("Song's album is a compilation by various artists", font='Any 14', background_color='#2B475D')],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\false.png', border_width=0, button_color='#2B475D', key='musicDownloaderPanel_changeNameCheckbox'), sg.Text("Custom rename to:", font='Any 14', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(36,1), enable_events=True, visible=False, key='musicDownloaderPanel_changeNameInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clipboard_Small.png', border_width=0, button_color='#2B475D', visible=False, key='musicDownloaderPanel_changeNameClipboard', tooltip="Paste Link"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clearInput.png', border_width=0, button_color='#2B475D', visible=False, key='musicDownloaderPanel_changeNameClearInput', tooltip="Clear Input")],
    [sg.HorizontalSeparator()], [sg.Text("", font='Any 4', background_color='#2B475D')], [sg.Push(background_color='#2B475D'), sg.Button("Download", button_color=("White", "Blue"), font='Any 15', size=(10, 1), key='musicDownloaderPanel_downloadButton'), sg.Push(background_color='#2B475D')]], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='musicDownloaderPanel'),
    ## YouTube Downloader Panel
     sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("YouTube Downloader:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Text("YouTube Link:", font='Any 13', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(48,1), enable_events=True, key='youtubeDownloaderPanel_youtubeUrlInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clipboard.png', border_width=0, button_color='#2B475D', key='youtubeDownloaderPanel_pasteClipboardButton', tooltip="Paste Link"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\openYoutube.png', border_width=0, button_color='#2B475D', key='youtubeDownloaderPanel_openYoutubeButton', tooltip="Open YouTube")],
    [sg.Text("Download Location:", font='Any 13', background_color='#2B475D'), sg.Input(str(pathlib.Path.home() / "Downloads"), do_not_clear=True, size=(50,1), enable_events=True, key='youtubeDownloaderPanel_downloadLocationInput'), sg.FolderBrowse(key='youtubeDownloaderPanel_fileBrowseButton')],
    [sg.HorizontalSeparator()], [sg.Push(background_color='#2B475D'), sg.Text("Downloader Settings:", font='Any 15', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\reset.png', border_width=0, button_color='#2B475D', key='youtubeDownloaderPanel_resetSettings', tooltip="Reset Settings")],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\false.png', border_width=0, button_color='#2B475D', key='youtubeDownloaderPanel_audioDownloadCheckbox'), sg.Text("Download audio file (.MP3) of the YouTube Video", font='Any 14', background_color='#2B475D')],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\true.png', border_width=0, button_color='#2B475D', key='youtubeDownloaderPanel_videoDownloadCheckbox'), sg.Text("Download video file (.MP4) of the YouTube Video", font='Any 14', background_color='#2B475D')],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\false.png', border_width=0, button_color='#2B475D', key='youtubeDownloaderPanel_changeNameCheckbox'), sg.Text("Rename download to:", font='Any 14', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(33,1), enable_events=True, visible=False, key='youtubeDownloaderPanel_changeNameInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clipboard_Small.png', border_width=0, button_color='#2B475D', visible=False, key='youtubeDownloaderPanel_changeNameClipboard', tooltip="Paste Clipboard"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clearInput.png', border_width=0, button_color='#2B475D', visible=False, key='youtubeDownloaderPanel_changeNameClearInput', tooltip="Clear Input")],
    [sg.HorizontalSeparator()], [sg.Text("", font='Any 4', background_color='#2B475D')], [sg.Push(background_color='#2B475D'), sg.Button("Download", button_color=("White", "Blue"), font='Any 15', size=(10, 1), key='youtubeDownloaderPanel_downloadButton'), sg.Push(background_color='#2B475D')]], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='youtubeDownloaderPanel'),
    ## Metadata Burner Panel
    sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("Metadata Burner:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')]
    ], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='metadataBurnerPanel'),
     ## CD Burner Panel
    sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("CD Burner:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')]
    ], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='cdburnerPanel'),
    ## Music Player Panel
    sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("Music Player:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')]
    ], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='musicPlayerPanel'),
    ## Extra Apps Panel
    # Side bar button - sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\sidebar.png', border_width=0, button_color='#2B475D', key='musicToolsPanel_moveSidebarButton'), sg.Push(background_color='#2B475D'), sg.Text("All Music Tools:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("All Music Tools:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Column(toolsPanel, size=(595,390), pad=((10,10), (10, 10)), background_color='#2B475D')]], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='musicToolsPanel'),
    ## Settings Panel
    sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("Settings:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Frame("User Preferences", [[sg.Push(background_color='#2B475D'), sg.Text("Music Service:", background_color='#2B475D'), sg.Combo(('Apple Music', 'Spotify'), readonly=True, default_value=musicSub, key='settingsPanel_musicServiceCombo'), sg.Push(background_color='#2B475D')]], size=(580, 60), background_color='#2B475D')],
    [sg.Frame("Cache Management", [[sg.Push(background_color='#2B475D'), sg.Text(str(round(getDirSize(str(os.getenv('APPDATA')) + "\\Oszust Industries\\Oszust OS Music Tools\\cache\\") / (1024 * 1024), 2)) + " MB", background_color='#2B475D', key='settingsPanel_cacheStorageText'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\clean.png', border_width=0, button_color='#2B475D', key='settingsPanel_cleanCacheButton', tooltip="Clean Cache Storage"), sg.Push(background_color='#2B475D')]], size=(580, 60), background_color='#2B475D')],
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
    global HomeWindow, homeWindowLocationX, homeWindowLocationY, profanityEngineDefinitions
    ## Oszust OS Music Tools List
    if wifiStatus: applist, apps = [[]], ["Music Search", "Music Downloader", "Youtube Downloader", "Profanity Engine", "Music Tools", "Settings"]
    else: applist, apps = [[]], ["Lyrics Checker", "Profanity Engine", "Music Tools", "Settings"]
    for app in apps: applist += [[sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent) + "\\data\\App icons\\" + app.lower().replace(" ", "") + ".png", button_color='#657076', border_width=0, key=app.replace(" ", "_") + '_AppSelector', tooltip='Open ' + app)]], pad=((5,5), (5, 5)), background_color='#657076')]] ## Add Apps to Side Panel
    ## Home Window
    layout = [[sg.Column(applist, size=(72,390), pad=((10,10), (10, 10)), background_color='#2B475D', scrollable=False, vertical_scroll_only=True), sg.Column(homeScreenAppPanels(), size=(595,390), pad=((10,10), (10, 10)), background_color='#2B475D', scrollable=False, vertical_scroll_only=True)]]
    if wifiStatus: layout += [[sg.Column([[sg.Text(platform.system() + " | " + softwareVersion + " | " + systemBuild + " | Online", enable_events=True, font='Any 13', background_color='#5A6E80', key='versionTextHomeBottom', tooltip="View Changelog and Check Updates"), sg.Push(background_color='#5A6E80'), sg.Text("Oszust Industries", enable_events=True, font='Any 13', background_color='#5A6E80', key='creditsTextHomeBottom')], [sg.Column([[]], size=(710, 1), pad=(0,0))]], size=(710, 30), pad=(0,0), background_color='#5A6E80')]]
    else: layout += [[sg.Column([[sg.Text(platform.system() + " | " + softwareVersion + " | " + systemBuild + " | Offline", enable_events=True, font='Any 13', background_color='#5A6E80', key='versionTextHomeBottom'), sg.Push(background_color='#5A6E80'), sg.Text("Oszust Industries", enable_events=True, font='Any 13', background_color='#5A6E80', key='creditsTextHomeBottom')], [sg.Column([[]], size=(710, 1), pad=(0,0))]], size=(710, 30), pad=(0,0), background_color='#5A6E80')]]
    windowSize = ((int((-4*(ctypes.windll.shcore.GetScaleFactorForDevice(0))+1060) * (ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100)), int((-4*(ctypes.windll.shcore.GetScaleFactorForDevice(0))+800) * (ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100))))
    HomeWindow = sg.Window('Oszust OS Music Tools', layout, size=windowSize, background_color='#657076', margins=(0,0), finalize=True, resizable=False, text_justification='r')
    HomeWindow.TKroot.minsize(710, 440)
    ## Music Search: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    HomeWindow['musicSearchPanel_billboardTopSongsList'].bind('<Return>', '_Enter')  ## Enter on Top 100 list
    HomeWindow['musicSearchPanel_songSearchInput'].bind('<Return>', '_Enter')        ## Enter on Song Search
    for key in ['normalSongSearchButton', 'listSongSearchButton', 'clearSongSearchInputButton', 'billboardTopSongsList']: HomeWindow['musicSearchPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## Settings: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    for key in ['saveButton']: HomeWindow['settingsPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## Music Downloader: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    musicBurnLyrics, musicCompilationAlbum, musicDownloadName = True, False, False ## App Variables
    for key in ['pasteClipboardButton', 'openYoutubeButton', 'fileBrowseButton', 'resetSettings', 'burnLyricsCheckbox', 'compilationCheckbox', 'changeNameCheckbox', 'changeNameClipboard', 'changeNameClearInput', 'downloadButton']: HomeWindow['musicDownloaderPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## YouTube Downloader: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    youtubeAudioDownload, youtubeVideoDownload, youtubeDownloadName = False, True, False ## App Variables
    for key in ['pasteClipboardButton', 'openYoutubeButton', 'fileBrowseButton', 'resetSettings', 'audioDownloadCheckbox', 'videoDownloadCheckbox', 'changeNameCheckbox', 'changeNameClipboard', 'changeNameClearInput', 'downloadButton']: HomeWindow['youtubeDownloaderPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## Lyrics Checker: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    for key in ['openWebButton', 'pasteClipboardButton', 'clearInputButton', 'checkLyricsButton']: HomeWindow['lyricsCheckerPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## Profanity Engine Editor: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    for key in ['definitionsList', 'searchClearInput', 'sortButton', 'importButton', 'exportButton', 'clearButton', 'swearPredefinedWords', 'alcoholPredefinedWords', 'drugsVapePredefinedWords', 'sexPredefinedWords', 'otherPredefinedWords', 'saveEditButton', 'deleteWordButton', 'newWordButton']: HomeWindow['profanityEnginePanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## Music Tools: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    for key in toolPanelApps: HomeWindow['musicTool_' + key.replace(" ", "_")].Widget.config(cursor="hand2") ## Hover icons
    ## Main Window: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    if wifiStatus:
        appSelected = "Music_Search" ## App Variables
        for key in ['versionTextHomeBottom', 'creditsTextHomeBottom']: HomeWindow[key].Widget.config(cursor="hand2") ## Hover icons
    else:
        appSelected = "Music_Tools" ## App Variables
        HomeWindow['musicToolsPanel'].update(visible=True)
        HomeWindow['musicSearchPanel'].update(visible=False)
    if userSettingsData["firstSoftwareUse"]:
        popupMessage("Welcome to Music Tools!", "Explore the pinned apps on the left sidebar. Look for blue buttons marked with question marks for assistance. Access more tools in the drawer by clicking the nine-square icon.", "help") ## First Software Launch Popup
        savingSettings("firstSoftwareUse", False)
    for app in apps: HomeWindow[app.replace(" ", "_") + "_AppSelector"].Widget.config(cursor="hand2") ## App Side Panel hover icons
    ## Reading Home Window
    while True:
        event, values = HomeWindow.read(timeout=10)
        homeWindowLocationX, homeWindowLocationY = HomeWindow.CurrentLocation() ## X & Y Location of Home Window
## Internet Status Changes
        HomeWindow['versionTextHomeBottom'].update(f"{platform.system()} | {softwareVersion} | {systemBuild} | {'Online' if wifiStatus else 'Offline'}")
## Closed Window
        if event == sg.WIN_CLOSED or event == 'Exit':
            HomeWindow.close()
            thisSystem = psutil.Process(os.getpid()) ## Close Program
            thisSystem.terminate()
            break
## Home Screen Bottom Text
        elif event == 'versionTextHomeBottom' and wifiStatus: ## Home Screen: Version Text
            webbrowser.open("https://github.com/Oszust-Industries/" + systemName.replace(" ", "-") + "/releases", new=2, autoraise=True)
            checkAutoUpdater("check")
        elif event == 'creditsTextHomeBottom' and wifiStatus: webbrowser.open("https://github.com/Oszust-Industries/", new=2, autoraise=True) ## Home Screen: Credits Button
## Side Panel Apps (Buttons)
        elif "_AppSelector" in event and event.replace("_AppSelector", "") != appSelected:
            appSelected = event.replace("_AppSelector", "")
            for app in toolPanelApps:
                if app.replace(" ", "_") == appSelected: HomeWindow[(app[:4].lower() + app[4:]).replace(" ", "") + "Panel"].update(visible=True)
                else: HomeWindow[(app[:4].lower() + app[4:]).replace(" ", "") + "Panel"].update(visible=False)
            if appSelected == "Music_Tools": HomeWindow["musicToolsPanel"].update(visible=True) ## Show Music Tools Window
            elif appSelected != "Music_Tools": HomeWindow["musicToolsPanel"].update(visible=False) ## Hide Music Tools Window
            if appSelected == "Settings": HomeWindow.Element('settingsPanel_cacheStorageText').Update(str(round(getDirSize(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "cache")) / (1024 * 1024), 2)) + " MB")
## Music Tools
        elif appSelected == "Music_Tools":
            if "musicTool_" in event:
                appSelected = event.replace("musicTool_", "")
                for tool in toolPanelApps:
                    if tool.replace(" ", "_") == appSelected: HomeWindow[(tool[:4].lower() + tool[4:]).replace(" ", "") + "Panel"].update(visible=True)
                    else: HomeWindow[(tool[:4].lower() + tool[4:]).replace(" ", "") + "Panel"].update(visible=False)
                HomeWindow["musicToolsPanel"].update(visible=False)
## Settings (Buttons/Events)
        elif appSelected == "Settings":
            if event == 'settingsPanel_saveButton':
                savingSettings("musicService", values['settingsPanel_musicServiceCombo'])
            elif event == 'settingsPanel_cleanCacheButton':
                if popupMessage("Cache Cleaner Confirmation", "Are you sure you want to delete all software cache?", "confirmation"):
                    try:
                        try:
                            for item in os.listdir(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "cache", "Music Search", "Artworks")):
                                os.remove(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "cache", "Music Search", "Artworks", item))
                            os.rmdir(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "cache", "Music Search", "Artworks"))
                        except: pass
                        for item in os.listdir(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "cache", "Music Search")):
                            os.remove(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "cache", "Music Search", item))
                        HomeWindow.Element('settingsPanel_cacheStorageText').Update(str(round(getDirSize(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "cache")) / (1024 * 1024), 2)) + " MB")
                        popupMessage("Settings", "Cache has been successfully cleaned.", "success")
                    except: popupMessage("Settings", "Unable to clean the cache.", "error")
## Music Search (Buttons/Events)
        elif appSelected == "Music_Search":
            if (event == 'musicSearchPanel_normalSongSearchButton' or (event == 'musicSearchPanel_songSearchInput' + '_Enter')) and values['musicSearchPanel_songSearchInput'].replace(" ","").lower() not in ["", "resultfailedtoload", "billboardtop100failedtoload"]: geniusMusicSearch(values['musicSearchPanel_songSearchInput'], False) ## Music Search
            elif event == 'musicSearchPanel_listSongSearchButton' and values['musicSearchPanel_songSearchInput'].replace(" ","").lower() not in ["", "resultfailedtoload", "billboardtop100failedtoload"]: geniusMusicSearchList(values['musicSearchPanel_songSearchInput']) ## Music Search All Results
            elif event == 'musicSearchPanel_clearSongSearchInputButton': HomeWindow.Element('musicSearchPanel_songSearchInput').Update("") ## Clear Music Search Input
            elif event == 'musicSearchPanel_billboardTopSongsList' and HomeWindow['musicSearchPanel_billboardTopSongsList'].get()[values['musicSearchPanel_billboardTopSongsList'][0]][0].split(". ", 1)[1].split("   (", 1)[0].replace(" ","").lower() not in ["", "resultfailedtoload", "billboardtop100failedtoload"]: HomeWindow.Element('musicSearchPanel_songSearchInput').Update(HomeWindow['musicSearchPanel_billboardTopSongsList'].get()[values['musicSearchPanel_billboardTopSongsList'][0]][0].split(". ", 1)[1].split("   (", 1)[0]) ## Copy Top 100 to Music Search
            elif (event == 'musicSearchPanel_billboardTopSongsList' + '_Enter'): geniusMusicSearch(values['musicSearchPanel_billboardTopSongsList'][0].split(". ", 1)[1].split("   (", 1)[0], False) ## Top 100 Song Search
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
            elif event == 'musicDownloaderPanel_downloadButton': ## Download Music Button
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
            elif event == 'youtubeDownloaderPanel_downloadButton': ## Download YouTube Button
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
            elif event == 'lyricsCheckerPanel_clearInputButton': ## Clear Lyrics Input
                HomeWindow.Element('lyricsCheckerPanel_lyricsInput').Update("")
                HomeWindow.Element('lyricsCheckerPanel_songUsableText').Update("Profanity Engine: Not checked yet", text_color='#FFFFFF', font='Any 11')
            elif event == 'lyricsCheckerPanel_checkLyricsButton':
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
            elif event == 'profanityEnginePanel_searchClearInput': ## Clear Search Input
                HomeWindow.Element('profanityEnginePanel_searchInput').Update("")
                HomeWindow.Element('profanityEnginePanel_definitionsList').Update([item.replace("~", "'") for item in profanityEngineDefinitions]) ## Default List
            elif event == 'profanityEnginePanel_definitionsList' and len(values['profanityEnginePanel_definitionsList']) > 0: HomeWindow.Element('profanityEnginePanel_wordEditorInput').Update(values['profanityEnginePanel_definitionsList'][0]) ## Copy Word to Editor Input
            elif event == 'profanityEnginePanel_sortButton': ## Sort Entire List
                profanityEngineDefinitions = sorted(profanityEngineDefinitions)
                saveProfanityEngine(profanityEngineDefinitions)
            elif event == 'profanityEnginePanel_importButton': ## Import New List from Downloads
                profanityEngineDefinitions, fileBrowserWindow = [], sg.Window("File Location Selector", [[sg.Text("Select a file location:")], [sg.Input(key="fileLocation"), sg.FileBrowse()], [sg.Push(), sg.Button("OK"), sg.Push()]], no_titlebar=True, keep_on_top=True, finalize=True)
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
                    with open(str(pathlib.Path.home() / "Downloads") + "\\ExportedProfanityEngine" + str((datetime.datetime.now()).strftime("%d-%m-%Y-%H-%M-%S")) + ".txt", 'w') as file:
                        for item in profanityEngineDefinitions: file.write(item + '\n')
                    popupMessage("Profanity Engine", "Your Profanity Engine definitions have been successfully exported to your downloads folder.", "success", 3000) ## Show Error Message
                except: popupMessage("Profanity Engine", "Failed to export Profanity Engine definitions.", "error", 3000) ## Show Error Message
            elif event == 'profanityEnginePanel_clearButton': ## Clear Entire List
                if popupMessage("Profanity Engine Confirmation", "Are you sure you want to delete the entire Profanity Engine definitions list?", "confirmation"):
                    profanityEngineDefinitions = []
                    saveProfanityEngine(profanityEngineDefinitions)
            elif event == 'profanityEnginePanel_saveEditButton' and values['profanityEnginePanel_wordEditorInput'].strip() not in [""]: ## Save Editor Word to List
                profanityEngineDefinitions.append(values['profanityEnginePanel_wordEditorInput'].strip().replace("'", "~"))
                saveProfanityEngine(profanityEngineDefinitions)
                HomeWindow.Element('profanityEnginePanel_wordEditorInput').Update("")
            elif event == 'profanityEnginePanel_deleteWordButton': ## Delete Editor Word from List
                try: profanityEngineDefinitions.remove(values['profanityEnginePanel_wordEditorInput'].replace("'", "~"))
                except: pass
                saveProfanityEngine(profanityEngineDefinitions)
                HomeWindow.Element('profanityEnginePanel_wordEditorInput').Update("")
            elif event == 'profanityEnginePanel_newWordButton': ## New Editor Word
                if values['profanityEnginePanel_wordEditorInput'] not in profanityEngineDefinitions:
                    profanityEngineDefinitions.append(values['profanityEnginePanel_wordEditorInput'].strip().replace("'", "~"))
                    saveProfanityEngine(profanityEngineDefinitions)
                HomeWindow.Element('profanityEnginePanel_wordEditorInput').Update("")
            elif 'PredefinedWords' in event: ## Add default Profanity Engine Definitions
                with open(os.path.join(pathlib.Path(__file__).resolve().parent, "data", "Default data", "profanityEngineDefaults.json"), 'r') as file: data = json.load(file)
                profanityEngineDefinitions.extend(data['categories'][event.replace("profanityEnginePanel_", "").replace("PredefinedWords", "")])
                saveProfanityEngine(profanityEngineDefinitions)

## Software Tools

def saveProfanityEngine(profanityEngineDefinitions):
    HomeWindow.Element('profanityEnginePanel_searchInput').Update("") ## Clear Search
    HomeWindow.Element('profanityEnginePanel_definitionsList').Update([item.replace("~", "'") for item in profanityEngineDefinitions]) ## Update List
    try: ## Save to File
        with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "cache", "Profanity Engine", "userDefinitions.txt"), 'w') as file:
            for item in profanityEngineDefinitions: file.write(item.replace("'", "~") + '\n')
    except: pass

def savingSettings(setting, argument):
    global userSettingsData
    try:
        with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Settings.json"), 'r') as file: userSettingsData = json.load(file)
        userSettingsData[setting] = argument
        with open(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "Settings.json"), 'w') as file: json.dump(userSettingsData, file)
    except: popupMessage("Settings", "Unable to save settings.", "error")

def getDirSize(path):
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size

def loadingScreen(functionLoader, homeHasLaunched, agr1=False, arg2=False, arg3=False, arg4=False, arg5=False):
    global loadingStatus, metadataInfo
    if homeHasLaunched:
        loadingPopup, loadingStatus, metadataInfo = sg.Window("", [[sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", background_color='#1b2838', key='loadingGIFImage')], [sg.Text("Loading...", font='Any 16', background_color='#1b2838', key='loadingScreenText')]], background_color='#1b2838', element_justification='c', no_titlebar=True, keep_on_top=True, finalize=True), "Start", {}
        loadingPopup.hide()
        loadingPopup.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - loadingPopup.size[0] // 2, HomeWindow.TKroot.winfo_y() + HomeWindow.TKroot.winfo_height() // 2 - loadingPopup.size[1] // 2)
        loadingPopup.un_hide()
    else: loadingPopup, loadingStatus, metadataInfo = sg.Window("", [[sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", background_color='#1b2838', key='loadingGIFImage')], [sg.Text("Downloading Billboard Hot 100 Songs...", font='Any 16', background_color='#1b2838', key='loadingScreenText')]], background_color='#1b2838', element_justification='c', no_titlebar=True, keep_on_top=True), "Start", {}
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
                downloadTop100SongsThread = threading.Thread(name="downloadTop100Songs", target=downloadTop100Songs, args=())
                downloadTop100SongsThread.start()
                loadingStatus = "Downloading Billboard Hot 100 Songs..."  
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
                popupMessage("Music Downloader", "The song has been downloadeded successfully.", "success")
            break

def popupMessage(popupMessageTitle, popupMessageText, popupMessageIcon, popupTimer=0):
    wrapper = textwrap.TextWrapper(width=45, max_lines=6, placeholder='...')
    popupMessageText = '\n'.join(wrapper.wrap(popupMessageText))
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
    messagePopup['messagePopupExitButton'].Widget.config(cursor="hand2") ## Hover icons
    while True:
        event, values = messagePopup.read(timeout=100)
        try: messagePopup.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - messagePopup.size[0] // 2, HomeWindow.TKroot.winfo_y() + HomeWindow.TKroot.winfo_height() // 2 - messagePopup.size[1] // 2)
        except: pass
        if messagePopup.CurrentLocation()[1] < 200: messagePopup.move(messagePopup.CurrentLocation()[0], 100) ## Fix Over Top
        if event == sg.WIN_CLOSED or event == 'messagePopupExitButton' or (event == '_Delete') or (event == '_FocusOut' and popupTimer != 0 and timeOpened >= 100):
            messagePopup.close()
            return True
        elif event == 'messagePopupRemindButton':
            messagePopup.close()
            return "Week"
        elif event == 'messagePopupCancelButton':
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

def downloadYouTube(youtubeLink, downloadLocation, audioFileNeeded, videoFileNeeded, renameFile):
    global audioSavedPath, loadingStatus, youtubeTitle
    try:
        stream = YouTube(youtubeLink).streams.filter(file_extension="mp4").get_highest_resolution()
        youtubeTitle = stream.default_filename
        if os.path.exists(os.path.join(downloadLocation, youtubeTitle)) or os.path.exists(os.path.join(downloadLocation, youtubeTitle[:youtubeTitle.rfind(".mp4")] + ".mp3")): ## Check if the file already exists
            base, ext = os.path.splitext(youtubeTitle)
            index = 1
            while os.path.exists(os.path.join(downloadLocation, f"{base} ({index}){ext}")) or os.path.exists(os.path.join(downloadLocation, f"{base} ({index}).mp3")): index += 1
            youtubeTitle = f"{base} ({index}){ext}"
        stream.download(downloadLocation, filename=youtubeTitle) ## Download the video
        youtubeTitle = youtubeTitle[:youtubeTitle.rfind(".mp4")]
    except:
        loadingStatus = "Failed_YouTubeDownloader"
        return
    if audioFileNeeded: ## Convert MP4 Video to MP3 Audio
        audioSavedPath, loadingStatus = downloadLocation + "\\" + youtubeTitle + ".mp3", "Downloading Audio File..." ## MP3 File Name
        try: videoFile = VideoFileClip(downloadLocation + "\\" + youtubeTitle + ".mp4")
        except:
            loadingStatus = "Failed_YouTubeDownloader"
            return
        audioFile = videoFile.audio
        audioFile.write_audiofile(audioSavedPath)
        audioFile.close()
        videoFile.close()
        if renameFile != False: ## Rename MP3 File
            loadingStatus = "Renaming Audio File..."
            try: os.rename(audioSavedPath, audioSavedPath.replace(audioSavedPath.rsplit('\\', 1)[1], "") + "\\" + renameFile + "." + audioSavedPath.rsplit('.', 1)[1]) ## Rename MP3 to Chosen Name
            except: pass
    if renameFile != False: ## Rename MP4 File
        loadingStatus = "Renaming Video File..."
        videoSavedLocation = downloadLocation + "\\" + youtubeTitle + ".mp4"
        try: os.rename(videoSavedLocation, videoSavedLocation.replace(videoSavedLocation.rsplit('\\', 1)[1], "") + "\\" + renameFile + "." + videoSavedLocation.rsplit('.', 1)[1]) ## Rename MP4 to Chosen Name
        except: pass
    if videoFileNeeded == False: ## Delete video file if audio is only needed
        try: os.remove(downloadLocation + "\\" + youtubeTitle + ".mp4")
        except: pass
    loadingStatus = "Done_YouTubeDownloader"

def downloadAudio(youtubeLink, downloadLocation):
    global audioSavedPath, loadingStatus, youtubeTitle
    try:
        stream = YouTube(youtubeLink).streams.filter(file_extension="mp4").get_highest_resolution()
        youtubeTitle = stream.default_filename
        if os.path.exists(os.path.join(downloadLocation, youtubeTitle)) or os.path.exists(os.path.join(downloadLocation, youtubeTitle[:youtubeTitle.rfind(".mp4")] + ".mp3")): ## Check if the file already exists
            base, ext = os.path.splitext(youtubeTitle)
            index = 1
            while os.path.exists(os.path.join(downloadLocation, f"{base} ({index}){ext}")) or os.path.exists(os.path.join(downloadLocation, f"{base} ({index}).mp3")): index += 1
            youtubeTitle = f"{base} ({index}){ext}"
        stream.download(downloadLocation, filename=youtubeTitle) ## Download the video
        youtubeTitle = youtubeTitle[:youtubeTitle.rfind(".mp4")]
    except:
        loadingStatus = "Failed_MusicDownloaderYouTube"
        return
    audioSavedPath, loadingStatus = downloadLocation + "\\" + youtubeTitle + ".mp3", "Downloading Audio File..." ## MP3 File Name
    try: videoFile = VideoFileClip(downloadLocation + "\\" + youtubeTitle + ".mp4")
    except:
        loadingStatus = "Failed_MusicDownloaderYouTube"
        return
    audioFile = videoFile.audio
    audioFile.write_audiofile(audioSavedPath)
    audioFile.close()
    videoFile.close()
    try: os.remove(downloadLocation + "\\" + youtubeTitle + ".mp4") ## Delete video file
    except: pass
    ## Remove extra characters from YouTube title for Music Search
    youtubeTitle = re.sub(r'\([^)]*\)', '', youtubeTitle)
    loadingStatus = "Done_MusicDownloader"

def loadGeniusMusic(userInput, forceResult):
    global loadingAction, musicSearchResultData
    artistSearch, goodResult, hitsFound, musicSearchResultData, resultCount = False, False, 1, {}, 0
    if "genius.com" in userInput: userInput = userInput.split("https://genius.com/",1)[1].split("-lyrics",1)[0] ## Genius Website URL
    if "/songs/" in userInput: request = urllib.request.Request("http://api.genius.com" + userInput) ## Song ID Search
    else: request = urllib.request.Request("http://api.genius.com/search?q=" + urllib.request.quote(userInput.lower().replace(" by ", "-").replace("@","").replace(":","").split("-featuring")[0]) + "&lang=en&type=song&page=1")
    request.add_header("Authorization", "Bearer " + "ThgJU2pTawXV60l2g2jQXNEYT-b3MP7KDRd51BD-kLL7K5Eg8-UzrEGY96L3Z1c4")   
    request.add_header("User-Agent", "curl/7.9.8 (i686-pc-linux-gnu) libcurl 7.9.8 (OpenSSL 0.9.6b) (ipv6 enabled)")
    try: raw = (urllib.request.urlopen(request, timeout=10)).read()
    except Exception as Argument:
        if "Error 403" in str(Argument):
            loadingAction = "Genius_Robot_Check"
            return
        else:
            loadingAction = "Genius_Page_Down:" + str(Argument)
            return
    try:
        musicSearchApiBody = [result for result in (json.loads(raw)["response"]["hits"]) if "song" in result["type"] and not any(tag in result["result"]["title"].lower() for tag in ["instrumental", "radio edit", "slow", "sped", "version", "acapella", "acoustic", "log", "transcriptions"]) and not any(tag in result["result"]["artist_names"].lower() for tag in ["genius", "siriusxm"])]
        if len(musicSearchApiBody) > 0: musicSearchApiBodyPath = musicSearchApiBody[0]["result"]
    except: musicSearchApiBody, musicSearchApiBodyPath = json.loads(raw)["response"]["song"], json.loads(raw)["response"]["song"]
    hitsFound = len(musicSearchApiBody)
    if hitsFound == 0: ## Check if Result Found
        loadingAction = "No_Result_Found"
        return
    while goodResult == False:
        if artistSearch == False or str(musicSearchApiBodyPath["artist_names"]).replace("\u200b","").replace(" ", "-").split('(')[0].lower() == userInput: ## Check if Search is Artist
            if forceResult == False and str(musicSearchApiBodyPath["artist_names"]).replace(" ", "-").lower() == userInput: ## Change to Artist Search
                loadingAction = "Artist_Search"
                return
            ## Finish Normal Search
            try: musicSearchResultData["geniusMusicSearchArtists"] = str(musicSearchApiBodyPath["artist_names"]).replace("(Rock)", "") ## Song Artists
            except: ## No Results Left
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
                geniusMusicSearchArtworkURL = str(musicSearchApiBodyPath["song_art_image_url"])
                if "https://assets.genius.com/images/default_cover_image.png" in geniusMusicSearchArtworkURL: png_data = str(pathlib.Path(__file__).resolve().parent) + "\\data\\icons\\defaultMusicArtwork.png"
                else:
                    try: ## Look in Cache for Artwork
                        pil_image = Image.open(str(os.getenv('APPDATA')) + "\\Oszust Industries\\Oszust OS Music Tools\\cache\\Music Search\\Artworks\\" + str(musicSearchApiBodyPath["song_art_image_url"]).split(".com/",1)[1].split(".",1)[0] + ".png")
                        png_bio = io.BytesIO()
                        pil_image.save(png_bio, format="PNG")
                        png_data = png_bio.getvalue()
                    except: ## Download Artwork From Online
                        jpg_data = (cloudscraper.create_scraper(browser={"browser": "firefox", "platform": "windows", "mobile": False}).get(geniusMusicSearchArtworkURL).content)
                        pil_image = Image.open(io.BytesIO(jpg_data))
                        pil_image = pil_image.resize((200, 200)) ## Artwork Size
                        png_bio = io.BytesIO()
                        pil_image.save(png_bio, format="PNG")
                        try: ## Save Artwork to Cache
                            pathlib.Path(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "cache", "Music Search", "Artworks")).mkdir(parents=True, exist_ok=True) ## Create Music Artwork Cache Folder
                            png_data = pil_image.save(str(os.getenv('APPDATA')) + "\\Oszust Industries\\Oszust OS Music Tools\\cache\\Music Search\\Artworks\\" + str(musicSearchApiBodyPath["song_art_image_url"]).split(".com/",1)[1].split(".",1)[0] + ".png")
                        except: pass
                        png_data = png_bio.getvalue()
            except: png_data = str(pathlib.Path(__file__).resolve().parent) + "\\data\\icons\\defaultMusicArtwork.png"
            ## Album, Album List, Genre, and Label
            try: html = bs4.BeautifulSoup((requests.get(musicSearchResultData["geniusMusicSearchGeniusURL"])).text, "html.parser") # Scrape the info from the HTML
            except:
                loadingAction = "Genius_Page_Down"
                return
            if "Genius is down for a quick minute!" in str(html): ## Check if Genius's Service is Down
                loadingAction = "Genius_Page_Down"
                return
            elif "make sure you're a human" in str(html): ## Check if Genius thinks Robot
                loadingAction = "Genius_Robot_Check"
                return
            try: ## Album
                songScrapedInfo = html.select("div[class*=PrimaryAlbum__AlbumDetails]") ## Album Container
                musicSearchResultData["geniusMusicSearchAlbum"] = ((re.sub(r'<.+?>', '', str(songScrapedInfo))).replace("[", "").replace("]", "").replace("&amp;", "&")).split(" (")[0] ## Song Album
                if len(musicSearchResultData["geniusMusicSearchAlbum"]) == 0: musicSearchResultData["geniusMusicSearchAlbum"] = None ## No Album Found
            except: musicSearchResultData["geniusMusicSearchAlbum"] = None
            try: ## Album List
                songScrapedInfo, albumList = str(html.select("div[class*=AlbumTracklist__Track]")).split('</a>'), [] ## Song's Album List
                for song in songScrapedInfo:
                    match = re.search(r"<div class=\"AlbumTracklist__TrackNumber-sc-123giuo-3 epTVob\">(\d+)\. </div>" + musicSearchResultData["geniusMusicSearchSongNameInfo"], song)
                    if match: musicSearchResultData["geniusMusicSearchAlbumCurrent"] = match.group(1)
                    albumList.append(song)
                musicSearchResultData["geniusMusicSearchAlbumLength"] = len(albumList)
            except: musicSearchResultData["geniusMusicSearchAlbumCurrent"], musicSearchResultData["geniusMusicSearchAlbumLength"] = None, None
            try: ## Song's Genre
                infoList = str(html.select("div[class*=SongTags__Container]")).split('</a>') ## Song Genre Container
                musicSearchResultData["geniusMusicSearchGenre"] = (re.sub(r'<.+?>', '', str(infoList[0]))).replace("[", "").replace("]", "").replace("&amp;", "&") ## Song Genre
            except: musicSearchResultData["geniusMusicSearchGenre"] = None
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
            # Add the collected data to the dictionary
            musicSearchResultData["hitsFound"] = hitsFound
            musicSearchResultData["lyrics"] = lyrics
            musicSearchResultData["lyricsListFinal"] = lyricsListFinal
            musicSearchResultData["png_data"] = png_data
            if "/songs/" in userInput or musicSearchResultData["geniusMusicSearchArtists"].lower() not in ["spotify", "genius"]: goodResult = True ## Good Result Found
            elif resultCount < hitsFound: resultCount += 1 ## Move to Next Result
            else: 
                loadingAction = "No_Result_Found" ## No Good Result Found
                return
    loadingAction = "Search_Finished"

def geniusMusicSearch(userInput, forceResult, searchType="search"):
    global MusicSearchSongWindow, extendedSongInfo, loadingAction, metadataInfo, musicSearchResultData
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
    extendedSongInfo = [musicSearchResultData["geniusMusicSearchSongNameInfo"], musicSearchResultData["geniusMusicSearchArtists"], musicSearchResultData["geniusMusicSearchAlbum"]]
    if musicSearchResultData["geniusMusicSearchSongNameInfo"] != None and len(musicSearchResultData["geniusMusicSearchSongNameInfo"]) > 42: musicSearchResultData["geniusMusicSearchSongNameInfo"] = musicSearchResultData["geniusMusicSearchSongNameInfo"][:39] + "..." ## Shorten Song Name
    if musicSearchResultData["geniusMusicSearchArtists"] != None and len(musicSearchResultData["geniusMusicSearchArtists"]) > 45: musicSearchResultData["geniusMusicSearchArtists"] = musicSearchResultData["geniusMusicSearchArtists"][:42] + "..." ## Shorten Artists Names
    if musicSearchResultData["geniusMusicSearchAlbum"] != None and len(musicSearchResultData["geniusMusicSearchAlbum"]) > 45: musicSearchResultData["geniusMusicSearchAlbum"] = musicSearchResultData["geniusMusicSearchAlbum"][:42] + "..." ## Shorten Album Name
    ## Music Downloader Burner
    if searchType == "downloader":
        if metadataInfo["metadataBurnLyrics"] == False: musicSearchResultData["lyrics"] = None ## Don't Burn Lyrics
        if metadataInfo["metadataNameChangeValue"] != False: burnAudioData(metadataInfo["metadataBurnLocation"], False, metadataInfo["metadataMultipleArtistsValue"], metadataInfo["metadataNameChangeValue"], False)
        else: burnAudioData(metadataInfo["metadataBurnLocation"], False, metadataInfo["metadataMultipleArtistsValue"], extendedSongInfo[0], False)
        return
    ## Song Window
    if musicSearchResultData["lyrics"] != None: lyricsRightClickMenu = ['', ['Copy', 'Lookup Definition', 'Add to Profanity Engine', 'Remove from Profanity Engine']] ## Lyrics Right Click Menu - Profanity Engine
    else: lyricsRightClickMenu = ['', ['Copy', 'Lookup Definition']] ## Lyrics Right Click Menu - No Profanity Engine
    if musicSearchResultData["hitsFound"] > 1: layout = [[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchMenu.png', border_width=0, button_color='#2B475D', key='musicSearchResultsMenu', tooltip="All Results"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\personSearch.png', border_width=0, button_color='#2B475D', key='musicSearchArtistResultsMenu', tooltip="Search Artist"), sg.Push(background_color='#2B475D'), sg.Text("Music Search Result", font='Any 20', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchMP3Opener.png', border_width=0, button_color='#2B475D', key='downloadMetadataMp3Button', tooltip="Burn Metadata to MP3")]]
    else: layout = [[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\personSearch.png', border_width=0, button_color='#2B475D', key='musicSearchArtistResultsMenu', tooltip="Search Artist"), sg.Push(background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Text("Music Search Result", font='Any 20', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchMP3Opener.png', border_width=0, button_color='#2B475D', key='downloadMetadataMp3Button', tooltip="Burn Metadata to MP3")]]
    if musicSub == "Apple Music": layout += [[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchArtist.png', border_width=0, button_color='#2B475D', key='musicSearchArtistButton', tooltip="Open Artist page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchGenius.png', border_width=0, button_color='#2B475D', key='searchmusicSearchGenius', tooltip="Open Genius Lyrics page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchListenApple.png', border_width=0, button_color='#2B475D', key='musicSearchListenButton', tooltip="Play Song - Apple Music")]]
    elif musicSub == "Spotify": layout += [[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchArtist.png', border_width=0, button_color='#2B475D', key='musicSearchArtistButton', tooltip="Open Artist page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchGenius.png', border_width=0, button_color='#2B475D', key='searchmusicSearchGenius', tooltip="Open Genius Lyrics page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchListenSpotify.png', border_width=0, button_color='#2B475D', key='musicSearchListenButton', tooltip="Play Song - Spotify")]]
    if musicSearchResultData["geniusMusicSearchAlbum"] != None and musicSearchResultData["geniusMusicSearchDate"] != None: layout += [[sg.Image(musicSearchResultData["png_data"])], [sg.Text(musicSearchResultData["geniusMusicSearchSongNameInfo"], font='Any 20 bold', background_color='#2B475D', enable_events=True, key='geniusMusicSearchSongNameInfoText', tooltip=extendedSongInfo[0])], [sg.Text(musicSearchResultData["geniusMusicSearchAlbum"], font='Any 18', background_color='#2B475D', enable_events=True, key='geniusMusicSearchAlbumText', tooltip=extendedSongInfo[2])], [sg.Text(musicSearchResultData["geniusMusicSearchArtists"], font='Any 16', background_color='#2B475D', enable_events=True, key='geniusMusicSearchArtistsText', tooltip=extendedSongInfo[1])], [sg.Text(musicSearchResultData["geniusMusicSearchGenre"].upper() + " " + u"\N{Dot Operator}" + " " + musicSearchResultData["geniusMusicSearchDate"], font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchGenreText')]] ## Album Name Found
    elif musicSearchResultData["geniusMusicSearchAlbum"] != None and musicSearchResultData["geniusMusicSearchDate"] == None: layout += [[sg.Image(musicSearchResultData["png_data"])], [sg.Text(musicSearchResultData["geniusMusicSearchSongNameInfo"], font='Any 20 bold', background_color='#2B475D', enable_events=True, key='geniusMusicSearchSongNameInfoText', tooltip=extendedSongInfo[0])], [sg.Text(musicSearchResultData["geniusMusicSearchAlbum"], font='Any 18', background_color='#2B475D', enable_events=True, key='geniusMusicSearchAlbumText', tooltip=extendedSongInfo[2])], [sg.Text(musicSearchResultData["geniusMusicSearchArtists"], font='Any 16', background_color='#2B475D', enable_events=True, key='geniusMusicSearchArtistsText', tooltip=extendedSongInfo[1])], [sg.Text(musicSearchResultData["geniusMusicSearchGenre"].upper(), font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchGenreText')]] ## Album Name Found and No Release Date
    elif musicSearchResultData["geniusMusicSearchAlbum"] == None and musicSearchResultData["geniusMusicSearchDate"] != None: layout += [[sg.Image(musicSearchResultData["png_data"])], [sg.Text(musicSearchResultData["geniusMusicSearchSongNameInfo"], font='Any 20 bold', background_color='#2B475D', enable_events=True, key='geniusMusicSearchSongNameInfoText', tooltip=extendedSongInfo[0])], [sg.Text(musicSearchResultData["geniusMusicSearchArtists"], font='Any 16', background_color='#2B475D', enable_events=True, key='geniusMusicSearchArtistsText', tooltip=extendedSongInfo[1])], [sg.Text(musicSearchResultData["geniusMusicSearchGenre"].upper() + " " + u"\N{Dot Operator}" + " " + musicSearchResultData["geniusMusicSearchDate"], font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchGenreText')]] ## Album Name not Found
    else: layout += [[sg.Image(musicSearchResultData["png_data"])], [sg.Text(musicSearchResultData["geniusMusicSearchSongNameInfo"], font='Any 20 bold', background_color='#2B475D', enable_events=True, key='geniusMusicSearchSongNameInfoText', tooltip=extendedSongInfo[0])], [sg.Text(musicSearchResultData["geniusMusicSearchArtists"], font='Any 16', background_color='#2B475D', enable_events=True, key='geniusMusicSearchArtistsText', tooltip=extendedSongInfo[1])], [sg.Text(musicSearchResultData["geniusMusicSearchGenre"].upper(), font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchGenreText')]] ## No Album Name and No Release Date
    if musicSearchResultData["lyrics"] != None: layout += [[sg.Multiline("", size=(55,20), font='Any 11', autoscroll=False, disabled=True, right_click_menu=lyricsRightClickMenu, key='MusicSearchSongWindowLyrics')]] ## Add Empty Lyrics Box
    else: layout += [[sg.Text("Lyrics couldn't be found on Genius.", font='Any 12 bold', background_color='#2B475D')]] ## No Lyrics Found Message
    if musicSearchResultData["lyrics"] != None: layout += [[sg.Text("Profanity Engine: Not checked yet", font='Any 11', background_color='#2B475D', key='songUsableText')]] ## Default Profanity Engine Text
    if musicSearchResultData["geniusMusicSearchLabels"] != None and len(musicSearchResultData["geniusMusicSearchLabels"]) > 1: layout += [[sg.Text("Labels: " + str(musicSearchResultData["geniusMusicSearchLabels"]).replace("&amp;", "&").replace("[", "").replace("]", "").replace('"', "").replace("'", ""), font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchLabels')]] ## Song's Labels
    elif musicSearchResultData["geniusMusicSearchLabels"] != None and len(musicSearchResultData["geniusMusicSearchLabels"]) == 1: layout += [[sg.Text("Label: " + str(musicSearchResultData["geniusMusicSearchLabels"]).replace("&amp;", "&").replace("[", "").replace("]", "").replace('"', "").replace("'", ""), font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchLabels')]] ## Song's Label
    layout += [[sg.Text("Music Search powered by Genius", font='Any 11', background_color='#2B475D')]] ## Credits
    MusicSearchSongWindow = sg.Window("Music Search - Song", layout, background_color='#2B475D', resizable=True, finalize=True, keep_on_top=False, element_justification='c')
    MusicSearchSongWindow.TKroot.minsize(580, 710)
    MusicSearchSongWindow.hide()
    MusicSearchSongWindow.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - MusicSearchSongWindow.size[0] // 2, HomeWindow.TKroot.winfo_y() + HomeWindow.TKroot.winfo_height() // 2 - MusicSearchSongWindow.size[1] // 2)
    if MusicSearchSongWindow.CurrentLocation()[1] < 200: MusicSearchSongWindow.move(MusicSearchSongWindow.CurrentLocation()[0], 100) ## Fix Over Top
    MusicSearchSongWindow.un_hide()
    ## Lyrics Right Click Menu
    if musicSearchResultData["lyrics"] != None: lyricsLine:sg.Multiline = MusicSearchSongWindow['MusicSearchSongWindowLyrics']
    ## Window Shortcuts
    MusicSearchSongWindow.bind('<PageUp>', '_PageUp')      ## List Result shortcut
    MusicSearchSongWindow.bind('<PageDown>', '_PageDown')  ## Download Metadata shortcut
    MusicSearchSongWindow.bind('<Delete>', '_Delete')      ## Close Window shortcut
    MusicSearchSongWindow.bind('<Home>', '_Home')          ## Genius Lyrics shortcut
    MusicSearchSongWindow.bind('<End>', '_End')            ## Artist shortcut
    ## Mouse Icon Changes
    for key in ['downloadMetadataMp3Button', 'musicSearchArtistButton', 'musicSearchArtistResultsMenu', 'musicSearchListenButton', 'searchmusicSearchGenius']: MusicSearchSongWindow[key].Widget.config(cursor="hand2") ## Hover icons
    if musicSearchResultData["hitsFound"] > 1: MusicSearchSongWindow["musicSearchResultsMenu"].Widget.config(cursor="hand2")                                     ## List Search Results Hover icon
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
                    if True:
                        wordToAdd = re.sub(r'[\'"\.,!?;:]', '', (lyricsLine.Widget.selection_get()).strip().lower())
                        profanityEngineDefinitions.append(wordToAdd.replace("'", "~"))
                        saveProfanityEngine(profanityEngineDefinitions)
                        musicSearchPrintSongLyrics("musicSearch", musicSearchResultData["lyricsListFinal"]) ## Reload Music Search's Lyrics
                        popupMessage("Profanity Engine", '"' + wordToAdd + '"  has been successfully added to the Profanity Engine.', "saved", 3000) ## Show Success Message
                    if False: popupMessage("Profanity Engine", 'Failed to add "' + wordToAdd + '" to the Profanity Engine.', "error", 3000) ## Show Error Message
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
        elif event == 'downloadMetadataMp3Button' or (event == '_PageDown'):
            metadataBurnLyricsOnlyValue, metadataChangeFileNameValue, metadataMultipleArtistsValue = False, True, False ## Reset Variables
            musicSearchMetadataWindow = sg.Window("Music Search - Metadata Burner", [[sg.Text("Metadata Burner", font=('Helvetica', 20), background_color='#646f75')], [sg.HorizontalSeparator()], [sg.Text("Choose .MP3 Audio File: ", font=("Helvetica", 14), background_color='#646f75')], [sg.Input("", do_not_clear=True, size=(38,1), enable_events=True, key='metadataBurnerFileChooserInput'), sg.FileBrowse(file_types=(("Audio Files", "*.mp3"),), key='metadataBurnerFileChooser')], [sg.HorizontalSeparator()], [sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\false.png', border_width=0, button_color='#646f75', key='metadataBurnLyricsOnlyCheckbox', tooltip="Burn lyrics only - No"), sg.Text("Burn Lyrics Only", font=('Helvetica', 11), background_color='#646f75', key='metadataBurnLyricsOnlyText')], [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\false.png', border_width=0, button_color='#646f75', key='metadataMultipleArtistsCheckbox', tooltip="Multiple artists - No"), sg.Text("Album Includes Multiple Artists?", font=('Helvetica', 11), background_color='#646f75', key='metadataMultipleArtistsText')], [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\icons\\true.png', border_width=0, button_color='#646f75', key='metadataChangeFileNameCheckbox', tooltip="Change file name - Yes"), sg.Text("Change Audio File's Name", font=('Helvetica', 11), background_color='#646f75', key='metadataChangeFileNameText')]], element_justification='l', background_color='#646f75')], [sg.HorizontalSeparator()], [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\start.png', border_width=0,button_color='#646f75', key='burnMetadataInfo'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\cancel.png', border_width=0, button_color='#646f75', key='closeMetadataWindow')]], background_color='#646f75', no_titlebar=True, resizable=False, finalize=True, keep_on_top=True, element_justification='c')
            for key in ['metadataBurnerFileChooser', 'metadataBurnLyricsOnlyCheckbox', 'metadataMultipleArtistsCheckbox', 'metadataChangeFileNameCheckbox', 'burnMetadataInfo', 'closeMetadataWindow']: musicSearchMetadataWindow[key].Widget.config(cursor="hand2") ## Hover icons
            musicSearchMetadataWindow.bind('<Delete>', '_Delete')  ## Close Window shortcut
            while True:
                event, values = musicSearchMetadataWindow.read()
                if event == sg.WIN_CLOSED or event == 'closeMetadataWindow' or (event == '_Delete'): ## Close Settings Window
                    musicSearchMetadataWindow.close()
                    break
                elif event == 'metadataBurnLyricsOnlyCheckbox' and metadataBurnLyricsOnlyValue == True: ## Set Burn Lyrics Only to False
                    musicSearchMetadataWindow['metadataBurnLyricsOnlyCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\false.png')
                    musicSearchMetadataWindow['metadataBurnLyricsOnlyCheckbox'].set_tooltip("Burn lyrics only - No")
                    metadataBurnLyricsOnlyValue = False
                elif event == 'metadataBurnLyricsOnlyCheckbox' and metadataBurnLyricsOnlyValue == False: ## Set Burn Lyrics Only to True
                    musicSearchMetadataWindow['metadataBurnLyricsOnlyCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\true.png')
                    musicSearchMetadataWindow['metadataBurnLyricsOnlyCheckbox'].set_tooltip("Burn lyrics only - Yes")
                    metadataBurnLyricsOnlyValue = True
                elif event == 'metadataMultipleArtistsCheckbox' and metadataMultipleArtistsValue == True: ## Set Multiple Artists to False
                    musicSearchMetadataWindow['metadataMultipleArtistsCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\false.png')
                    musicSearchMetadataWindow['metadataMultipleArtistsCheckbox'].set_tooltip("Multiple artists - No")
                    metadataMultipleArtistsValue = False
                elif event == 'metadataMultipleArtistsCheckbox' and metadataMultipleArtistsValue == False: ## Set Multiple Artists to True
                    musicSearchMetadataWindow['metadataMultipleArtistsCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\true.png')
                    musicSearchMetadataWindow['metadataMultipleArtistsCheckbox'].set_tooltip("Multiple artists - Yes")
                    metadataMultipleArtistsValue = True
                elif event == 'metadataChangeFileNameCheckbox' and metadataChangeFileNameValue == True: ## Set Change File Name to False
                    musicSearchMetadataWindow['metadataChangeFileNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\false.png')
                    musicSearchMetadataWindow['metadataChangeFileNameCheckbox'].set_tooltip("Change file name - No")
                    metadataChangeFileNameValue = False
                elif event == 'metadataChangeFileNameCheckbox' and metadataChangeFileNameValue == False: ## Set Change File Name to True
                    musicSearchMetadataWindow['metadataChangeFileNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\true.png')
                    musicSearchMetadataWindow['metadataChangeFileNameCheckbox'].set_tooltip("Change file name - Yes")
                    metadataChangeFileNameValue = True
                elif event == 'burnMetadataInfo':
                    musicSearchMetadataWindow.close()
                    burnAudioData(values['metadataBurnerFileChooserInput'], metadataBurnLyricsOnlyValue, metadataMultipleArtistsValue, extendedSongInfo[0]) ## Download Metadata to MP3
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
        badWordCount = 0
        lyricsBox.update("", autoscroll=False)
        loadProfanityEngineDefinitions(False)
        profanityRegex = re.compile('|'.join([r'\b{}\b'.format(re.escape(phrase)) for phrase in [phrase.lower().replace("\n", "").replace("~", "'") for phrase in profanityEngineDefinitions]]), re.IGNORECASE)
        for lyric in lyricsListFinal:
            badLine = False
            lastEnd, matches = 0, profanityRegex.finditer(lyric.replace(",", ""))
            for match in matches:
                start, end = match.span()
                if "," in lyric: end += 2
                lyricsBox.update(lyric[lastEnd:start], autoscroll=False, append=True)
                lyricsBox.update(lyric[start:end], autoscroll=False, text_color_for_value='Red', append=True)
                badLine, lastEnd = True, end
            if badLine: badWordCount += 1
            lyricsBox.update(lyric[lastEnd:], autoscroll=False, append=True)
            lyricsBox.update("\n", autoscroll=False, append=True)
    except: ## Profanity Engine Dictionary Failed to Load
        profanityEngineDefinitions = "Failed"
        lyricsBox.update("", autoscroll=False)
        for line in range(len(lyricsListFinal)): lyricsBox.print(lyricsListFinal[line], autoscroll=False)
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
        audiofile, lyricsText = eyed3.load(audioSavedPath), "" ## Load MP3
        audiofile.initTag(version=(2, 3, 0)) ## Version is Important
        for i in range(len(musicSearchResultData["lyricsListFinal"])): ## Get Lyrics
            if len(musicSearchResultData["lyricsListFinal"][i]) == 0: lyricsText += "\n"
            else: lyricsText += musicSearchResultData["lyricsListFinal"][i] + "\n"
        if musicSearchResultData["lyrics"] != None: audiofile.tag.lyrics.set(lyricsText) ## Save Lyrics
        if burnLyricsOnly:
            audiofile.tag.comments.set(u"Metadata: Oszust Industries") ## Comment
            audiofile.tag.save() ## Save File
            popupMessage("Metadata Burner", "Metadata has been successfully saved to " + renameFile + ".", "saved", 3000) ## Show Success Message
            return
        audiofile.tag.artist = extendedSongInfo[1] ## Artist
        if multipleArtists: audiofile.tag.album_artist = "Various Artists" ## Album's Artists (Various Artists)
        else: audiofile.tag.album_artist = musicSearchResultData["geniusMusicSearchPrimeArtist"] ## Album's Artists
        audiofile.tag.title = extendedSongInfo[0] ## Title
        if musicSearchResultData["geniusMusicSearchDate"] != None and musicSearchResultData["geniusMusicSearchDate"] != "Unknown Release Date": audiofile.tag.recording_date = musicSearchResultData["geniusMusicSearchDate"][-4:] ## Year
        if musicSearchResultData["geniusMusicSearchGenre"] != "Non-Music": audiofile.tag.genre = musicSearchResultData["geniusMusicSearchGenre"] ## Genre
        audiofile.tag.album = extendedSongInfo[2] ## Album
        if musicSearchResultData["geniusMusicSearchLabels"] != None: audiofile.tag.publisher = musicSearchResultData["geniusMusicSearchLabels"][0].replace("[", "").replace("]", "").replace("'", "") ## Label
        if musicSearchResultData["geniusMusicSearchAlbumCurrent"] != None and musicSearchResultData["geniusMusicSearchAlbumLength"] != None: audiofile.tag.track_num = (musicSearchResultData["geniusMusicSearchAlbumCurrent"], musicSearchResultData["geniusMusicSearchAlbumLength"]) ## Current Song Position and Total Album
        elif musicSearchResultData["geniusMusicSearchAlbumCurrent"] != None: audiofile.tag.track_num = musicSearchResultData["geniusMusicSearchAlbumCurrent"] ## Current Song Position
        if musicSearchResultData["png_data"] != str(pathlib.Path(__file__).resolve().parent) + "\\data\\icons\\defaultMusicArtwork.png": 
            for artworkType in [4, 3, 0]: audiofile.tag.images.set(artworkType, musicSearchResultData["png_data"], "image/png") ## Artwork - Basic
            for artworkType in [4, 3, 0]: audiofile.tag.images.set(artworkType, musicSearchResultData["png_data"], "image/jpeg", "cover") ## Artwork - Higher Quality
        audiofile.tag.comments.set(u"Metadata: Oszust Industries") ## Comment
        audiofile.tag.save() ## Save File
        ## Change the audio file's name
        if renameFile != False:
            try: os.rename(audioSavedPath, audioSavedPath.replace(audioSavedPath.rsplit('/', 1)[1], "") + "\\" + renameFile.strip() + ".mp3") ## Rename MP3 to Song Name
            except:
                try: os.rename(audioSavedPath, audioSavedPath.replace(audioSavedPath.rsplit('\\', 1)[1], "") + "\\" + renameFile.strip() + ".mp3") ## Rename MP3 to Song Name Fix
                except: pass
        if displayMessage: popupMessage("Metadata Burner", "Metadata has been successfully saved to " + renameFile + ".", "saved", 3000) ## Show Success Message
    except: popupMessage("Metadata Burner", "Failed to burn metadata.", "error")

def loadGeniusMusicList(userInput):
    global musicListLayout, loadingAction, musicListResultData
    musicListResultData = {}
    ## Set Local Variables
    try: musicSub = userSettingsData["musicService"]
    except: musicSub = "Apple Music"
    artistSearch, musicListResultData["geniusSongIDs"], musicListResultData["geniusURLs"], musicListResultData["musicListLayout"], resultNumber, musicListResultData["resultNumbers"], musicListResultData["songArtists"], musicListResultData["songNames"] = False, [], [], [[sg.Push(background_color='#657076'), sg.Text('Music Search Results:', font='Any 20', background_color='#657076'), sg.Push(background_color='#657076')], [sg.Push(background_color='#657076'), sg.Input(userInput, do_not_clear=True, size=(60,1), enable_events=True, key='geniusMusicListSearchInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\search.png', border_width=0, button_color='#657076', key='geniusMusicListSearchButton', tooltip="Search"), sg.Push(background_color='#657076')]], 0, [], [], []
    if "genius.com" in userInput: userInput = userInput.split("https://genius.com/",1)[1].split("-lyrics",1)[0] ## Genius Website URL
    request = urllib.request.Request("http://api.genius.com/search?q=" + urllib.request.quote(userInput.lower().replace(" by ", "-")) + "&lang=en&type=song&page=1")
    request.add_header("Authorization", "Bearer " + "ThgJU2pTawXV60l2g2jQXNEYT-b3MP7KDRd51BD-kLL7K5Eg8-UzrEGY96L3Z1c4")   
    request.add_header("User-Agent", "curl/7.9.8 (i686-pc-linux-gnu) libcurl 7.9.8 (OpenSSL 0.9.6b) (ipv6 enabled)")
    try: raw = (urllib.request.urlopen(request, timeout=10)).read()
    except Exception as Argument:
        if "Error 403" in str(Argument):
            loadingAction = "Genius_Robot_Check"
            return
        else:
            loadingAction = "Genius_Page_Down:" + str(Argument)
            return
    ## Find Number of Hits
    musicSearchApiBody = [result for result in (json.loads(raw)["response"]["hits"]) if "song" in result["type"] and not any(tag in result["result"]["title"].lower() for tag in ["instrumental", "radio edit", "slow", "sped", "version", "acapella", "acoustic", "log", "transcriptions"]) and not any(tag in result["result"]["artist_names"].lower() for tag in ["genius", "siriusxm"])]
    hitsFound = len(musicSearchApiBody)
    if hitsFound == 0: ## Check if Result Found
        loadingAction = "No_Result_Found"
        return
    if hitsFound > 8: hitsFound = 8 ## Set Max to 8 if More Than 8 Results Returned
    while hitsFound > 0 and resultNumber < 10:
        geniusMusicSearchArtists = str(musicSearchApiBody[resultNumber]["result"]["artist_names"]).replace("(Rock)", "") ## Song Artists
        musicListResultData["songArtists"].append(geniusMusicSearchArtists) ## Add Artists to List 
        geniusMusicSearchPrimeArtist = str(musicSearchApiBody[resultNumber]["result"]["primary_artist"]["name"]).split('(')[0] ## Song Main Artist
        if str(musicSearchApiBody[0]["result"]["artist_names"]).replace(" ", "-").lower() == userInput: artistSearch = True ## Find if Search is an Artist
        geniusMusicSearchDate = str(musicSearchApiBody[resultNumber]["result"]["release_date_for_display"]) ## Result Release Date
        if geniusMusicSearchDate == "None": geniusMusicSearchDate = None ## Fix Release Date if None Found
        geniusMusicSearchSongNameInfo = str(musicSearchApiBody[resultNumber]["result"]["title_with_featured"]) ## Result Full Title
        musicListResultData["songNames"].append(geniusMusicSearchSongNameInfo) ## Add Song Full Title to List
        geniusMusicSearchGeniusURL = str(musicSearchApiBody[resultNumber]["result"]["url"]) ## Result Genius URL
        musicListResultData["geniusURLs"].append(geniusMusicSearchGeniusURL) ## Add Genius URL to List
        geniusMusicSearchGeniusSongID = str(musicSearchApiBody[resultNumber]["result"]["api_path"]) ## Song ID
        musicListResultData["geniusSongIDs"].append(geniusMusicSearchGeniusSongID) ## Add Song ID to List
        ## Shorten Results
        longSongNameInfo = geniusMusicSearchSongNameInfo
        longArtists = geniusMusicSearchArtists
        if len(geniusMusicSearchSongNameInfo) > 30: geniusMusicSearchSongNameInfo = geniusMusicSearchSongNameInfo[:29] + "..." ## Shorten Song Name
        if len(geniusMusicSearchArtists) > 30: geniusMusicSearchArtists = geniusMusicSearchArtists[:29] + "..." ## Shorten Artists Names
        ## Song Artwork
        try:
            geniusMusicSearchArtworkURL = str(musicSearchApiBody[resultNumber]["result"]["song_art_image_url"])
            if "https://assets.genius.com/images/default_cover_image.png" in geniusMusicSearchArtworkURL: png_data = str(pathlib.Path(__file__).resolve().parent) + "\\data\\icons\\defaultMusicArtwork.png"
            else:
                try: ## Look in Cache for Artwork
                    pil_image = Image.open(str(os.getenv('APPDATA')) + "\\Oszust Industries\\Oszust OS Music Tools\\cache\\Music Search\\" + str(musicSearchApiBody[resultNumber]["result"]["song_art_image_url"]).split(".com/",1)[1].split(".",1)[0] + "-small.png") ## Open Artwork from Cache
                    png_bio = io.BytesIO()
                    pil_image.save(png_bio, format="PNG")
                    png_data = png_bio.getvalue()
                except: ## Download Artwork From Online
                    jpg_data = (cloudscraper.create_scraper(browser={"browser": "firefox", "platform": "windows", "mobile": False}).get(geniusMusicSearchArtworkURL).content)
                    pil_image = Image.open(io.BytesIO(jpg_data))
                    pil_image = pil_image.resize((80, 80)) ## Artwork Size
                    png_bio = io.BytesIO()
                    pil_image.save(png_bio, format="PNG")
                    try: ## Save Artwork to Cache
                        pathlib.Path(os.path.join(os.getenv('APPDATA'), "Oszust Industries", "Oszust OS Music Tools", "cache", "Music Search")).mkdir(parents=True, exist_ok=True) ## Create Music Cache Folder
                        png_data = pil_image.save(str(os.getenv('APPDATA')) + "\\Oszust Industries\\Oszust OS Music Tools\\cache\\Music Search\\" + str(musicSearchApiBody[resultNumber]["result"]["song_art_image_url"]).split(".com/",1)[1].split(".",1)[0] + "-small.png")
                    except: pass
                    png_data = png_bio.getvalue()
        except: png_data = str(pathlib.Path(__file__).resolve().parent) + "\\data\\icons\\defaultMusicArtwork.png" ## Default Artwork if Retrieval Fails
        ## Song Lyrics
        geniusMusicSearchLyricsState = str(musicSearchApiBody[resultNumber]["result"]["lyrics_state"]) ## Result Song Lyrics
        if geniusMusicSearchLyricsState.lower() == "complete": lyricsImage, lyricsHoverMessage = "checked", "Lyrics Found" ## Lyrics Found
        else: lyricsImage, lyricsHoverMessage = "checkFailed", "Lyrics Not Found" ## No Lyrics Found
        ## Music Service
        if musicSub == "Apple Music": musicServiceImage = "musicSearchListenApple" ## Set Listening Link to Apple
        elif musicSub == "Spotify": musicServiceImage = "musicSearchListenSpotify" ## Set Listening Link to Spotify
        ## Song Window
        if (artistSearch == False or (artistSearch == True and geniusMusicSearchPrimeArtist.replace(" ", "-").split('(')[0].lower() == userInput)) and geniusMusicSearchArtists.lower() not in ["spotify", "genius", "siriusxm the highway"] and "genius" not in geniusMusicSearchArtists.lower():
            if geniusMusicSearchDate != None: musicListResultData["musicListLayout"] += [[sg.Column([[sg.Image(png_data), sg.Column([[sg.Text(str(geniusMusicSearchSongNameInfo), font='Any 16', background_color='#2b475d', tooltip=longSongNameInfo)], [sg.Text(str(geniusMusicSearchArtists), font='Any 14', background_color='#2b475d', tooltip=longArtists)], [sg.Text(str(geniusMusicSearchDate), font='Any 12', background_color='#2b475d')]], background_color='#2b475d'), sg.Push(background_color='#2b475d'), sg.Column([[sg.Image(str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\'+lyricsImage+'.png', background_color='#2b475d', tooltip=lyricsHoverMessage), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchGenius.png', border_width=0, button_color='#2b475d', key='searchmusicListSearchGenius_' + str(resultNumber), tooltip="Open Genius Page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\'+musicServiceImage+'.png', border_width=0, button_color='#2b475d', key='searchmusicListPlaySong_' + str(resultNumber), tooltip="Play Song"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\openView.png', border_width=0, button_color='#2b475d', key='searchMusicListOpenSong_' + str(resultNumber), tooltip="Open Result")]], background_color='#2b475d')]], background_color='#2b475d', expand_x=True)]]
            else: musicListResultData["musicListLayout"] += [[sg.Column([[sg.Image(png_data), sg.Column([[sg.Text(str(geniusMusicSearchSongNameInfo), font='Any 16', background_color='#2b475d', tooltip=longSongNameInfo)], [sg.Text(str(geniusMusicSearchArtists), font='Any 14', background_color='#2b475d', tooltip=longArtists)]], background_color='#2b475d'), sg.Push(background_color='#2b475d'), sg.Column([[sg.Image(str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\'+lyricsImage+'.png', background_color='#2b475d', tooltip=lyricsHoverMessage), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\musicSearchGenius.png', border_width=0, button_color='#2b475d', key='searchmusicListSearchGenius_' + str(resultNumber), tooltip="Open Genius Page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\'+musicServiceImage+'.png', border_width=0, button_color='#2b475d', key='searchmusicListPlaySong_' + str(resultNumber), tooltip="Play Song"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\icons\\openView.png', border_width=0, button_color='#2b475d', key='searchMusicListOpenSong_' + str(resultNumber), tooltip="Open Result")]], background_color='#2b475d')]], background_color='#2b475d', expand_x=True)]]
            musicListResultData["resultNumbers"].append(resultNumber)
        resultNumber += 1
        hitsFound -= 1
    musicListResultData["musicListLayout"] += [[sg.Push(background_color='#657076'), sg.Text("Music Search powered by Genius", background_color='#657076', font='Any 11'), sg.Push(background_color='#657076')]] ## Credits
    ## Check if Any Good Results Found
    if len(musicListResultData["resultNumbers"]) == 0: loadingAction = "No_Result_Found"
    elif len(musicListResultData["resultNumbers"]) == 1: loadingAction = "Only_One_Result"
    else: loadingAction = "Search_Finished"

def geniusMusicSearchList(userInput, searchType="search"):
    global loadingAction
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
            loadGeniusMusicListThread = threading.Thread(name="loadGeniusMusicList", target=loadGeniusMusicList, args=(userInput,))
            loadGeniusMusicListThread.start()
            loadingAction = "Running"
        elif loadingAction == "No_Result_Found" and searchType == "downloader": ## No Music Search Result Found and Downloader
            musicListResultData["musicListLayout"] += [[sg.Column([[sg.Push(background_color='#2b475d'), sg.Text("No results were found!", background_color='#2b475d', font='Any 16 bold'), sg.Push(background_color='#2b475d')], [sg.Push(background_color='#2b475d'), sg.Text("Please enter a new search query in the search bar or close the window to not burn metadata to your song.", background_color='#2b475d', font='Any 12'), sg.Push(background_color='#2b475d')]], background_color='#2b475d', expand_x=True)]]
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
    MusicSearchListWindow.TKroot.minsize(700, 300)
    MusicSearchListWindow.hide()
    MusicSearchListWindow.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - MusicSearchListWindow.size[0] // 2, HomeWindow.TKroot.winfo_y() + HomeWindow.TKroot.winfo_height() // 2 - MusicSearchListWindow.size[1] // 2)
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

def burnMusicCD():
    import subprocess
    import tempfile
    import shutil

    # Create a temporary directory to store the WAV files.
    temp_dir = tempfile.mkdtemp()

    try:
        # Convert the MP3 files to WAV files.
        for mp3_file in ['/path/to/mp3/file1.mp3', '/path/to/mp3/file2.mp3']:
            if mp3_file.endswith('.mp3'):
                wav_file = os.path.join(temp_dir, os.path.basename(mp3_file)[:-4] + '.wav')
                subprocess.call(['ffmpeg', '-i', mp3_file, wav_file])

        # Burn the WAV files to the CD.
        subprocess.call(['wodim', '-v', '-e', '/dev/cdrom', temp_dir])
    except Exception as e: print("An error occurred:", e)
    finally: shutil.rmtree(temp_dir)


## Start System
try: softwareSetup()
except Exception as Argument: crashMessage("Error 00: " + str(Argument))