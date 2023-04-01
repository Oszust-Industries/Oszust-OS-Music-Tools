## Oszust OS Music Tools - Oszust Industries
## Created on: 1-02-23 - Last update: 4-01-23
softwareVersion = "v1.0.0.001 BETA"
import ctypes, datetime, json, math, os, pathlib, pickle, platform, psutil, re, requests, textwrap, threading, urllib.request, webbrowser, win32clipboard
from moviepy.editor import *
from pytube import YouTube
import PySimpleGUI as sg

def softwareConfig():
    ## System Configuration
    global exitSystem, systemBuild, systemName, musicSub
    exitSystem, systemName, systemBuild = False, "Oszust OS Music Tools", "dev"
    musicSub = "Apple"

def getScaling():
    # Get Scaling Infomation
    root = sg.tk.Tk()
    scaling = root.winfo_fpixels('1i')/72
    root.destroy()
    return scaling

def softwareSetup():
    global firstHomeLaunch, screenHeight, screenWidth, topSongsList, wifiStatus
    ## Setup Software
    print("Loading...\nLaunching Interface...")
    firstHomeLaunch, wifiStatus = True, True
    ## Fix Screen Size
    ctypes.windll.user32.SetProcessDPIAware(False) ## DPI Awareness
    scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100 ## Get Windows Scale Factor
    screenWidth, screenHeight = sg.Window.get_screen_size() ## Get WxH of Pixels
    sg.set_options(scaling = (getScaling() * min(screenWidth / (screenWidth * scaleFactor), screenHeight / (1080 * scaleFactor)))) ## Apply Fix to Window
    ## Setup Commands
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0) ## Hide Console
    softwareConfig() ## Get User's Configs
    ## Check WIFI
    try: urllib.request.urlopen("http://google.com", timeout=3)
    except: wifiStatus = False
    ## Billboard Top 100 Hits from Cache
    try:
        billboardCache, topSongsList = (open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Billboard.txt", "r")).read().split("\n"), []
        if datetime.datetime.strptime(billboardCache[0], '%Y-%m-%d') + datetime.timedelta(days=7) >= datetime.datetime.now(): ## Check if Cache is >= Week
            for item in billboardCache[1:]: topSongsList.append(item) ## Set List from Cache
        else: loadingScreen("Billboard_List_Download", agr1=False, arg2=False, arg3=False, arg4=False, arg5=False) ## Download Billboard Data
    except: loadingScreen("Billboard_List_Download", agr1=False, arg2=False, arg3=False, arg4=False, arg5=False) ## Download Billboard Data
    ## Retrieve Profanity Engine Definitions
    try:
        ProfanityEngineCache = pickle.load(open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Profanity Engine\\Date.p", "rb"))
        if ProfanityEngineCache + datetime.timedelta(days=1) > datetime.datetime.now(): loadProfanityEngineDefinitions(False) ## Check if Cache is >= Day
        else: loadProfanityEngineDefinitions(True)
    except: loadProfanityEngineDefinitions(True)
    ## Launch Default Home App
    homeScreen()

def crashMessage(message):
    errorWindow = sg.Window("ERROR", [[sg.Text(message, font=("Any", 13))], [sg.Button("Report Error", button_color=("White", "Blue"), key='Report'), sg.Button("Quit", button_color=("White", "Red"), key='Quit')]], resizable=False, finalize=True, keep_on_top=True, element_justification='c')
    ## Window Shortcuts
    errorWindow.bind('<Insert>', '_Insert')  ## Report Error shortcut
    errorWindow.bind('<Delete>', '_Delete')  ## Close Window shortcut
    ## Mouse Icon Changes
    for key in ['Report', 'Quit']: errorWindow[key].Widget.config(cursor="hand2") ## Hover icons
    while True:
        event, values = errorWindow.read()
        if event == sg.WIN_CLOSED or event == 'Quit' or (event == '_Delete'):
            if systemBuild.lower() in ["dev"]: exit()
            else:
                thisSystem = psutil.Process(os.getpid()) ## Close Program
                thisSystem.terminate()
        elif event == 'Report' or (event == '_Insert'): webbrowser.open("https://github.com/Oszust-Industries/" + systemName.replace(" ", "-") + "/issues/new", new=2, autoraise=True)

def downloadTop100Songs():
    global loadingStatus, topSongsList
    try:
        import billboard
        chart, topSongsList = billboard.ChartData('hot-100', fetch=True, max_retries=3, timeout=25), [] ## Get Data from Billboard
        for x in range(100):
            try:
                song = chart[x]
                if song.weeks == 1: topSongsList.append(str(x+1) + ". " + song.title + " - " + song.artist + "   (" + str(song.weeks) + " week) NEW") ## New Song on Billboard
                elif song.lastPos > song.rank: topSongsList.append(str(x+1) + ". " + song.title + " - " + song.artist + "   (" + str(song.weeks) + " weeks) ^") ## Song Moved Up
                elif song.lastPos == song.rank: topSongsList.append(str(x+1) + ". " + song.title + " - " + song.artist + "   (" + str(song.weeks) + " weeks) -") ## Song Stayed Same
                elif song.lastPos < song.rank: topSongsList.append(str(x+1) + ". " + song.title + " - " + song.artist + "   (" + str(song.weeks) + " weeks) v") ## Song Moved Down
            except: topSongsList.append(str(x+1) + ". Result Failed to Load") ## One Result Failed
        try: ## Cache the List
            pathlib.Path(str(pathlib.Path(__file__).resolve().parent) + "\\cache").mkdir(parents=True, exist_ok=True) ## Create Cache Folder
            with open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Billboard.txt", "w") as billboardTextFile: ## Create Cache File
                lastTuesday = datetime.date.today() - datetime.timedelta(days=(datetime.date.today().weekday() - 1) % 7) ## Data is Fresh on Tuesday
                billboardTextFile.write(str(lastTuesday))
                for item in topSongsList: billboardTextFile.write("\n" + item)
                billboardTextFile.close()
        except: pass
    except: topSongsList.append("Billboard Top 100 Failed to Load")
    loadingStatus = "Done"

def loadProfanityEngineDefinitions(downloadList):
    global badWordCount, profanityEngineDefinitions
    try:
        if downloadList:
            badWordCount, profanityEngineDefinitions = 0, json.loads(urllib.request.urlopen(f"https://raw.githubusercontent.com/Oszust-Industries/" + systemName.replace(" ", "-") + "/Server/profanityEngineDefinitions.txt").read().decode())
            try:
                pathlib.Path(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Profanity Engine").mkdir(parents=True, exist_ok=True) ## Create Profanity Engine Cache Folder
                pickle.dump(profanityEngineDefinitions, open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Profanity Engine\\Cache.p", "wb"))
                pickle.dump(datetime.datetime.now(), open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Profanity Engine\\Date.p", "wb"))
            except: pass
        else:
            try: badWordCount, profanityEngineDefinitions = 0, pickle.load(open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Profanity Engine\\Cache.p", "rb"))
            except:
                loadProfanityEngineDefinitions(True)
                return
        try: ## Add User's Definitions
            additionProfanityEngineInfo = pickle.load(open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Profanity Engine\\Additions.p", "rb"))
            for phrase in additionProfanityEngineInfo: profanityEngineDefinitions.append(phrase)
        except: pass
        try: ## Remove User's Definitions
            removalsProfanityEngineInfo = pickle.load(open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Profanity Engine\\Removals.p", "rb"))
            for phrase in removalsProfanityEngineInfo:
                try: profanityEngineDefinitions.remove(phrase)
                except: pass
        except: pass
    except: profanityEngineDefinitions = "Failed"

def homeScreenAppPanels():
    ## Extra Apps Panel Creator
    global toolPanelApps
    toolsPanel, toolPanelAppLocation, toolPanelApps, toolsPanelRow = [[]], 0, ["Music Search", "Music Downloader", "Youtube Downloader", "Lyrics Checker"], [] #"Profanity Editor"
    for toolsPanelRowNumber in range(math.ceil(len(toolPanelApps)/5)):
        try:
            for app in range(toolPanelAppLocation, 5*(toolsPanelRowNumber+1)): toolsPanelRow.append(toolPanelApps[app])
        except: pass
        toolsPanel += [[sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\Apps\\' + app[0].lower() + app[1:].replace(" ", "") + '.png', border_width=0, button_color='#657076', key='musicTool_' + app.replace(" ", "_"), tooltip="Open " + app)]], background_color='#657076') for app in toolsPanelRow]]
        toolsPanelRow = []
        toolPanelAppLocation += 5
    ## Music Search Panel [Default]
    topSongsListBoxed = [[sg.Listbox(topSongsList, size=(79, 15), horizontal_scroll=True, select_mode=None, enable_events=True, highlight_background_color='blue', highlight_text_color='white', key='musicSearchPanel_billboardTopSongsList')]]
    return [[sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("Music Search:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Text("Search:", font='Any 16', background_color='#2B475D'), sg.Input(do_not_clear=True, size=(50,1), enable_events=True, key='musicSearchPanel_songSearchInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\search.png', border_width=0, button_color='#2B475D', key='musicSearchPanel_normalSongSearchButton', tooltip="Search Music"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\listSearch.png', border_width=0, button_color='#2B475D', key='musicSearchPanel_listSongSearchButton', tooltip="Music Search - All Results"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\clearInput.png', border_width=0, button_color='#2B475D', key='musicSearchPanel_clearSongSearchInputButton', tooltip="Clear Search")],
    [sg.Frame("The Billboard Hot 100", topSongsListBoxed, relief='flat', background_color='#2B475D', key='topSongsListFrame'), sg.Push(background_color='#2B475D')]], pad=((0,0), (0, 0)), background_color='#2B475D', visible=True, key='musicSearchPanel'),
    ## Music Downloader Panel
     sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("Music Downloader:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Text("YouTube Link:", font='Any 13', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(48,1), enable_events=True, key='musicDownloaderPanel_youtubeUrlInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\clipboard.png', border_width=0, button_color='#2B475D', key='musicDownloaderPanel_pasteClipboardButton', tooltip="Paste Link"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\youtubeDownloader.png', border_width=0, button_color='#2B475D', key='musicDownloaderPanel_openYoutubeButton', tooltip="Open YouTube")],
    [sg.Text("Download Location:", font='Any 13', background_color='#2B475D'), sg.Input(str(pathlib.Path.home() / "Downloads"), do_not_clear=True, size=(50,1), enable_events=True, key='musicDownloaderPanel_downloadLocationInput'), sg.FolderBrowse(key='musicDownloaderPanel_fileBrowseButton')],
    [sg.HorizontalSeparator()], [sg.Push(background_color='#2B475D'), sg.Text("Downloader Settings:", font='Any 15', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\reset.png', border_width=0, button_color='#2B475D', key='musicDownloaderPanel_resetSettings', tooltip="Reset Settings")],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\true.png', border_width=0, button_color='#2B475D', key='musicDownloaderPanel_burnLyricsCheckbox'), sg.Text("Burn lyrics to the audio file", font='Any 14', background_color='#2B475D')],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\false.png', border_width=0, button_color='#2B475D', key='musicDownloaderPanel_compilationCheckbox'), sg.Text("Song's album is a compilation by various artists", font='Any 14', background_color='#2B475D')],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\false.png', border_width=0, button_color='#2B475D', key='musicDownloaderPanel_changeNameCheckbox'), sg.Text("Custom rename to:", font='Any 14', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(36,1), enable_events=True, visible=False, key='musicDownloaderPanel_changeNameInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\clipboard_Small.png', border_width=0, button_color='#2B475D', visible=False, key='musicDownloaderPanel_changeNameClipboard', tooltip="Paste Link"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\clearInput.png', border_width=0, button_color='#2B475D', visible=False, key='musicDownloaderPanel_changeNameClearInput', tooltip="Paste Link")],
    [sg.HorizontalSeparator()], [sg.Text("", font='Any 4', background_color='#2B475D')], [sg.Push(background_color='#2B475D'), sg.Button("Download", button_color=("White", "Blue"), font='Any 15', size=(10, 1), key='musicDownloaderPanel_downloadButton'), sg.Push(background_color='#2B475D')]], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='musicDownloaderPanel'),
    ## YouTube Downloader Panel
     sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("YouTube Downloader:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Text("YouTube Link:", font='Any 13', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(48,1), enable_events=True, key='youtubeDownloaderPanel_youtubeUrlInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\clipboard.png', border_width=0, button_color='#2B475D', key='youtubeDownloaderPanel_pasteClipboardButton', tooltip="Paste Link"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\youtubeDownloader.png', border_width=0, button_color='#2B475D', key='youtubeDownloaderPanel_openYoutubeButton', tooltip="Open YouTube")],
    [sg.Text("Download Location:", font='Any 13', background_color='#2B475D'), sg.Input(str(pathlib.Path.home() / "Downloads"), do_not_clear=True, size=(50,1), enable_events=True, key='youtubeDownloaderPanel_downloadLocationInput'), sg.FolderBrowse(key='youtubeDownloaderPanel_fileBrowseButton')],
    [sg.HorizontalSeparator()], [sg.Push(background_color='#2B475D'), sg.Text("Downloader Settings:", font='Any 15', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\reset.png', border_width=0, button_color='#2B475D', key='youtubeDownloaderPanel_resetSettings', tooltip="Reset Settings")],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\false.png', border_width=0, button_color='#2B475D', key='youtubeDownloaderPanel_audioDownloadCheckbox'), sg.Text("Download audio file (.MP3) of the YouTube Video", font='Any 14', background_color='#2B475D')],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\true.png', border_width=0, button_color='#2B475D', key='youtubeDownloaderPanel_videoDownloadCheckbox'), sg.Text("Download video file (.MP4) of the YouTube Video", font='Any 14', background_color='#2B475D')],
    [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\false.png', border_width=0, button_color='#2B475D', key='youtubeDownloaderPanel_changeNameCheckbox'), sg.Text("Rename download to:", font='Any 14', background_color='#2B475D'), sg.Input("", do_not_clear=True, size=(33,1), enable_events=True, visible=False, key='youtubeDownloaderPanel_changeNameInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\clipboard_Small.png', border_width=0, button_color='#2B475D', visible=False, key='youtubeDownloaderPanel_changeNameClipboard', tooltip="Paste Clipboard"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\clearInput.png', border_width=0, button_color='#2B475D', visible=False, key='youtubeDownloaderPanel_changeNameClearInput', tooltip="Clear Input")],
    [sg.HorizontalSeparator()], [sg.Text("", font='Any 4', background_color='#2B475D')], [sg.Push(background_color='#2B475D'), sg.Button("Download", button_color=("White", "Blue"), font='Any 15', size=(10, 1), key='youtubeDownloaderPanel_downloadButton'), sg.Push(background_color='#2B475D')]], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='youtubeDownloaderPanel'),
    ## CD Burner Panel
    sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("CD Burner:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')]
    ], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='cdburnerPanel'),
    ## Extra Apps Panel
    sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("All Music Tools:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Column(toolsPanel, size=(595,390), pad=((10,10), (10, 10)), background_color='#2B475D')]], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='musicToolsPanel'),
    ## Settings Panel
    sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("Settings:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')]
    ], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='settingsPanel'),
    ## Lyrics Checker Panel
     sg.Column([[sg.Push(background_color='#2B475D'), sg.Text("Lyrics Checker:", font='Any 20 bold', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Push(background_color='#2B475D'), sg.Multiline("", size=(63,18), font='Any 11', autoscroll=False, disabled=False, right_click_menu=['', ['Copy', 'Lookup Definition', 'Add to Profanity Engine', 'Remove from Profanity Engine']], key='lyricsCheckerPanel_lyricsInput'), sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\openWeb.png', border_width=0, button_color='#2B475D', key='lyricsCheckerPanel_openWebButton')], [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\clipboard_Small.png', border_width=0, button_color='#2B475D', key='lyricsCheckerPanel_pasteClipboardButton')], [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\clearInput.png', border_width=0, button_color='#2B475D', key='lyricsCheckerPanel_clearInputButton')], [sg.Text("", font='Any 14', background_color='#2B475D')], [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\checkInput.png', border_width=0, button_color='#2B475D', key='lyricsCheckerPanel_checkLyricsButton')]], vertical_alignment='b', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
    [sg.Push(background_color='#2B475D'), sg.Text("Profanity Engine: Not checked yet", font='Any 11', background_color='#2B475D', key='lyricsCheckerPanel_songUsableText'), sg.Push(background_color='#2B475D')]], pad=((0,0), (0, 0)), background_color='#2B475D', visible=False, key='lyricsCheckerPanel'),
    ]]

def homeScreen():
    global firstHomeLaunch, HomeWindow, homeWindowLocationX, homeWindowLocationY, lyrics, lyricsListFinal, wifiStatus
    ## Oszust OS Music Tools List
    if wifiStatus: applist, apps = [[]], ["Music Search", "Music Downloader", "YouTube Downloader", "Music Tools"] ## "Music Search", "Music Downloader", "YouTube Downloader", "CD Burner", "Music Tools", "Settings"
    else: applist, apps = [[]], ["CD Burner", "Music Tools", "Settings"]
    for app in apps: applist += [[sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent) + "\\data\\" + app.lower().replace(" ", "") + ".png", button_color='#657076', border_width=0, key=app.replace(" ", "_") + '_AppSelector', tooltip='Open ' + app)]], pad=((5,5), (5, 5)), background_color='#657076')]] ## Add Apps to Side Panel
    ## Home Window
    layout = [[sg.Column(applist, size=(72,390), pad=((10,10), (10, 10)), background_color='#2B475D', scrollable=False, vertical_scroll_only=True), sg.Column(homeScreenAppPanels(), size=(595,390), pad=((10,10), (10, 10)), background_color='#2B475D', scrollable=False, vertical_scroll_only=True)]]
    if wifiStatus: layout += [[sg.Column([[sg.Text(platform.system() + " | " + softwareVersion + " | " + systemBuild + " | Online", enable_events=True, font='Any 13', background_color='#5A6E80', key='versionTextHomeBottom'), sg.Push(background_color='#5A6E80'), sg.Text("Oszust Industries", enable_events=True, font='Any 13', background_color='#5A6E80', key='creditsTextHomeBottom')], [sg.Column([[]], size=(710, 1), pad=(0,0))]], size=(710, 30), pad=(0,0), background_color='#5A6E80')]]
    else: layout += [[sg.Column([[sg.Text(platform.system() + " | " + softwareVersion + " | " + systemBuild + " |", enable_events=True, font='Any 13', background_color='#5A6E80', key='versionTextHomeBottom'), sg.Text("OFFLINE", enable_events=True, font='Any 13', background_color='#5A6E80', key='wifiTextHomeBottom'), sg.Push(background_color='#5A6E80'), sg.Text("Oszust Industries", enable_events=True, font='Any 13', background_color='#5A6E80', key='creditsTextHomeBottom')], [sg.Column([[]], size=(710, 1), pad=(0,0))]], size=(710, 30), pad=(0,0), background_color='#5A6E80')]]
    HomeWindow = sg.Window('Oszust OS Music Tools', layout, background_color='#657076', margins=(0,0), finalize=True, resizable=False, text_justification='r')
    ## Music Search: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    HomeWindow['musicSearchPanel_billboardTopSongsList'].bind('<Return>', '_Enter')  ## Enter on Top 100 list
    HomeWindow['musicSearchPanel_songSearchInput'].bind('<Return>', '_Enter')        ## Enter on Song Search
    for key in ['normalSongSearchButton', 'listSongSearchButton', 'clearSongSearchInputButton', 'billboardTopSongsList']: HomeWindow['musicSearchPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## Music Downloader: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    musicBurnLyrics, musicCompilationAlbum, musicDownloadName = True, False, False ## App Variables
    for key in ['pasteClipboardButton', 'openYoutubeButton', 'fileBrowseButton', 'resetSettings', 'burnLyricsCheckbox', 'compilationCheckbox', 'changeNameCheckbox', 'changeNameClipboard', 'changeNameClearInput', 'downloadButton']: HomeWindow['musicDownloaderPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## YouTube Downloader: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    youtubeAudioDownload, youtubeVideoDownload, youtubeDownloadName = False, True, False ## App Variables
    for key in ['pasteClipboardButton', 'openYoutubeButton', 'fileBrowseButton', 'resetSettings', 'audioDownloadCheckbox', 'videoDownloadCheckbox', 'changeNameCheckbox', 'changeNameClipboard', 'changeNameClearInput', 'downloadButton']: HomeWindow['youtubeDownloaderPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## Lyrics Checker: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    for key in ['openWebButton', 'pasteClipboardButton', 'clearInputButton', 'checkLyricsButton']: HomeWindow['lyricsCheckerPanel_' + key].Widget.config(cursor="hand2") ## Hover icons
    ## Main Window: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    for key in ['versionTextHomeBottom', 'creditsTextHomeBottom']: HomeWindow[key].Widget.config(cursor="hand2") ## Hover icons
    if wifiStatus == False:
        HomeWindow['wifiTextHomeBottom'].Widget.config(cursor="hand2") ## Hover icon
        HomeWindow['musicToolsPanel'].update(visible=True)
        HomeWindow['musicSearchPanel'].update(visible=False)
    for app in apps: HomeWindow[app.replace(" ", "_") + "_AppSelector"].Widget.config(cursor="hand2") ## App Side Panel hover icons
    appSelected, firstHomeLaunch = "Music_Search", False ## App Variables
    ## Reading Home Window
    while True:
        event, values = HomeWindow.read(timeout=10)
        homeWindowLocationX, homeWindowLocationY = HomeWindow.CurrentLocation() ## X & Y Location of Home Window
## Closed Window
        if event == sg.WIN_CLOSED or event == 'Exit':
            HomeWindow.close()
            thisSystem = psutil.Process(os.getpid()) ## Close Program
            thisSystem.terminate()
## Home Screen Bottom Text
        elif event == 'versionTextHomeBottom': webbrowser.open("https://github.com/Oszust-Industries/" + systemName.replace(" ", "-") + "/releases", new=2, autoraise=True) ## Home Screen: Version Text
        elif event == 'creditsTextHomeBottom': webbrowser.open("https://github.com/Oszust-Industries/", new=2, autoraise=True) ## Home Screen: Credits Button
        elif event == 'wifiTextHomeBottom':
            HomeWindow.close()
            softwareSetup()
            break
## Side Panel Apps (Buttons)
        elif "_AppSelector" in event and event.replace("_AppSelector", "") != appSelected:
            appSelected = event.replace("_AppSelector", "")
            for app in toolPanelApps:
                if app.replace(" ", "_") == appSelected: HomeWindow[(app[:4].lower() + app[4:]).replace(" ", "") + "Panel"].update(visible=True)
                else: HomeWindow[(app[:4].lower() + app[4:]).replace(" ", "") + "Panel"].update(visible=False)
            if appSelected == "Music_Tools": HomeWindow["musicToolsPanel"].update(visible=True) ## Show Music Tools Window
            elif appSelected != "Music_Tools": HomeWindow["musicToolsPanel"].update(visible=False) ## Hide Music Tools Window
            elif appSelected == "Music_Downloader": ## Shows Terms of Service Popup
                try: pickle.load(open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\contract.p", "rb"))
                except:
                    popupMessage("Terms of Service", "Songs downloaded from Music Downloader can't be used in a public setting.\t\tUsing songs on the radio or anywhere public would be voilating YouTube's Terms of Service and FCC laws.", "announcement")
                    pickle.dump(True, open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\contract.p", "wb"))
## Music Tools
        elif appSelected == "Music_Tools":
            if "musicTool_" in event:
                appSelected = event.replace("musicTool_", "")
                for tool in toolPanelApps:
                    if tool.replace(" ", "_") == appSelected: HomeWindow[(tool[:4].lower() + tool[4:]).replace(" ", "") + "Panel"].update(visible=True)
                    else: HomeWindow[(tool[:4].lower() + tool[4:]).replace(" ", "") + "Panel"].update(visible=False)
                HomeWindow["musicToolsPanel"].update(visible=False)
## Music Search (Buttons/Events)
        elif appSelected == "Music_Search":
            if (event == 'musicSearchPanel_normalSongSearchButton' or (event == 'musicSearchPanel_songSearchInput' + '_Enter')) and values['musicSearchPanel_songSearchInput'].replace(" ","").lower() not in ["", "resultfailedtoload", "billboardtop100failedtoload"]: geniusMusicSearch(values['musicSearchPanel_songSearchInput'], False) ## Music Search
            elif event == 'musicSearchPanel_listSongSearchButton' and values['musicSearchPanel_songSearchInput'].replace(" ","").lower() not in ["", "resultfailedtoload", "billboardtop100failedtoload"]: geniusMusicSearchList(values['musicSearchPanel_songSearchInput']) ## Music Search All Results
            elif event == 'musicSearchPanel_clearSongSearchInputButton': HomeWindow.Element('musicSearchPanel_songSearchInput').Update("") ## Clear Music Search Input
            elif event == 'musicSearchPanel_billboardTopSongsList' and values['musicSearchPanel_billboardTopSongsList'][0].split(". ", 1)[1].split("   (", 1)[0].replace(" ","").lower() not in ["", "resultfailedtoload", "billboardtop100failedtoload"]: HomeWindow.Element('musicSearchPanel_songSearchInput').Update(values['musicSearchPanel_billboardTopSongsList'][0].split(". ", 1)[1].split("   (", 1)[0]) ## Copy Top 100 to Music Search
            elif (event == 'musicSearchPanel_billboardTopSongsList' + '_Enter'): geniusMusicSearch(values['musicSearchPanel_billboardTopSongsList'][0].split(". ", 1)[1].split("   (", 1)[0], False) ## Top 100 Song Search
## Music Downloader (Buttons/Events)
        elif appSelected == "Music_Downloader":
            if event == 'musicDownloaderPanel_pasteClipboardButton': ## Paste Clipboard in YouTube Link Input
                win32clipboard.OpenClipboard()
                HomeWindow.Element('musicDownloaderPanel_youtubeUrlInput').Update(win32clipboard.GetClipboardData())
                win32clipboard.CloseClipboard()
            elif event == 'musicDownloaderPanel_openYoutubeButton': webbrowser.open("youtube.com", new=2, autoraise=True) ## Open YouTube Website
            elif event == 'musicDownloaderPanel_resetSettings': ## Reset Settings
                musicBurnLyrics, musicCompilationAlbum, musicDownloadName = True, False, False
                HomeWindow['musicDownloaderPanel_burnLyricsCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png')
                HomeWindow['musicDownloaderPanel_compilationCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                HomeWindow['musicDownloaderPanel_changeNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                HomeWindow.Element('musicDownloaderPanel_changeNameInput').Update("")
                for key in ['musicDownloaderPanel_changeNameInput', 'musicDownloaderPanel_changeNameClipboard', 'musicDownloaderPanel_changeNameClearInput']: HomeWindow.Element(key).Update(visible=False)
            elif event == 'musicDownloaderPanel_burnLyricsCheckbox' and musicBurnLyrics == True: ## Burn Lyrics - False
                HomeWindow['musicDownloaderPanel_burnLyricsCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                musicBurnLyrics = False
            elif event == 'musicDownloaderPanel_burnLyricsCheckbox' and musicBurnLyrics == False: ## Burn Lyrics - True
                HomeWindow['musicDownloaderPanel_burnLyricsCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png')
                musicBurnLyrics = True
            elif event == 'musicDownloaderPanel_compilationCheckbox' and musicCompilationAlbum == True: ## Compilation Album - False
                HomeWindow['musicDownloaderPanel_compilationCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                musicCompilationAlbum = False
            elif event == 'musicDownloaderPanel_compilationCheckbox' and musicCompilationAlbum == False: ## Compilation Album - True
                HomeWindow['musicDownloaderPanel_compilationCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png')
                musicCompilationAlbum = True
            elif event == 'musicDownloaderPanel_changeNameCheckbox' and musicDownloadName == True: ## Change File Name - False
                HomeWindow['musicDownloaderPanel_changeNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                for key in ['musicDownloaderPanel_changeNameInput', 'musicDownloaderPanel_changeNameClipboard', 'musicDownloaderPanel_changeNameClearInput']: HomeWindow.Element(key).Update(visible=False)
                musicDownloadName = False
            elif event == 'musicDownloaderPanel_changeNameCheckbox' and musicDownloadName == False: ## Change File Name - True
                HomeWindow['musicDownloaderPanel_changeNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png')
                for key in ['musicDownloaderPanel_changeNameInput', 'musicDownloaderPanel_changeNameClipboard', 'musicDownloaderPanel_changeNameClearInput']: HomeWindow.Element(key).Update(visible=True)
                musicDownloadName = True
            elif event == 'musicDownloaderPanel_changeNameClipboard': ## Paste Clipboard in File Name Input
                win32clipboard.OpenClipboard()
                HomeWindow.Element('musicDownloaderPanel_changeNameInput').Update(win32clipboard.GetClipboardData())
                win32clipboard.CloseClipboard()
            elif event == 'musicDownloaderPanel_changeNameClearInput': HomeWindow.Element('musicDownloaderPanel_changeNameInput').Update("") ## Clear File Name Input
            elif event == 'musicDownloaderPanel_downloadButton' and "youtube.com" in values['musicDownloaderPanel_youtubeUrlInput'].lower(): ## Download Music Button
                if youtubeDownloadName: youtubeDownloadName = values['musicDownloaderPanel_changeNameInput']
                loadingScreen("Music_Downloader", values['musicDownloaderPanel_youtubeUrlInput'], values['musicDownloaderPanel_downloadLocationInput'], musicBurnLyrics, musicCompilationAlbum, musicDownloadName)
                HomeWindow["musicDownloaderPanel_youtubeUrlInput"].update("")
## YouTube Downloader (Buttons/Events)
        elif appSelected == "YouTube_Downloader":
            if event == 'youtubeDownloaderPanel_pasteClipboardButton': ## Paste Clipboard in YouTube Link Input
                win32clipboard.OpenClipboard()
                HomeWindow.Element('youtubeDownloaderPanel_youtubeUrlInput').Update(win32clipboard.GetClipboardData())
                win32clipboard.CloseClipboard()
            elif event == 'youtubeDownloaderPanel_openYoutubeButton': webbrowser.open("youtube.com", new=2, autoraise=True) ## Open YouTube Website
            elif event == 'youtubeDownloaderPanel_resetSettings': ## Reset Settings
                youtubeAudioDownload, youtubeVideoDownload, youtubeDownloadName = False, True, False
                HomeWindow['youtubeDownloaderPanel_audioDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                HomeWindow['youtubeDownloaderPanel_videoDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png')
                HomeWindow['youtubeDownloaderPanel_changeNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                HomeWindow.Element('youtubeDownloaderPanel_changeNameInput').Update("")
                for key in ['youtubeDownloaderPanel_changeNameInput', 'youtubeDownloaderPanel_changeNameClipboard', 'youtubeDownloaderPanel_changeNameClearInput']: HomeWindow.Element(key).Update(visible=False)
            elif event == 'youtubeDownloaderPanel_audioDownloadCheckbox' and youtubeAudioDownload == True: ## Download Audio - False
                HomeWindow['youtubeDownloaderPanel_audioDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                youtubeAudioDownload = False
            elif event == 'youtubeDownloaderPanel_audioDownloadCheckbox' and youtubeAudioDownload == False: ## Download Audio - True
                HomeWindow['youtubeDownloaderPanel_audioDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png')
                youtubeAudioDownload = True
            elif event == 'youtubeDownloaderPanel_videoDownloadCheckbox' and youtubeVideoDownload == True: ## Download Video - False
                HomeWindow['youtubeDownloaderPanel_videoDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                youtubeVideoDownload = False
            elif event == 'youtubeDownloaderPanel_videoDownloadCheckbox' and youtubeVideoDownload == False: ## Download Video - True
                HomeWindow['youtubeDownloaderPanel_videoDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png')
                youtubeVideoDownload = True
            elif event == 'youtubeDownloaderPanel_changeNameCheckbox' and youtubeDownloadName == True: ## Change File Name - False
                HomeWindow['youtubeDownloaderPanel_changeNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                for key in ['youtubeDownloaderPanel_changeNameInput', 'youtubeDownloaderPanel_changeNameClipboard', 'youtubeDownloaderPanel_changeNameClearInput']: HomeWindow.Element(key).Update(visible=False)
                youtubeDownloadName = False
            elif event == 'youtubeDownloaderPanel_changeNameCheckbox' and youtubeDownloadName == False: ## Change File Name - True
                HomeWindow['youtubeDownloaderPanel_changeNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png')
                for key in ['youtubeDownloaderPanel_changeNameInput', 'youtubeDownloaderPanel_changeNameClipboard', 'youtubeDownloaderPanel_changeNameClearInput']: HomeWindow.Element(key).Update(visible=True)
                youtubeDownloadName = True
            elif event == 'youtubeDownloaderPanel_changeNameClipboard': ## Paste Clipboard in File Name Input
                win32clipboard.OpenClipboard()
                HomeWindow.Element('youtubeDownloaderPanel_changeNameInput').Update(win32clipboard.GetClipboardData())
                win32clipboard.CloseClipboard()
            elif event == 'youtubeDownloaderPanel_changeNameClearInput': HomeWindow.Element('youtubeDownloaderPanel_changeNameInput').Update("") ## Clear File Name Input
            elif event == 'youtubeDownloaderPanel_downloadButton' and "youtube.com" in values['youtubeDownloaderPanel_youtubeUrlInput'].lower(): ## Download YouTube Button
                if youtubeAudioDownload == False and youtubeVideoDownload == False: popupMessage("YouTube Downloader", "You must select audio or video download.", "error", 5000)
                else:
                    if youtubeDownloadName: youtubeDownloadName = values['youtubeDownloaderPanel_changeNameInput']
                    loadingScreen("YouTube_Downloader", values['youtubeDownloaderPanel_youtubeUrlInput'], values['youtubeDownloaderPanel_downloadLocationInput'], youtubeAudioDownload, youtubeVideoDownload, youtubeDownloadName)
                    HomeWindow["youtubeDownloaderPanel_youtubeUrlInput"].update("")
## Lyrics Checker (Buttons/Events)
        elif appSelected == "Lyrics_Checker":
            if event == 'lyricsCheckerPanel_openWebButton': webbrowser.open("google.com", new=2, autoraise=True) ## Open Web Browser
            elif event == 'lyricsCheckerPanel_pasteClipboardButton': ## Paste Clipboard in Lyrics Input
                    win32clipboard.OpenClipboard()
                    HomeWindow.Element('lyricsCheckerPanel_lyricsInput').Update(win32clipboard.GetClipboardData())
                    win32clipboard.CloseClipboard()
            elif event == 'lyricsCheckerPanel_clearInputButton': ## Clear Lyrics Input
                HomeWindow.Element('lyricsCheckerPanel_lyricsInput').Update("")
                HomeWindow.Element('lyricsCheckerPanel_songUsableText').Update("Profanity Engine: Not checked yet")
            elif event == 'lyricsCheckerPanel_checkLyricsButton' and len(values['lyricsCheckerPanel_lyricsInput'].strip()) > 0:
                lyrics, lyricsListFinal = "userInputed", values['lyricsCheckerPanel_lyricsInput'].splitlines()
                musicSearchPrintSongLyrics("lyricsCheck")

def loadingScreen(functionLoader, agr1=False, arg2=False, arg3=False, arg4=False, arg5=False):
    global loadingStatus
    if firstHomeLaunch == False:
        loadingPopup, loadingStatus = sg.Window("", [[sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", background_color='#1b2838', key='loadingGIFImage')], [sg.Text("Loading...", font='Any 16', background_color='#1b2838', key='loadingScreenText')]], background_color='#1b2838', element_justification='c', no_titlebar=True, keep_on_top=True, finalize=True), "Start"
        loadingPopup.hide()
        loadingPopup.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - loadingPopup.size[0] // 2, HomeWindow.TKroot.winfo_y() + HomeWindow.TKroot.winfo_height() // 2 - loadingPopup.size[1] // 2)
        loadingPopup.un_hide()
    else: loadingPopup, loadingStatus = sg.Window("", [[sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", background_color='#1b2838', key='loadingGIFImage')], [sg.Text("Downloading Billboard Hot 100 Songs...", font='Any 16', background_color='#1b2838', key='loadingScreenText')]], background_color='#1b2838', element_justification='c', no_titlebar=True, keep_on_top=True), "Start"
    loadingPopup["loadingGIFImage"].UpdateAnimation(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", time_between_frames=10) ## Load Loading GIF
    while True:
        event, values = loadingPopup.read(timeout=10)
        loadingPopup["loadingGIFImage"].UpdateAnimation(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", time_between_frames=30) ## Load Loading GIF
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
            popupMessage("YouTube Downloader", "The download of the video failed.\t\t\tPlease try again a little later.", "error")
            break
        elif loadingStatus == "Failed_MusicDownloaderYouTube": ## Music Downloader (YouTube Download) Failed
            loadingPopup.close()
            popupMessage("Music Downloader", "The download of the song failed.\t\t\tPlease try again a little later.", "error")
            break
        elif "Done" in loadingStatus:
            loadingPopup.close()
            if loadingStatus == "Done_YouTubeDownloader": popupMessage("YouTube Downloader", "Video downloaded successfully.", "success")
            elif loadingStatus == "Done_MusicDownloader": popupMessage("Music Downloader", "Song downloaded successfully.", "success")
            break

def popupMessage(popupMessageTitle, popupMessageText, popupMessageIcon, popupTimer=0):
    wrapper = textwrap.TextWrapper(width=45, max_lines=6, placeholder='...')
    popupMessageText = '\n'.join(wrapper.wrap(popupMessageText))
    alpha, messagePopup, timeOpened = 0.9, sg.Window("", [[sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\" + popupMessageIcon + "_Popup.png", background_color='#1b2838', key='loadingGIFImage')], [sg.Text(popupMessageTitle, font='Any 24 bold', background_color='#1b2838', key='messagePopupTitle')], [sg.Text(popupMessageText, font='Any 13', background_color='#1b2838', key='messagePopupMessage')], [sg.Button("OK", font=('Any 12'), button_color=('white','#5A6E80'), key='messagePopupExitButton')]], background_color='#1b2838', element_justification='c', text_justification='c', no_titlebar=True, keep_on_top=True, finalize=True), 0
    messagePopup.hide()
    messagePopup.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - messagePopup.size[0] // 2, HomeWindow.TKroot.winfo_y() + HomeWindow.TKroot.winfo_height() // 2 - messagePopup.size[1] // 2)
    messagePopup.un_hide()
    messagePopup.force_focus()
    ## Window Shortcuts
    messagePopup.bind('<FocusOut>', '_FocusOut')        ## Window Focus Out
    messagePopup.bind('<Delete>', '_Delete')           ## Close Window shortcut
    messagePopup['messagePopupExitButton'].Widget.config(cursor="hand2") ## Hover icons
    while True:
        event, values = messagePopup.read(timeout=100)
        if event == sg.WIN_CLOSED or event == 'messagePopupExitButton' or (event == '_Delete') or (event == '_FocusOut' and popupTimer != 0 and timeOpened >= 100):
            messagePopup.close()
            break
        elif popupTimer != 0 and timeOpened >= popupTimer: ## Fade Out Window (3000)
            for i in range(int(alpha*100),1,-1): ## Start Fade Out
                messagePopup.set_alpha(i/150)
                event, values = messagePopup.read(timeout=20)
                if event != sg.TIMEOUT_KEY: break
            messagePopup.close()
            break
        timeOpened += 100

## Music Tools

def downloadYouTube(youtubeLink, downloadLocation, audioFile, videoFile, renameFile):
    global audioSavedPath, loadingStatus, youtubeTitle
    try: YouTube(youtubeLink).streams.filter(file_extension="mp4").get_highest_resolution().download(downloadLocation) ## Download Video
    except:
        loadingStatus = "Failed_YouTubeDownloader"
        return
    youtubeTitle = (YouTube(youtubeLink).title).replace("|", "").replace("'", "").replace("/", "").replace("#", "").replace(".", "") ## Downloaded File's Name
    if audioFile: ## Convert MP4 Video to MP3 Audio
        audioSavedPath, loadingStatus = downloadLocation + "\\" + youtubeTitle + ".mp3", "Downloading Audio File..." ## MP3 File Name
        FILETOCONVERT = AudioFileClip(downloadLocation + "\\" + youtubeTitle + ".mp4")
        FILETOCONVERT.write_audiofile(audioSavedPath)
        FILETOCONVERT.close()
        if renameFile != False: ## Rename MP3 File
            loadingStatus = "Renaming Audio File..."
            try: os.rename(audioSavedPath, audioSavedPath.replace(audioSavedPath.rsplit('\\', 1)[1], "") + "\\" + renameFile + "." + audioSavedPath.rsplit('.', 1)[1]) ## Raname MP3 to Chosen Name
            except: pass
    if renameFile != False: ## Rename MP4 File
        loadingStatus = "Renaming Video File..."
        videoSavedLocation = downloadLocation + "\\" + youtubeTitle + ".mp4"
        try: os.rename(videoSavedLocation, videoSavedLocation.replace(videoSavedLocation.rsplit('\\', 1)[1], "") + "\\" + renameFile + "." + videoSavedLocation.rsplit('.', 1)[1]) ## Raname MP4 to Chosen Name
        except: pass
    if videoFile == False: os.remove(downloadLocation + "\\" + youtubeTitle + ".mp4") ## Delete video file if audio is only needed
    loadingStatus = "Done_YouTubeDownloader"

def downloadAudio(youtubeLink, downloadLocation):
    global audioSavedPath, loadingStatus, youtubeTitle
    try: YouTube(youtubeLink).streams.filter(file_extension="mp4").get_highest_resolution().download(downloadLocation) ## Download Video
    except:
        loadingStatus = "Failed_MusicDownloaderYouTube"
        return
    youtubeTitle = (YouTube(youtubeLink).title).replace("|", "").replace("'", "").replace("/", "").replace("#", "").replace(".", "") ## Downloaded File's Name
    audioSavedPath, loadingStatus = downloadLocation + "\\" + youtubeTitle + ".mp3", "Downloading Audio File..." ## MP3 File Name
    FILETOCONVERT = AudioFileClip(downloadLocation + "\\" + youtubeTitle + ".mp4")
    FILETOCONVERT.write_audiofile(audioSavedPath)
    FILETOCONVERT.close()
    os.remove(downloadLocation + "\\" + youtubeTitle + ".mp4") ## Delete video file
    ## Remove extra characters from YouTube title for Music Search
    youtubeTitle = re.sub("([\(\[]).*?([\)\]])", "\g<1>\g<2>", youtubeTitle)
    loadingStatus = "Done_MusicDownloader"

def loadGeniusMusic(userInput, forceResult):
    from PIL import Image
    import bs4, cloudscraper, io, re
    global geniusMusicSearchAlbum, geniusMusicSearchAlbumCurrent, geniusMusicSearchAlbumLength, geniusMusicSearchArtistURL, geniusMusicSearchArtists, geniusMusicSearchDate, geniusMusicSearchGeniusURL, geniusMusicSearchGenre, geniusMusicSearchLabels, geniusMusicSearchPrimeArtist, geniusMusicSearchSongName, geniusMusicSearchSongNameInfo, hitsFound, loadingAction, lyrics, lyricsListFinal, png_data
    artistSearch, goodResult, hitsFound, resultCount = False, False, 1, 0
    if "genius.com" in userInput: userInput = userInput.split("https://genius.com/",1)[1].split("-lyrics",1)[0] ## Genius Website URL
    if "/songs/" in userInput: request = urllib.request.Request("http://api.genius.com" + userInput) ## Song ID Search
    else: request = urllib.request.Request("http://api.genius.com/search?q=" + urllib.request.quote(userInput.lower().replace(" by ", "-").split("-featuring")[0]) + "&page=1")
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
        musicSearchApiBody = json.loads(raw)["response"]["hits"]
        if len(musicSearchApiBody) > 0: musicSearchApiBodyPath = musicSearchApiBody[0]["result"]
    except: musicSearchApiBody, musicSearchApiBodyPath = json.loads(raw)["response"]["song"], json.loads(raw)["response"]["song"]
    hitsFound = len(musicSearchApiBody)
    if hitsFound == 0: ## Check if Result Found
        loadingAction = "No_Result_Found"
        return
    while goodResult == False:
        lyricsList, lyricsListFinal = [], []
        if artistSearch == False or str(musicSearchApiBodyPath["artist_names"]).replace("\u200b","").replace(" ", "-").split('(')[0].lower() == userInput: ## Check if Search is Artist
            if forceResult == False and str(musicSearchApiBodyPath["artist_names"]).replace(" ", "-").lower() == userInput: ## Change to Artist Search
                loadingAction = "Artist_Search"
                return
            ## Finish Normal Search
            try: geniusMusicSearchArtists = str(musicSearchApiBodyPath["artist_names"]).replace("(Rock)", "") ## Song Artists
            except: ## No Results Left
                loadingAction = "No_Result_Found"
                return
            geniusMusicSearchPrimeArtist = str(musicSearchApiBodyPath["primary_artist"]["name"]).split('(')[0] ## Song Main Artist
            geniusMusicSearchDate = str(musicSearchApiBodyPath["release_date_for_display"]) ## Song Release Date
            if geniusMusicSearchDate == "None": geniusMusicSearchDate = None ## Fix Release Date if None Found
            geniusMusicSearchSongNameInfo = str(musicSearchApiBodyPath["title_with_featured"]) ## Song Full Title
            geniusMusicSearchArtistURL = str(musicSearchApiBodyPath["primary_artist"]["url"])
            geniusMusicSearchGeniusURL = str(musicSearchApiBodyPath["url"]) ## Song Genius URL
            geniusMusicSearchSongName = str(musicSearchApiBodyPath["title"]) ## Song Title
            ## Song Artwork
            try:
                geniusMusicSearchArtworkURL = str(musicSearchApiBodyPath["song_art_image_url"])
                if "https://assets.genius.com/images/default_cover_image.png" in geniusMusicSearchArtworkURL: png_data = str(pathlib.Path(__file__).resolve().parent) + "\\data\\defaultMusicArtwork.png"
                else:
                    try: ## Look in Cache for Artwork
                        pil_image = Image.open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Music Search\\Artworks\\" + str(musicSearchApiBodyPath["song_art_image_url"]).split(".com/",1)[1].split(".",1)[0] + ".png")
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
                            pathlib.Path(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Music Search\\Artworks").mkdir(parents=True, exist_ok=True) ## Create Music Artwork Cache Folder
                            png_data = pil_image.save(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Music Search\\Artworks\\" + str(musicSearchApiBodyPath["song_art_image_url"]).split(".com/",1)[1].split(".",1)[0] + ".png")
                        except: pass
                        png_data = png_bio.getvalue()
            except: png_data = str(pathlib.Path(__file__).resolve().parent) + "\\data\\defaultMusicArtwork.png"
            ## Album, Album List, Genre, and Label
            try: html = bs4.BeautifulSoup((requests.get(geniusMusicSearchGeniusURL)).text, "html.parser") # Scrape the info from the HTML
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
                geniusMusicSearchAlbum = ((re.sub(r'<.+?>', '', str(songScrapedInfo))).replace("[", "").replace("]", "").replace("&amp;", "&")).split(" (")[0] ## Song Album
                if len(geniusMusicSearchAlbum) == 0: geniusMusicSearchAlbum = None ## No Album Found
            except: geniusMusicSearchAlbum = None
            try: ## Album List
                songScrapedInfo, albumList = str(html.select("div[class*=AlbumTracklist__Track]")).split('</a>'), [] ## Song's Album List
                for song in songScrapedInfo:
                    if song.count('.') >= 4: geniusMusicSearchAlbumCurrent = len(albumList) + 1 ## Current Song Position
                    albumList.append(song)
                geniusMusicSearchAlbumLength = len(albumList)
            except: geniusMusicSearchAlbumCurrent, geniusMusicSearchAlbumLength = None, None
            try: ## Song's Genre
                infoList = str(html.select("div[class*=SongTags__Container]")).split('</a>') ## Song Genre Container
                geniusMusicSearchGenre = (re.sub(r'<.+?>', '', str(infoList[0]))).replace("[", "").replace("]", "").replace("&amp;", "&") ## Song Genre
            except: geniusMusicSearchGenre = None
            try: ## Record Label
                songScrapedInfo = html.select("div[class*=SongInfo__Credit]") ## Song's Label Container
                songScrapedInfo = (str(songScrapedInfo).split("Label</div><div>")[1]).split("</a></div></div>")[0]
                geniusMusicSearchLabels = ((re.sub(r'<.+?>', '', str(songScrapedInfo))).replace(" &amp; ", ",,,").replace(" ,,,", ",,,").replace(" (Label)", "")).split(',,,') ## Song's Labels
                for blacklist in [", Release Date", ", Publishers", ", Distributor", ", Copyright", " Copyright", ", Recorded At", ", Assistant Mix Engineer", ", Writer", ", Phonographic", ", Vocal Programmer", ", Background Vocals", ", Mastered at"]:  geniusMusicSearchLabels = str(geniusMusicSearchLabels).split(blacklist)[0].replace("\\u200b", "") ## Put Labels in List
                geniusMusicSearchLabels = str(geniusMusicSearchLabels).split(',') ## Split Labels
                if len(geniusMusicSearchLabels) > 3: geniusMusicSearchLabels = geniusMusicSearchLabels[:3] ## Shorten Labels List
            except: geniusMusicSearchLabels = None
            ## Song Lyrics
            if str(musicSearchApiBodyPath["lyrics_state"]).lower() == "complete":
                try:
                    lyrics, count = html.select("div[class*=Lyrics__Container]"), 1
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
            if "/songs/" in userInput or geniusMusicSearchArtists.lower() not in ["spotify", "genius"]: goodResult = True ## Good Result Found
            elif resultCount < hitsFound: resultCount += 1 ## Move to Next Result
            else:loadingAction = "No_Result_Found" ## No Good Result Found
    loadingAction = "Search_Finished"

def geniusMusicSearch(userInput, forceResult):
    global extendedSongInfo, geniusMusicSearchAlbum, geniusMusicSearchAlbumCurrent, geniusMusicSearchAlbumLength, geniusMusicSearchArtistURL, geniusMusicSearchArtists, geniusMusicSearchDate, geniusMusicSearchGeniusURL, geniusMusicSearchGenre, geniusMusicSearchLabels, geniusMusicSearchPrimeArtist, geniusMusicSearchSongName, geniusMusicSearchSongNameInfo, loadingAction, MusicSearchSongWindow, png_data
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
            popupMessage("Music Search Error", loadingAction.split("Genius_Page_Down:",1)[1] + "\t\t\t\t\tPlease try again a little later.", "error")
            return
        elif loadingAction == "Genius_Page_Down": ## Genius's Service is Down
            loadingPopup.close() ## Close Loading Popup
            popupMessage("Music Search Error", "Genius is down.\t\t\t\t\tPlease try again a little later.", "error")
            return
        elif loadingAction == "Genius_Robot_Check": ## Genius is Checking Robot
            loadingPopup.close() ## Close Loading Popup
            popupMessage("Music Search Error", "Genius thinks you're a robot.\t\t\t\t\tPlease disable your VPN.", "error")
            return
        elif loadingAction == "Artist_Search": ## Start Artist Search
            loadingPopup.close()
            geniusMusicSearchList(userInput)
            return
        elif loadingAction == "Search_Finished": ## Show Music Search Window
            loadingPopup.close()
            break
    ## Shorten Results
    extendedSongInfo = [geniusMusicSearchSongNameInfo, geniusMusicSearchArtists, geniusMusicSearchAlbum]
    if geniusMusicSearchSongNameInfo != None and len(geniusMusicSearchSongNameInfo) > 42: geniusMusicSearchSongNameInfo = geniusMusicSearchSongNameInfo[:39] + "..." ## Shorten Song Name
    if geniusMusicSearchArtists != None and len(geniusMusicSearchArtists) > 45: geniusMusicSearchArtists = geniusMusicSearchArtists[:42] + "..." ## Shorten Artists Names
    if geniusMusicSearchAlbum != None and len(geniusMusicSearchAlbum) > 45: geniusMusicSearchAlbum = geniusMusicSearchAlbum[:42] + "..." ## Shorten Album Name
    ## Song Window
    if lyrics != None: lyricsRightClickMenu = ['', ['Copy', 'Lookup Definition', 'Add to Profanity Engine', 'Remove from Profanity Engine']] ## Lyrics Right Click Menu - Profanity Engine
    else: lyricsRightClickMenu = ['', ['Copy', 'Lookup Definition']] ## Lyrics Right Click Menu - No Profanity Engine
    if hitsFound > 1: layout = [[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchMenu.png', border_width=0, button_color='#2B475D', key='musicSearchResultsMenu', tooltip="All Results"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\personSearch.png', border_width=0, button_color='#2B475D', key='musicSearchArtistResultsMenu', tooltip="Search Artist"), sg.Push(background_color='#2B475D'), sg.Text("Music Search Result", font='Any 20', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchMP3Opener.png', border_width=0, button_color='#2B475D', key='downloadMetadataMp3Button', tooltip="Burn Metadata to MP3")]]
    else: layout = [[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\personSearch.png', border_width=0, button_color='#2B475D', key='musicSearchArtistResultsMenu', tooltip="Search Artist"), sg.Push(background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Text("Music Search Result", font='Any 20', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchMP3Opener.png', border_width=0, button_color='#2B475D', key='downloadMetadataMp3Button', tooltip="Burn Metadata to MP3")]]
    if musicSub == "Apple": layout += [[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchArtist.png', border_width=0, button_color='#2B475D', key='musicSearchArtistButton', tooltip="Open Artist page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchGenius.png', border_width=0, button_color='#2B475D', key='searchmusicSearchGenius', tooltip="Open Genius Lyrics page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchListenApple.png', border_width=0, button_color='#2B475D', key='musicSearchListenButton', tooltip="Play Song - Apple Music")]]
    elif layout == "Spotify": layout += [[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchArtist.png', border_width=0, button_color='#2B475D', key='musicSearchArtistButton', tooltip="Open Artist page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchGenius.png', border_width=0, button_color='#2B475D', key='searchmusicSearchGenius', tooltip="Open Genius Lyrics page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchListenSpotify.png', border_width=0, button_color='#2B475D', key='musicSearchListenButton', tooltip="Play Song - Spotify")]]
    if geniusMusicSearchAlbum != None and geniusMusicSearchDate != None: layout += [[sg.Image(png_data)], [sg.Text(geniusMusicSearchSongNameInfo, font='Any 20 bold', background_color='#2B475D', enable_events=True, key='geniusMusicSearchSongNameInfoText', tooltip=extendedSongInfo[0])], [sg.Text(geniusMusicSearchAlbum, font='Any 18', background_color='#2B475D', enable_events=True, key='geniusMusicSearchAlbumText', tooltip=extendedSongInfo[2])], [sg.Text(geniusMusicSearchArtists, font='Any 16', background_color='#2B475D', enable_events=True, key='geniusMusicSearchArtistsText', tooltip=extendedSongInfo[1])], [sg.Text(geniusMusicSearchGenre.upper() + " " + u"\N{Dot Operator}" + " " + geniusMusicSearchDate, font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchGenreText')]] ## Album Name Found
    elif geniusMusicSearchAlbum != None and geniusMusicSearchDate == None: layout += [[sg.Image(png_data)], [sg.Text(geniusMusicSearchSongNameInfo, font='Any 20 bold', background_color='#2B475D', enable_events=True, key='geniusMusicSearchSongNameInfoText', tooltip=extendedSongInfo[0])], [sg.Text(geniusMusicSearchAlbum, font='Any 18', background_color='#2B475D', enable_events=True, key='geniusMusicSearchAlbumText', tooltip=extendedSongInfo[2])], [sg.Text(geniusMusicSearchArtists, font='Any 16', background_color='#2B475D', enable_events=True, key='geniusMusicSearchArtistsText', tooltip=extendedSongInfo[1])], [sg.Text(geniusMusicSearchGenre.upper(), font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchGenreText')]] ## Album Name Found and No Release Date
    elif geniusMusicSearchAlbum == None and geniusMusicSearchDate != None: layout += [[sg.Image(png_data)], [sg.Text(geniusMusicSearchSongNameInfo, font='Any 20 bold', background_color='#2B475D', enable_events=True, key='geniusMusicSearchSongNameInfoText', tooltip=extendedSongInfo[0])], [sg.Text(geniusMusicSearchArtists, font='Any 16', background_color='#2B475D', enable_events=True, key='geniusMusicSearchArtistsText', tooltip=extendedSongInfo[1])], [sg.Text(geniusMusicSearchGenre.upper() + " " + u"\N{Dot Operator}" + " " + geniusMusicSearchDate, font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchGenreText')]] ## Album Name not Found
    else: layout += [[sg.Image(png_data)], [sg.Text(geniusMusicSearchSongNameInfo, font='Any 20 bold', background_color='#2B475D', enable_events=True, key='geniusMusicSearchSongNameInfoText', tooltip=extendedSongInfo[0])], [sg.Text(geniusMusicSearchArtists, font='Any 16', background_color='#2B475D', enable_events=True, key='geniusMusicSearchArtistsText', tooltip=extendedSongInfo[1])], [sg.Text(geniusMusicSearchGenre.upper(), font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchGenreText')]] ## No Album Name and No Release Date
    if lyrics != None: layout += [[sg.Multiline("", size=(55,20), font='Any 11', autoscroll=False, disabled=False, right_click_menu=lyricsRightClickMenu, key='MusicSearchSongWindowLyrics')]] ## Add Empty Lyrics Box
    else: layout += [[sg.Text("Lyrics couldn't be found on Genius.", font='Any 12 bold', background_color='#2B475D')]] ## No Lyrics Found Message
    if lyrics != None: layout += [[sg.Text("Profanity Engine: Not checked yet", font='Any 11', background_color='#2B475D', key='songUsableText')]] ## Default Profanity Engine Text
    if geniusMusicSearchLabels != None and len(geniusMusicSearchLabels) > 1: layout += [[sg.Text("Labels: " + str(geniusMusicSearchLabels).replace("&amp;", "&").replace("[", "").replace("]", "").replace('"', "").replace("'", ""), font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchLabels')]] ## Song's Labels
    elif geniusMusicSearchLabels != None and len(geniusMusicSearchLabels) == 1: layout += [[sg.Text("Label: " + str(geniusMusicSearchLabels).replace("&amp;", "&").replace("[", "").replace("]", "").replace('"', "").replace("'", ""), font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchLabels')]] ## Song's Label
    layout += [[sg.Text("Music Search powered by Genius", font='Any 11', background_color='#2B475D')]] ## Credits
    MusicSearchSongWindow = sg.Window("Music Search - Song", layout, background_color='#2B475D', resizable=False, finalize=True, keep_on_top=False, element_justification='c')
    MusicSearchSongWindow.hide()
    MusicSearchSongWindow.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - MusicSearchSongWindow.size[0] // 2, HomeWindow.TKroot.winfo_y() + HomeWindow.TKroot.winfo_height() // 2 - MusicSearchSongWindow.size[1] // 2)
    MusicSearchSongWindow.un_hide()
    ## Lyrics Right Click Menu
    if lyrics != None: lyricsLine:sg.Multiline = MusicSearchSongWindow['MusicSearchSongWindowLyrics']
    ## Window Shortcuts
    MusicSearchSongWindow.bind('<PageUp>', '_PageUp')      ## List Result shortcut
    MusicSearchSongWindow.bind('<PageDown>', '_PageDown')  ## Download Metadata shortcut
    MusicSearchSongWindow.bind('<Delete>', '_Delete')      ## Close Window shortcut
    MusicSearchSongWindow.bind('<Home>', '_Home')          ## Genius Lyrics shortcut
    MusicSearchSongWindow.bind('<End>', '_End')            ## Artist shortcut
    ## Mouse Icon Changes
    for key in ['downloadMetadataMp3Button', 'musicSearchArtistButton', 'musicSearchArtistResultsMenu', 'musicSearchListenButton', 'searchmusicSearchGenius']: MusicSearchSongWindow[key].Widget.config(cursor="hand2") ## Hover icons
    if hitsFound > 1: MusicSearchSongWindow["musicSearchResultsMenu"].Widget.config(cursor="hand2")                                     ## List Search Results Hover icon
    if geniusMusicSearchSongNameInfo != None: MusicSearchSongWindow["geniusMusicSearchSongNameInfoText"].Widget.config(cursor="hand2")  ## Song Name Text Hover icon
    if geniusMusicSearchAlbum != None: MusicSearchSongWindow["geniusMusicSearchAlbumText"].Widget.config(cursor="hand2")                ## Song Album Text Hover icon
    if geniusMusicSearchArtists != None: MusicSearchSongWindow["geniusMusicSearchArtistsText"].Widget.config(cursor="hand2")            ## Song Artist Text Hover icon
    if geniusMusicSearchGenre != None: MusicSearchSongWindow["geniusMusicSearchGenreText"].Widget.config(cursor="hand2")                ## Song Genre Text Hover icon
    if geniusMusicSearchLabels != None: MusicSearchSongWindow["geniusMusicSearchLabels"].Widget.config(cursor="hand2")                  ## Song Label Hover icon
    ## Print Lyrics and Check for Profanity
    if lyrics != None: musicSearchPrintSongLyrics()
    while True:
        event, values = MusicSearchSongWindow.read()
        if event == sg.WIN_CLOSED or (event == '_Delete'): ## Window Closed
            MusicSearchSongWindow.close()
            HomeWindow.Element('musicSearchPanel_songSearchInput').Update("")
            break
        elif event == 'geniusMusicSearchSongNameInfoText': ## Click Song Title
            MusicSearchSongWindow.TKroot.clipboard_clear()
            MusicSearchSongWindow.TKroot.clipboard_append(geniusMusicSearchSongNameInfo)
        elif event == 'geniusMusicSearchAlbumText': ## Click Album Title
            MusicSearchSongWindow.TKroot.clipboard_clear()
            MusicSearchSongWindow.TKroot.clipboard_append(geniusMusicSearchAlbum)
        elif event == 'geniusMusicSearchArtistsText': ## Click Artist Name
            MusicSearchSongWindow.TKroot.clipboard_clear()
            MusicSearchSongWindow.TKroot.clipboard_append(geniusMusicSearchArtists)
        elif event == 'geniusMusicSearchGenreText': ## Click Song Genre
            MusicSearchSongWindow.TKroot.clipboard_clear()
            MusicSearchSongWindow.TKroot.clipboard_append(' '.join(word.capitalize() for word in (geniusMusicSearchGenre.lower()).split()))
        elif event == 'geniusMusicSearchLabels': ## Click Song Labels
            for label in geniusMusicSearchLabels: webbrowser.open("https://en.wikipedia.org/wiki/" + label.replace("[", "").replace("]", "").replace('"', "").replace("'", "").replace(" ", "_"), new=2, autoraise=True)
        elif event in lyricsRightClickMenu[1]: ## Right Click Menu Actions
            try:
                if event == 'Copy': ## Copy Lyrics Text
                    try:
                        MusicSearchSongWindow.TKroot.clipboard_clear()
                        MusicSearchSongWindow.TKroot.clipboard_append(lyricsLine.Widget.selection_get())
                    except: pass
                elif event == 'Lookup Definition': webbrowser.open("https://www.dictionary.com/browse/" + (lyricsLine.Widget.selection_get().split(" ")[0]).replace(",", "").replace(".", "").replace("?", "").replace("!", "").replace(" ", "-"), new=2, autoraise=True)
                elif event == 'Add to Profanity Engine': ## Add Text to Profanity Engine
                    try:
                        pathlib.Path(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Profanity Engine").mkdir(parents=True, exist_ok=True) ## Create Profanity Engine Cache Folder
                        try: additionProfanityEngineInfo = pickle.load(open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Profanity Engine\\Additions.p", "rb")) ## Load Additions Cache
                        except: additionProfanityEngineInfo = []
                        try: removalsProfanityEngineInfo = pickle.load(open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Profanity Engine\\Removals.p", "rb")) ## Load Removals Cache
                        except: removalsProfanityEngineInfo = []
                        additionProfanityEngineInfo.append(lyricsLine.Widget.selection_get().lower())
                        pickle.dump(additionProfanityEngineInfo, open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Profanity Engine\\Additions.p", "wb"))
                        try: ## Remove from the Removals Cache List
                            removalsProfanityEngineInfo.remove(lyricsLine.Widget.selection_get().lower())
                            pickle.dump(removalsProfanityEngineInfo, open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Profanity Engine\\Removals.p", "wb"))
                        except: pass
                        musicSearchPrintSongLyrics() ## Reload Music Search's Lyrics
                    except:
                        popupMessage("Profanity Engine", 'Failed to add "' + lyricsLine.Widget.selection_get() + '" to Profanity Engine.', "error", 3000) ## Show Error Message
                elif event == 'Remove from Profanity Engine': ## Remove Text from Profanity Engine
                    try:
                        profanityEngineMatches, selectedText = "", lyricsLine.Widget.selection_get()
                        pathlib.Path(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Profanity Engine").mkdir(parents=True, exist_ok=True) ## Create Profanity Engine Cache Folder
                        try: removalsProfanityEngineInfo = pickle.load(open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Profanity Engine\\Removals.p", "rb")) ## Load Removals Cache
                        except: removalsProfanityEngineInfo = []
                        try: additionProfanityEngineInfo = pickle.load(open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Profanity Engine\\Additions.p", "rb")) ## Load Additions Cache
                        except: additionProfanityEngineInfo = []
                        loadProfanityEngineDefinitions(True)
                        try:
                            profanityEngineDefinitions.remove(selectedText.strip().replace("'", "~").lower().replace(",", "").replace(".", "").replace("?", "").replace("!", ""))
                            profanityEngineMatches = selectedText.replace("'", "~")
                        except: pass
                        if len(profanityEngineMatches) > 0:
                            removalsProfanityEngineInfo.append(profanityEngineMatches.lower())
                            pickle.dump(removalsProfanityEngineInfo, open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Profanity Engine\\Removals.p", "wb"))
                            try: ## Remove from the Additions Cache List
                                additionProfanityEngineInfo.remove(profanityEngineMatches.lower())
                                pickle.dump(additionProfanityEngineInfo, open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Profanity Engine\\Additions.p", "wb"))
                            except: pass
                            musicSearchPrintSongLyrics() ## Reload Music Search's Lyrics
                            popupMessage("Profanity Engine", '"' + str(profanityEngineMatches).replace("[", "").replace("]", "").replace("'", "").replace('"', "").replace("~", "'") + '" was successfully removed from Profanity Engine.', "saved", 3000) ## Show Success Message
                        else: popupMessage("Profanity Engine", "No words needed to be removed from Profanity Engine.", "success", 3000)
                    except: popupMessage("Profanity Engine", 'Failed to remove "' + selectedText + '" from Profanity Engine.', "error", 3000) ## Show Error Message
            except: pass
        elif event == 'musicSearchResultsMenu' or (event == '_PageUp'): ## Move Song to List Results
            MusicSearchSongWindow.close()
            if "/songs/" in userInput: geniusMusicSearchList(geniusMusicSearchSongNameInfo + " - " + geniusMusicSearchArtists)
            else: geniusMusicSearchList(userInput)
            break
        elif event == 'musicSearchArtistResultsMenu': ## Move Artist to List Results
            MusicSearchSongWindow.close()
            geniusMusicSearchList(geniusMusicSearchPrimeArtist)
            break
        elif event == 'downloadMetadataMp3Button' or (event == '_PageDown'):
            metadataBurnLyricsOnlyValue, metadataChangeFileNameValue, metadataMultipleArtistsValue = False, True, False ## Reset Variables
            musicSearchMetadataWindow = sg.Window("Music Search - Metadata Burner", [[sg.Text("Metadata Burner", font=('Helvetica', 20), background_color='#646f75')], [sg.HorizontalSeparator()], [sg.Text("Choose .MP3 Audio File: ", font=("Helvetica", 14), background_color='#646f75')], [sg.Input("", do_not_clear=True, size=(38,1), enable_events=True, key='metadataBurnerFileChooserInput'), sg.FileBrowse(file_types=(("Audio Files", "*.mp3"),), key='metadataBurnerFileChooser')], [sg.HorizontalSeparator()], [sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png', border_width=0, button_color='#646f75', key='metadataBurnLyricsOnlyCheckbox', tooltip="Burn lyrics only - No"), sg.Text("Burn Lyrics Only", font=('Helvetica', 11), background_color='#646f75', key='metadataBurnLyricsOnlyText')], [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png', border_width=0, button_color='#646f75', key='metadataMultipleArtistsCheckbox', tooltip="Multiple artists - No"), sg.Text("Album Includes Multiple Artists?", font=('Helvetica', 11), background_color='#646f75', key='metadataMultipleArtistsText')], [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png', border_width=0, button_color='#646f75', key='metadataChangeFileNameCheckbox', tooltip="Change file name - Yes"), sg.Text("Change Audio File's Name", font=('Helvetica', 11), background_color='#646f75', key='metadataChangeFileNameText')]], element_justification='l', background_color='#646f75')], [sg.HorizontalSeparator()], [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\start.png', border_width=0,button_color='#646f75', key='burnMetadataInfo'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\cancel.png', border_width=0, button_color='#646f75', key='closeMetadataWindow')]], background_color='#646f75', no_titlebar=True, resizable=False, finalize=True, keep_on_top=True, element_justification='c')
            for key in ['metadataBurnerFileChooser', 'metadataBurnLyricsOnlyCheckbox', 'metadataMultipleArtistsCheckbox', 'metadataChangeFileNameCheckbox', 'burnMetadataInfo', 'closeMetadataWindow']: musicSearchMetadataWindow[key].Widget.config(cursor="hand2") ## Hover icons
            musicSearchMetadataWindow.bind('<Delete>', '_Delete')  ## Close Window shortcut
            while True:
                event, values = musicSearchMetadataWindow.read()
                if event == sg.WIN_CLOSED or event == 'closeMetadataWindow' or (event == '_Delete'): ## Close Settings Window
                    musicSearchMetadataWindow.close()
                    break
                elif event == 'metadataBurnLyricsOnlyCheckbox' and metadataBurnLyricsOnlyValue == True: ## Set Burn Lyrics Only to False
                    musicSearchMetadataWindow['metadataBurnLyricsOnlyCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\false.png')
                    musicSearchMetadataWindow['metadataBurnLyricsOnlyCheckbox'].set_tooltip("Burn lyrics only - No")
                    metadataBurnLyricsOnlyValue = False
                elif event == 'metadataBurnLyricsOnlyCheckbox' and metadataBurnLyricsOnlyValue == False: ## Set Burn Lyrics Only to True
                    musicSearchMetadataWindow['metadataBurnLyricsOnlyCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\true.png')
                    musicSearchMetadataWindow['metadataBurnLyricsOnlyCheckbox'].set_tooltip("Burn lyrics only - Yes")
                    metadataBurnLyricsOnlyValue = True
                elif event == 'metadataMultipleArtistsCheckbox' and metadataMultipleArtistsValue == True: ## Set Multiple Artists to False
                    musicSearchMetadataWindow['metadataMultipleArtistsCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\false.png')
                    musicSearchMetadataWindow['metadataMultipleArtistsCheckbox'].set_tooltip("Multiple artists - No")
                    metadataMultipleArtistsValue = False
                elif event == 'metadataMultipleArtistsCheckbox' and metadataMultipleArtistsValue == False: ## Set Multiple Artists to True
                    musicSearchMetadataWindow['metadataMultipleArtistsCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\true.png')
                    musicSearchMetadataWindow['metadataMultipleArtistsCheckbox'].set_tooltip("Multiple artists - Yes")
                    metadataMultipleArtistsValue = True
                elif event == 'metadataChangeFileNameCheckbox' and metadataChangeFileNameValue == True: ## Set Change File Name to False
                    musicSearchMetadataWindow['metadataChangeFileNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\false.png')
                    musicSearchMetadataWindow['metadataChangeFileNameCheckbox'].set_tooltip("Change file name - No")
                    metadataChangeFileNameValue = False
                elif event == 'metadataChangeFileNameCheckbox' and metadataChangeFileNameValue == False: ## Set Change File Name to True
                    musicSearchMetadataWindow['metadataChangeFileNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\true.png')
                    musicSearchMetadataWindow['metadataChangeFileNameCheckbox'].set_tooltip("Change file name - Yes")
                    metadataChangeFileNameValue = True
                elif event == 'burnMetadataInfo':
                    musicSearchMetadataWindow.close()
                    if metadataChangeFileNameValue: burnAudioData(values['metadataBurnerFileChooserInput'], metadataBurnLyricsOnlyValue, metadataMultipleArtistsValue, extendedSongInfo[0]) ## Download Metadata to MP3 (File Name Change)
                    else: burnAudioData(values['metadataBurnerFileChooserInput'], metadataBurnLyricsOnlyValue, metadataMultipleArtistsValue, extendedSongInfo[0]) ## Download Metadata to MP3
                    break
        elif event == 'musicSearchArtistButton' or (event == '_Home'): webbrowser.open(geniusMusicSearchArtistURL, new=2, autoraise=True)  ## Open Artist's Genius Page
        elif event == 'searchmusicSearchGenius' or (event == '_End'): webbrowser.open(geniusMusicSearchGeniusURL, new=2, autoraise=True) ## Open Genius Page
        elif event == 'musicSearchListenButton': ## Play Song Online
            if musicSub == "Apple": webbrowser.open("https://music.apple.com/us/search?term=" + geniusMusicSearchPrimeArtist.replace(" ", "%20") + "%20" + geniusMusicSearchSongName.replace(" ", "%20"), new=2, autoraise=True)
            elif musicSub == "Spotify": webbrowser.open("https://open.spotify.com/search/" + geniusMusicSearchPrimeArtist.replace(" ", "%20") + "%20" + geniusMusicSearchSongName.replace(" ", "%20"), new=2, autoraise=True)

def musicSearchPrintSongLyrics(lyricsLocation="musicSearch"):
    global badWordCount, lyrics, lyricsListFinal, profanityEngineDefinitions
    if lyricsLocation == "musicSearch": lyricsBox, lyricsText = MusicSearchSongWindow['MusicSearchSongWindowLyrics'], MusicSearchSongWindow['songUsableText']
    elif lyricsLocation == "lyricsCheck": lyricsBox, lyricsText = HomeWindow['lyricsCheckerPanel_lyricsInput'], HomeWindow['lyricsCheckerPanel_songUsableText']
    try:
        lyricsBox.update("", autoscroll=False)
        loadProfanityEngineDefinitions(True)
        ## Load Profanity Engine Dictionary
        for word in range(len(profanityEngineDefinitions)): profanityEngineDefinitions[word] = profanityEngineDefinitions[word].lower().replace("\n", "")
        ## Print Each Lyric Line and Check for Profanity
        for i in range(len(lyricsListFinal)):
            badLine = False ## Reset Bad Line for each Line
            for phrase in profanityEngineDefinitions:
                searchPhaseWithTop = re.search(r"\b{}\b".format(phrase.replace("~", "")), lyricsListFinal[i].replace(",", ""), re.IGNORECASE)
                searchPhaseWithoutTop = re.search(r"\b{}\b".format(phrase.replace("~", "'")), lyricsListFinal[i].replace(",", ""), re.IGNORECASE)
                if badLine == False and phrase[len(phrase)-1] == "~" and searchPhaseWithTop is not None: ## Check Words and Phrases for Bad Words, Ending with '
                    lyricsBox.update(lyricsListFinal[i].split(searchPhaseWithTop.group())[0], autoscroll=False, append=True)
                    lyricsBox.update(searchPhaseWithTop.group(), autoscroll=False, text_color_for_value='Red', append=True)
                    try: lyricsBox.update(lyricsListFinal[i].split(searchPhaseWithTop.group())[1], autoscroll=False, append=True)
                    except: pass
                    lyricsBox.update("\n", autoscroll=False, append=True)
                    badWordCount += 1
                    badLine = True
                elif badLine == False and phrase[len(phrase)-1] != "~" and searchPhaseWithoutTop is not None: ## Check Words and Phrases for Bad Words
                    lyricsBox.update(lyricsListFinal[i].split(searchPhaseWithoutTop.group())[0], autoscroll=False, append=True)
                    lyricsBox.update(searchPhaseWithoutTop.group(), autoscroll=False, text_color_for_value='Red', append=True)
                    try: lyricsBox.update(lyricsListFinal[i].split(searchPhaseWithoutTop.group())[1], autoscroll=False, append=True)
                    except: pass
                    lyricsBox.update("\n", autoscroll=False, append=True)
                    badWordCount += 1
                    badLine = True
            if badLine == False: lyricsBox.print(lyricsListFinal[i], autoscroll=False) ## Clean Line
    except: ## Profanity Engine Dictionary Failed to Load
        profanityEngineDefinitions = "Failed"
        lyricsBox.update("", autoscroll=False)
        for i in range(len(lyricsListFinal)): lyricsBox.print(lyricsListFinal[i], autoscroll=False)
    ## Update Profanity Engine Text
    if lyrics != None and profanityEngineDefinitions != "Failed":
        lyricsText.update("Profanity Engine: Lyrics are " + str(round((1 - (badWordCount/len(lyricsListFinal))) * 100)) + "% clean.")
        if round((1 - (badWordCount/len(lyricsListFinal))) * 100) == 100: lyricsText.update(text_color='#00C957')
        elif round((1 - (badWordCount/len(lyricsListFinal))) * 100) >= 95: lyricsText.update(text_color='#FFD700')
        elif round((1 - (badWordCount/len(lyricsListFinal))) * 100) >= 90: lyricsText.update(text_color='#FF6103')
        elif round((1 - (badWordCount/len(lyricsListFinal))) * 100) < 90: lyricsText.update(text_color='#DC143C')
    elif lyrics != None and profanityEngineDefinitions == "Failed": lyricsText.update("Profanity Engine failed to load.", font='Any 13 bold')

def burnAudioData(audioSavedPath, burnLyricsOnly, multipleArtists, renameFile):
    import eyed3
    try:
        audiofile, lyricsText = eyed3.load(audioSavedPath), "" ## Load MP3
        audiofile.initTag(version=(2, 3, 0)) ## Version is Important
        for i in range(len(lyricsListFinal)): ## Get Lyrics
            if len(lyricsListFinal[i]) == 0: lyricsText += "\n"
            else: lyricsText += lyricsListFinal[i] + "\n"
        if lyrics != None: audiofile.tag.lyrics.set(lyricsText) ## Save Lyrics
        if burnLyricsOnly:
            audiofile.tag.comments.set(u"Metadata: Oszust Industries") ## Comment
            audiofile.tag.save() ## Save File
            popupMessage("Metadata Burner", "Metadata has been saved to " + renameFile + ".", "saved", 3000) ## Show Success Message
            return
        audiofile.tag.artist = extendedSongInfo[1] ## Artist
        if multipleArtists: audiofile.tag.album_artist = "Various Artists" ## Album's Artists (Various Artists)
        else: audiofile.tag.album_artist = geniusMusicSearchPrimeArtist ## Album's Artists
        audiofile.tag.title = extendedSongInfo[0] ## Title
        if geniusMusicSearchDate != None and geniusMusicSearchDate != "Unknown Release Date": audiofile.tag.recording_date = geniusMusicSearchDate[-4:] ## Year
        audiofile.tag.genre = geniusMusicSearchGenre ## Genre
        audiofile.tag.album = extendedSongInfo[2] ## Album
        if geniusMusicSearchLabels != None: audiofile.tag.publisher = geniusMusicSearchLabels[0].replace("[", "").replace("]", "").replace("'", "") ## Label
        if geniusMusicSearchAlbumCurrent != None: audiofile.tag.track_num = geniusMusicSearchAlbumCurrent ## Curent Song Position
        if geniusMusicSearchAlbumLength != None: audiofile.tag.track_total = geniusMusicSearchAlbumLength ## Album length
        for artworkType in [4, 3, 0]: audiofile.tag.images.set(artworkType, png_data, "image/png") ## Artwork - Basic
        for artworkType in [4, 3, 0]: audiofile.tag.images.set(artworkType, png_data, "image/jpeg", "cover") ## Artwork - Higher Quality
        audiofile.tag.comments.set(u"Metadata: Oszust Industries") ## Comment
        audiofile.tag.save() ## Save File
        ## Change the audio file's name
        if renameFile != False:
            try: os.rename(audioSavedPath, audioSavedPath.replace(audioSavedPath.rsplit('/', 1)[1], "") + "\\" + renameFile + ".mp3") ## Raname MP3 to Song Name
            except: pass
        popupMessage("Metadata Burner", "Metadata has been saved to " + renameFile + ".", "saved", 3000) ## Show Success Message
    except: popupMessage("Metadata Burner", "The burner failed.", "error")

def loadGeniusMusicList(userInput):
    from PIL import Image
    import cloudscraper, io
    global geniusSongIDs, geniusURLs, layout, loadingAction, resultNumbers, songArtists, songNames
    artistSearch, geniusSongIDs, geniusURLs, layout, resultNumber, resultNumbers, songArtists, songNames = False, [], [], [[sg.Push(background_color='#657076'), sg.Text('Music Search Results:', font='Any 20', background_color='#657076'), sg.Push(background_color='#657076')], [sg.Push(background_color='#657076'), sg.Input(userInput.replace("-", " "), do_not_clear=True, size=(40,1), enable_events=True, key='geniusMusicListSearchInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\search.png', border_width=0, button_color='#657076', key='geniusMusicListSearchButton', tooltip="Search"), sg.Push(background_color='#657076')]], 0, [], [], []
    if "genius.com" in userInput: userInput = userInput.split("https://genius.com/",1)[1].split("-lyrics",1)[0] ## Genius Website URL
    request = urllib.request.Request("http://api.genius.com/search?q=" + urllib.request.quote(userInput.lower().replace(" by ", "-")) + "&page=1")
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
    musicSearchApiBody = json.loads(raw)["response"]["hits"]
    hitsFound = len(musicSearchApiBody)
    if hitsFound == 0: ## Check if Result Found
        loadingAction = "No_Result_Found"
        return
    if hitsFound > 8: hitsFound = 8 ## Set Max to 8 if More Than 8 Results Returned
    while hitsFound > 0 and resultNumber < 10:
        geniusMusicSearchArtists = str(musicSearchApiBody[resultNumber]["result"]["artist_names"]).replace("(Rock)", "") ## Song Artists
        songArtists.append(geniusMusicSearchArtists) ## Add Artists to List 
        geniusMusicSearchPrimeArtist = str(musicSearchApiBody[resultNumber]["result"]["primary_artist"]["name"]).split('(')[0] ## Song Main Artist
        if str(musicSearchApiBody[0]["result"]["artist_names"]).replace(" ", "-").lower() == userInput: artistSearch = True ## Find if Search is an Artist
        geniusMusicSearchDate = str(musicSearchApiBody[resultNumber]["result"]["release_date_for_display"]) ## Result Release Date
        if geniusMusicSearchDate == "None": geniusMusicSearchDate = None ## Fix Release Date if None Found
        geniusMusicSearchSongNameInfo = str(musicSearchApiBody[resultNumber]["result"]["title_with_featured"]) ## Result Full Title
        songNames.append(geniusMusicSearchSongNameInfo) ## Add Song Full Title to List
        geniusMusicSearchGeniusURL = str(musicSearchApiBody[resultNumber]["result"]["url"]) ## Result Genius URL
        geniusURLs.append(geniusMusicSearchGeniusURL) ## Add Genius URL to List
        geniusMusicSearchGeniusSongID = str(musicSearchApiBody[resultNumber]["result"]["api_path"]) ## Song ID
        geniusSongIDs.append(geniusMusicSearchGeniusSongID) ## Add Song ID to List
        ## Shorten Results
        longSongNameInfo = geniusMusicSearchSongNameInfo
        longArtists = geniusMusicSearchArtists
        if len(geniusMusicSearchSongNameInfo) > 30: geniusMusicSearchSongNameInfo = geniusMusicSearchSongNameInfo[:29] + "..." ## Shorten Song Name
        if len(geniusMusicSearchArtists) > 30: geniusMusicSearchArtists = geniusMusicSearchArtists[:29] + "..." ## Shorten Artists Names
        ## Song Artwork
        try:
            geniusMusicSearchArtworkURL = str(musicSearchApiBody[resultNumber]["result"]["song_art_image_url"])
            if "https://assets.genius.com/images/default_cover_image.png" in geniusMusicSearchArtworkURL: png_data = str(pathlib.Path(__file__).resolve().parent) + "\\data\\defaultMusicArtwork.png"
            else:
                try: ## Look in Cache for Artwork
                    pil_image = Image.open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Music Search\\" + str(musicSearchApiBody[resultNumber]["result"]["song_art_image_url"]).split(".com/",1)[1].split(".",1)[0] + "-small.png") ## Open Artwork from Cache
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
                        pathlib.Path(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Music Search").mkdir(parents=True, exist_ok=True) ## Create Music Search Cache Folder
                        png_data = pil_image.save(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Music Search\\" + str(musicSearchApiBody[resultNumber]["result"]["song_art_image_url"]).split(".com/",1)[1].split(".",1)[0] + "-small.png")
                    except: pass
                    png_data = png_bio.getvalue()
        except: png_data = str(pathlib.Path(__file__).resolve().parent) + "\\data\\defaultMusicArtwork.png" ## Default Artwork if Retrieval Fails
        ## Song Lyrics
        geniusMusicSearchLyricsState = str(musicSearchApiBody[resultNumber]["result"]["lyrics_state"]) ## Result Song Lyrics
        if geniusMusicSearchLyricsState.lower() == "complete": lyricsImage, lyricsHoverMessage = "checked", "Lyrics Found" ## Lyrics Found
        else: lyricsImage, lyricsHoverMessage = "checkFailed", "Lyrics Not Found" ## No Lyrics Found
        ## Music Service
        if musicSub == "Apple": musicServiceImage = "musicSearchListenApple" ## Set Listening Link to Apple
        elif musicSub == "Spotify": musicServiceImage = "musicSearchListenSpotify" ## Set Listening Link to Spotify
        ## Song Window
        if (artistSearch == False or (artistSearch == True and geniusMusicSearchPrimeArtist.replace(" ", "-").split('(')[0].lower() == userInput)) and geniusMusicSearchArtists.lower() not in ["spotify", "genius", "siriusxm the highway"] and "genius" not in geniusMusicSearchArtists.lower():
            if geniusMusicSearchDate != None: layout += [[sg.Column([[sg.Image(png_data), sg.Column([[sg.Text(str(geniusMusicSearchSongNameInfo), font='Any 16', background_color='#2b475d', tooltip=longSongNameInfo)], [sg.Text(str(geniusMusicSearchArtists), font='Any 14', background_color='#2b475d', tooltip=longArtists)], [sg.Text(str(geniusMusicSearchDate), font='Any 12', background_color='#2b475d')]], background_color='#2b475d'), sg.Push(background_color='#2b475d'), sg.Column([[sg.Image(str(pathlib.Path(__file__).resolve().parent)+'\\data\\'+lyricsImage+'.png', background_color='#2b475d', tooltip=lyricsHoverMessage), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchGenius.png', border_width=0, button_color='#2b475d', key='searchmusicListSearchGenius_' + str(resultNumber), tooltip="Open Genius Page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\'+musicServiceImage+'.png', border_width=0, button_color='#2b475d', key='searchmusicListPlaySong_' + str(resultNumber), tooltip="Play Song"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\openView.png', border_width=0, button_color='#2b475d', key='searchMusicListOpenSong_' + str(resultNumber), tooltip="Open Result")]], background_color='#2b475d')]], background_color='#2b475d', expand_x=True)]]
            else: layout += [[sg.Column([[sg.Image(png_data), sg.Column([[sg.Text(str(geniusMusicSearchSongNameInfo), font='Any 16', background_color='#2b475d', tooltip=longSongNameInfo)], [sg.Text(str(geniusMusicSearchArtists), font='Any 14', background_color='#2b475d', tooltip=longArtists)]], background_color='#2b475d'), sg.Push(background_color='#2b475d'), sg.Column([[sg.Image(str(pathlib.Path(__file__).resolve().parent)+'\\data\\'+lyricsImage+'.png', background_color='#2b475d', tooltip=lyricsHoverMessage), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchGenius.png', border_width=0, button_color='#2b475d', key='searchmusicListSearchGenius_' + str(resultNumber), tooltip="Open Genius Page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\'+musicServiceImage+'.png', border_width=0, button_color='#2b475d', key='searchmusicListPlaySong_' + str(resultNumber), tooltip="Play Song"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\openView.png', border_width=0, button_color='#2b475d', key='searchMusicListOpenSong_' + str(resultNumber), tooltip="Open Result")]], background_color='#2b475d')]], background_color='#2b475d', expand_x=True)]]
            resultNumbers.append(resultNumber)
        resultNumber += 1
        hitsFound -= 1
    layout += [[sg.Push(background_color='#657076'), sg.Text("Music Search powered by Genius", background_color='#657076', font='Any 11'), sg.Push(background_color='#657076')]] ## Credits
    ## Check if Any Good Results Found
    if len(resultNumbers) == 0: loadingAction = "No_Result_Found"
    elif len(resultNumbers) == 1: loadingAction = "Only_One_Result"
    else: loadingAction = "Search_Finished"

def geniusMusicSearchList(userInput):
    global geniusSongIDs, geniusURLs, layout, loadingAction, resultNumbers, songArtists, songNames
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
        elif loadingAction == "No_Result_Found": ## No Music Search Result Found
            loadingPopup.close() ## Close Loading Popup
            popupMessage("No Search Result", "", "fail")
            return
        elif "Genius_Page_Down:" in loadingAction: ## Genius's Service is Down (Special Error)
            loadingPopup.close() ## Close Loading Popup
            popupMessage("Music Search Error", loadingAction.split("Genius_Page_Down:",1)[1] + "\t\t\t\t\tPlease try again a little later.", "error")
            return
        elif loadingAction == "Genius_Page_Down": ## Genius's Service is Down
            loadingPopup.close() ## Close Loading Popup
            popupMessage("Music Search Error", "Genius is down.\t\t\t\t\tPlease try again a little later.", "error")
            return
        elif loadingAction == "Genius_Robot_Check": ## Genius is Checking Robot
            loadingPopup.close() ## Close Loading Popup
            popupMessage("Music Search Error", "Genius thinks you're a robot.\t\t\t\t\tPlease disable your VPN.", "error")
            return
        elif loadingAction == "Only_One_Result": ## Only One Result Found, Open It
            loadingPopup.close()
            geniusMusicSearch(geniusSongIDs[0], True)
            return
        elif loadingAction == "Search_Finished": ## Show Music Search List Window
            loadingPopup.close()
            break
    MusicSearchListWindow = sg.Window("Music Search - List Results", layout, background_color='#657076', finalize=True, resizable=False, keep_on_top=False, element_justification='l')
    MusicSearchListWindow.hide()
    MusicSearchListWindow.move(HomeWindow.TKroot.winfo_x() + HomeWindow.TKroot.winfo_width() // 2 - MusicSearchListWindow.size[0] // 2, HomeWindow.TKroot.winfo_y() + HomeWindow.TKroot.winfo_height() // 2 - MusicSearchListWindow.size[1] // 2)
    MusicSearchListWindow.un_hide()
    ## Window Shortcuts
    MusicSearchListWindow.bind('<Delete>', '_Delete')                               ## Close Window shortcut
    MusicSearchListWindow['geniusMusicListSearchInput'].bind('<Return>', '_Enter')  ## Enter on Song Search
    ## Mouse Icon Changes
    MusicSearchListWindow["geniusMusicListSearchButton"].Widget.config(cursor="hand2")  ## Change Search Button Hover icon
    for resultNumber in resultNumbers:
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
            geniusMusicSearchList(values['geniusMusicListSearchInput'].lower().replace(" by ", "-").replace(" ","-"))
            break
        elif 'searchmusicListSearchGenius' in event: webbrowser.open(geniusURLs[int(event.split("_")[-1])], new=2, autoraise=True) ## Open Genius Page
        elif 'searchmusicListPlaySong_' in event: ## Play Song Online
            if musicSub == "Apple": webbrowser.open("https://music.apple.com/us/search?term=" + songArtists[int(event.split("_")[-1])].replace(" ", "%20") + "%20" + songNames[int(event.split("_")[-1])].replace(" ", "%20"), new=2, autoraise=True)
            elif musicSub == "Spotify": webbrowser.open("https://open.spotify.com/search/" + songArtists[int(event.split("_")[-1])].replace(" ", "%20") + "%20" + songNames[int(event.split("_")[-1])].replace(" ", "%20"), new=2, autoraise=True)
        elif 'searchMusicListOpenSong' in event: ## Open Song in Music Search
            HomeWindow.Element('musicSearchPanel_songSearchInput').Update(songNames[int(event.split("_")[-1])] + " - " + songArtists[int(event.split("_")[-1])])
            MusicSearchListWindow.close()
            geniusMusicSearch(geniusSongIDs[int(event.split("_")[-1])], True)
            break


## Start System
try:softwareSetup()
except Exception as Argument: crashMessage("Error 00: " + str(Argument))