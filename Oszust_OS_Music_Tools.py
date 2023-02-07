## Oszust OS Music Tools - Oszust Industries
## Created on: 1-02-23 - Last update: 2-06-23
softwareVersion = "v1.0.0.000 (02.06.23)"
import ctypes, datetime, eyed3, json, os, pathlib, platform, psutil, re, requests, threading, urllib.request, webbrowser, win32clipboard, pickle, textwrap
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
    global profanityEngineDefinitions, topSongsList, screenWidth, screenHeight
    ## Setup Software
    print("Loading...\nLaunching Interface...")
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
    except:
        failedSetupWindow = sg.Window("NO WIFI", [[sg.Text("There doesn't seem to be any internet connection on your device.\n" + systemName + " requires an internet connection.", justification='c', font='Any 16')], [sg.Button("Retry Connection", button_color=("White", "Blue"), key='RetryWIFI'), sg.Button("Quit App", button_color=("White", "Red"), key='Quit')]], resizable=False, finalize=True, keep_on_top=True, element_justification='c')
        while True:
            event, values = failedSetupWindow.read()
            if event == sg.WIN_CLOSED or event == 'Quit': exit()
            elif event in ['RetryWIFI']: ## Retry Internet Test
                failedSetupWindow.close()
                softwareSetup()
    ## Billboard Top 100 Hits from Cache
    try:
        billboardCache, topSongsList = (open(str(pathlib.Path(__file__).resolve().parent)+'\\cache\\Billboard.txt', "r")).read().split("\n"), []
        if datetime.datetime.strptime(billboardCache[0], '%Y-%m-%d') + datetime.timedelta(days=7) >= datetime.datetime.now(): ## Check if Cache is >= Week
            for item in billboardCache[1:]: topSongsList.append(item) ## Set List from Cache
        else: loadingScreen("Billboard_List_Download", agr1=False, arg2=False, arg3=False, arg4=False, arg5=False) ## Download Billboard Data
    except: loadingScreen("Billboard_List_Download", agr1=False, arg2=False, arg3=False, arg4=False, arg5=False) ## Download Billboard Data
    ## Retrieve Profanity Engine Definitions
    profanityEngineDefinitions = json.loads(urllib.request.urlopen(f"https://raw.githubusercontent.com/Oszust-Industries/" + systemName.replace(" ", "-") + "/Server/profanityEngineDefinitions.txt").read().decode())
    ## Launch Default Home App
    homeScreen("Music_Search")

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
            pathlib.Path(str(pathlib.Path(__file__).resolve().parent)+'\\cache').mkdir(parents=True, exist_ok=True) ## Create Cache Folder
            with open(str(pathlib.Path(__file__).resolve().parent)+'\\cache\\Billboard.txt', 'w') as billboardTextFile: ## Create Cache File
                lastTuesday = datetime.date.today() - datetime.timedelta(days=(datetime.date.today().weekday() - 1) % 7) ## Data is Fresh on Tuesday
                billboardTextFile.write(str(lastTuesday))
                for item in topSongsList: billboardTextFile.write("\n" + item)
                billboardTextFile.close()
        except: pass
    except: topSongsList.append("Billboard Top 100 Failed to Load")
    loadingStatus = "Done"

def homeScreenAppPanels(appName): ## CLEAN THIS ONE
    if appName == "Music_Search":
        topSongsListBoxed = [[sg.Listbox(topSongsList, size=(80, 15), key='billboardTopSongsList', horizontal_scroll=True, select_mode=None, enable_events=True, highlight_background_color='blue', highlight_text_color='white')]]
        return [[sg.Push(background_color='#2B475D'), sg.Text("Music Search:", font='Any 20', background_color='#2B475D'), sg.Push(background_color='#2B475D')],
        [sg.Text("Search:", font='Any 16', background_color='#2B475D'), sg.Input(do_not_clear=True, size=(50,1), enable_events=True, key='songSearchBox'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\search.png', border_width=0, button_color='#2B475D', key='searchSongSearchButton', tooltip="Search Music"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\listSearch.png', border_width=0, button_color='#2B475D', key='listSongSearchButton', tooltip="Music Search - All Results"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\clearInput.png', border_width=0, button_color='#2B475D', key='clearInputSongSearchButton', tooltip="Clear Search")],
        [sg.Frame("The Billboard Hot 100", topSongsListBoxed, relief="flat", background_color='#2B475D', key='topSongsListFrame'), sg.Push(background_color='#2B475D')]]
    elif appName == "Music_Downloader":
        return [[sg.Push(background_color='#4d4d4d'), sg.Text("Music Downloader:", font='Any 20', background_color='#4d4d4d'), sg.Push(background_color='#4d4d4d')],
        [sg.Text("YouTube Link:", font='Any 13', background_color='#4d4d4d'), sg.Input("", do_not_clear=True, size=(48,1),enable_events=True, key='musicDownloaderYoutubeLink'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\clipboard.png', border_width=0, key='musicDownloaderLinkClipboard', tooltip="Paste Link"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\youtubeDownloader.png', border_width=0, key='musicDownloaderOpenYoutube', tooltip="Open YouTube")],
        [sg.Text("Download Location:", font='Any 13', background_color='#4d4d4d'), sg.Input("", do_not_clear=True, size=(50,1),enable_events=True, key='musicDownloaderLocation'), sg.FolderBrowse()],
        [sg.HorizontalSeparator()], [sg.Push(background_color='#4d4d4d'), sg.Text("Downloader Settings:", font='Any 15', background_color='#4d4d4d'), sg.Push(background_color='#4d4d4d'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\reset.png', border_width=0, key='musicDownloaderResetSettings', tooltip="Paste Link")],
        [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\true.png', border_width=0, key='musicDownloaderAudioDownloadCheckbox', tooltip="Paste Link"), sg.Text("Burn lyrics to the audio file", font='Any 14', background_color='#4d4d4d')],
        [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\false.png', border_width=0, key='musicDownloaderVideoDownloadCheckbox', tooltip="Paste Link"), sg.Text("Song's album is a compilation by various artists", font='Any 14', background_color='#4d4d4d')],
        [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\false.png', border_width=0, key='musicDownloaderDownloadNameCheckbox', tooltip="Paste Link"), sg.Text("Rename download to:", font='Any 14', background_color='#4d4d4d'), sg.Input("", do_not_clear=True, size=(31,1), enable_events=True, visible=False, key='musicDownloaderDownloadNameInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\clipboard_Small.png', border_width=0, visible=False, key='musicDownloaderDownloadNameClipboard', tooltip="Paste Link"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\clearInput.png', border_width=0, visible=False, key='musicDownloaderDownloadNameClear', tooltip="Paste Link")],
        ]#[sg.HorizontalSeparator()], [sg.Text("", font='Any 4', background_color='#4d4d4d')], [sg.Push(background_color='#4d4d4d'), sg.Button("Download", button_color=("White", "Blue"), font='Any 15', size=(10, 1), key='musicDownloaderDownloadButton'), sg.Push(background_color='#4d4d4d')]]
    elif appName == "YouTube_Downloader":
        return [[sg.Push(background_color='#4d4d4d'), sg.Text("YouTube Downloader:", font='Any 20', background_color='#4d4d4d'), sg.Push(background_color='#4d4d4d')],
        [sg.Text("YouTube Link:", font='Any 13', background_color='#4d4d4d'), sg.Input("", do_not_clear=True, size=(48,1),enable_events=True, key='youtubeDownloaderYoutubeLink'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\clipboard.png', border_width=0, key='youtubeDownloaderLinkClipboard', tooltip="Paste Link"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\youtubeDownloader.png', border_width=0, key='youtubeDownloaderOpenYoutube', tooltip="Open YouTube")],
        [sg.Text("Download Location:", font='Any 13', background_color='#4d4d4d'), sg.Input("", do_not_clear=True, size=(50,1),enable_events=True, key='youtubeDownloaderLocation'), sg.FolderBrowse(key='youtubeDownloaderLocationFinder')],
        [sg.HorizontalSeparator()], [sg.Push(background_color='#4d4d4d'), sg.Text("Downloader Settings:", font='Any 15', background_color='#4d4d4d'), sg.Push(background_color='#4d4d4d'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\reset.png', border_width=0, key='youtubeDownloaderResetSettings', tooltip="Paste Link")],
        [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\false.png', border_width=0, key='youtubeDownloaderAudioDownloadCheckbox', tooltip="Paste Link"), sg.Text("Download audio file (.MP3) of the YouTube Video", font='Any 14', background_color='#4d4d4d')],
        [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\true.png', border_width=0, key='youtubeDownloaderVideoDownloadCheckbox', tooltip="Paste Link"), sg.Text("Download video file (.MP4) of the YouTube Video", font='Any 14', background_color='#4d4d4d')],
        [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\false.png', border_width=0, key='youtubeDownloaderDownloadNameCheckbox', tooltip="Paste Link"), sg.Text("Rename download to:", font='Any 14', background_color='#4d4d4d'), sg.Input("", do_not_clear=True, size=(31,1), enable_events=True, visible=False, key='youtubeDownloaderDownloadNameInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\clipboard_Small.png', border_width=0, visible=False, key='youtubeDownloaderDownloadNameClipboard', tooltip="Paste Link"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\clearInput.png', border_width=0, visible=False, key='youtubeDownloaderDownloadNameClear', tooltip="Paste Link")],
        [sg.HorizontalSeparator()], [sg.Text("", font='Any 4', background_color='#4d4d4d')], [sg.Push(background_color='#4d4d4d'), sg.Button("Download", button_color=("White", "Blue"), font='Any 15', size=(10, 1), key='youtubeDownloaderDownloadButton'), sg.Push(background_color='#4d4d4d')]]
    else: return [[sg.Text(appName)]]

def homeScreen(appSelected):
    global HomeWindow
    ## Oszust OS Music Tools List
    applist, apps = [[]], ["Music Search", "Music Downloader", "YouTube Downloader"] ##["Music Search", "Metadata Burner", "Music Downloader", "YouTube Downloader", "CD Burner", "Settings"]
    for app in apps: applist += [[sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent) + "\\data\\" + app.lower().replace(" ", "") + ".png", button_color='#64778D', border_width=0, key=app.replace(" ", "_") + "_AppSelector", tooltip='Open ' + app)]], pad=((5,5), (5, 5)))]] ## Add apps to side panel
    ## Home Window
    appWindow = homeScreenAppPanels(appSelected) ## App Panel Loading Based on App
    layout = [[sg.Column(applist, size=(72,390), pad=((10,10), (10, 10)), background_color='#2B475D', scrollable=False, vertical_scroll_only=True), sg.Column(appWindow, size=(600,390), pad=((10,10), (10, 10)), background_color='#2B475D', scrollable=False, vertical_scroll_only=True)]]
    layout += [[sg.Column([[sg.Text(platform.system() + " | " + softwareVersion + " | " + systemBuild + " | Online", enable_events=True, font='Any 13', key='versionTextHomeBottom'), sg.Push(), sg.Text("Oszust Industries", enable_events=True, font='Any 13', key='creditsTextHomeBottom')], [sg.Column([[]], size=(715, 1), pad=(0,0))]], size=(715, 30), pad=(0,0))]]
    HomeWindow = sg.Window('Oszust OS Music Tools', layout, background_color='#4d4d4d', margins=(0,0), finalize=True, resizable=True, text_justification='r')
    ## Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    if appSelected == "Music_Search":
        HomeWindow['billboardTopSongsList'].bind('<Return>', '_Enter')  ## Enter on Top 100 list
        HomeWindow['songSearchBox'].bind('<Return>', '_Enter')          ## Enter on Song Search
        for key in ['searchSongSearchButton', 'listSongSearchButton', 'clearInputSongSearchButton', 'billboardTopSongsList']: HomeWindow[key].Widget.config(cursor="hand2") ## Hover icons
    elif appSelected == "Music_Downloader":
         ## App Variables
        for key in []: HomeWindow[key].Widget.config(cursor="hand2") ## Hover icons
    elif appSelected == "YouTube_Downloader":
        youtubeAudioDownload, youtubeVideoDownload, youtubeDownloadName, = False, True, False ## App Variables
        for key in ['youtubeDownloaderLinkClipboard', 'youtubeDownloaderOpenYoutube', 'youtubeDownloaderLocationFinder', 'youtubeDownloaderResetSettings', 'youtubeDownloaderAudioDownloadCheckbox', 'youtubeDownloaderVideoDownloadCheckbox', 'youtubeDownloaderDownloadNameCheckbox', 'youtubeDownloaderDownloadNameClipboard', 'youtubeDownloaderDownloadNameClear', 'youtubeDownloaderDownloadButton']: HomeWindow[key].Widget.config(cursor="hand2") ## Hover icons
    ## Main Window: Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    for key in ['versionTextHomeBottom', 'creditsTextHomeBottom']: HomeWindow[key].Widget.config(cursor="hand2") ## Hover icons
    for app in apps: HomeWindow[app.replace(" ", "_") + "_AppSelector"].Widget.config(cursor="hand2") ## App Side Panel hover icons
    ## Reading Home Window
    while True:
        event, values = HomeWindow.read(timeout=10)
## Closed Window
        if event == sg.WIN_CLOSED or event == 'Exit':
            HomeWindow.close()
            thisSystem = psutil.Process(os.getpid()) ## Close Program
            thisSystem.terminate()
## Home Screen Bottom Text
        elif event == 'creditsTextHomeBottom':
            creditsWindow = sg.Window("Credits", [[sg.Text("Music Downloader Credits", font='Any 16')], [sg.Text("Development Started: January 2, 2023")], [sg.HorizontalSeparator()], [sg.Text("Developer Team:", font='Any 12')], [sg.Text("Lead Developer: Simon Oszust")], [sg.HorizontalSeparator()], [sg.Button("Ok", button_color=("White", "Blue"), key='okButton')]], resizable=False, finalize=True, keep_on_top=True, element_justification='c')
            creditsWindow["okButton"].Widget.config(cursor="hand2") ## Hover icon
            creditsWindow.bind('<Delete>', '_Delete')  ## Close Window shortcut
            while True:
                event, values = creditsWindow.read()
                if event == sg.WIN_CLOSED or event == 'okButton' or (event == '_Delete'): ## Window Closed
                    creditsWindow.close()
                    break
        elif event == 'versionTextHomeBottom': webbrowser.open("https://github.com/Oszust-Industries/" + systemName.replace(" ", "-") + "/releases", new=2, autoraise=True)
## App Picker Panel (Buttons)
        elif "_AppSelector" in event and event.replace("_AppSelector", "") != appSelected:
            HomeWindow.close()
            homeScreen(event.replace("_AppSelector", ""))
            break
## Music Search (Buttons/Events)
        elif appSelected == "Music_Search":
            if (event == 'searchSongSearchButton' or (event == 'songSearchBox' + '_Enter')) and values['songSearchBox'].replace(" ","").lower() not in ["", "resultfailedtoload", "billboardtop100failedtoload"]: geniusMusicSearch(values['songSearchBox'].lower().replace(" by ", "-").replace(" ","-"), False) ## Music Search
            elif event == 'listSongSearchButton' and values['songSearchBox'].replace(" ","").lower() not in ["", "resultfailedtoload", "billboardtop100failedtoload"]: geniusMusicSearchList(values['songSearchBox'].lower().replace(" by ", "-").replace(" ","-")) ## Music Search All Results
            elif event == 'clearInputSongSearchButton': HomeWindow.Element('songSearchBox').Update("") ## Clear Music Search Input
            elif event == 'billboardTopSongsList' and values['billboardTopSongsList'][0].split(". ", 1)[1].split("   (", 1)[0].replace(" ","").lower() not in ["", "resultfailedtoload", "billboardtop100failedtoload"]: HomeWindow.Element('songSearchBox').Update(values['billboardTopSongsList'][0].split(". ", 1)[1].split("   (", 1)[0]) ## Copy Top 100 to Music Search
            elif (event == 'billboardTopSongsList' + '_Enter'): geniusMusicSearch(values['billboardTopSongsList'][0].split(". ", 1)[1].split("   (", 1)[0], False) ## Top 100 Song Search
## Music Downloader (Buttons/Events)

## YouTube Downloader (Buttons/Events)
        elif appSelected == "YouTube_Downloader":
            if event == 'youtubeDownloaderLinkClipboard': ## Paste Clipboard in YouTube Link Input
                win32clipboard.OpenClipboard()
                HomeWindow.Element('youtubeDownloaderYoutubeLink').Update(win32clipboard.GetClipboardData())
                win32clipboard.CloseClipboard()
            elif event == 'youtubeDownloaderOpenYoutube': webbrowser.open("youtube.com", new=2, autoraise=True) ## Open YouTube Website
            elif event == 'youtubeDownloaderResetSettings': ## Reset Settings
                youtubeAudioDownload = False
                HomeWindow['youtubeDownloaderAudioDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                HomeWindow['youtubeDownloaderVideoDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png')
                youtubeVideoDownload = True
                HomeWindow['youtubeDownloaderDownloadNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                HomeWindow.Element('youtubeDownloaderDownloadNameInput').Update("")
                for key in ['youtubeDownloaderDownloadNameInput', 'youtubeDownloaderDownloadNameClipboard', 'youtubeDownloaderDownloadNameClear']: HomeWindow.Element(key).Update(visible=False)
                youtubeDownloadName = False
            elif event == 'youtubeDownloaderAudioDownloadCheckbox' and youtubeAudioDownload == True and youtubeVideoDownload == True: ## Download Audio - False
                HomeWindow['youtubeDownloaderAudioDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                youtubeAudioDownload = False
            elif event == 'youtubeDownloaderAudioDownloadCheckbox' and youtubeAudioDownload == False: ## Download Audio - True
                HomeWindow['youtubeDownloaderAudioDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png')
                youtubeAudioDownload = True
            elif event == 'youtubeDownloaderVideoDownloadCheckbox' and youtubeVideoDownload == True and youtubeAudioDownload == True: ## Download Video - False
                HomeWindow['youtubeDownloaderVideoDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                youtubeVideoDownload = False
            elif event == 'youtubeDownloaderVideoDownloadCheckbox' and youtubeVideoDownload == False: ## Download Video - True
                HomeWindow['youtubeDownloaderVideoDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png')
                youtubeVideoDownload = True
            elif event == 'youtubeDownloaderDownloadNameCheckbox' and youtubeDownloadName == True: ## Change File Name - False
                HomeWindow['youtubeDownloaderDownloadNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                for key in ['youtubeDownloaderDownloadNameInput', 'youtubeDownloaderDownloadNameClipboard', 'youtubeDownloaderDownloadNameClear']: HomeWindow.Element(key).Update(visible=False)
                youtubeDownloadName = False
            elif event == 'youtubeDownloaderDownloadNameCheckbox' and youtubeDownloadName == False: ## Change File Name - True
                HomeWindow['youtubeDownloaderDownloadNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png')
                for key in ['youtubeDownloaderDownloadNameInput', 'youtubeDownloaderDownloadNameClipboard', 'youtubeDownloaderDownloadNameClear']: HomeWindow.Element(key).Update(visible=True)
                youtubeDownloadName = True
            elif event == 'youtubeDownloaderDownloadNameClipboard': ## Paste Clipboard in File Name Input
                win32clipboard.OpenClipboard()
                HomeWindow.Element('youtubeDownloaderDownloadNameInput').Update(win32clipboard.GetClipboardData())
                win32clipboard.CloseClipboard()
            elif event == 'youtubeDownloaderDownloadNameClear': HomeWindow.Element('youtubeDownloaderDownloadNameInput').Update("") ## Clear File Name Input
            elif event == 'youtubeDownloaderDownloadButton': ## Download YouTube Button
                if youtubeDownloadName: youtubeDownloadName = values['youtubeDownloaderDownloadNameInput']
                loadingScreen("YouTube_Downloader", values['youtubeDownloaderYoutubeLink'], values['youtubeDownloaderLocation'], youtubeAudioDownload, youtubeVideoDownload, youtubeDownloadName)
                HomeWindow["youtubeDownloaderYoutubeLink"].update("")

def loadingScreen(functionLoader, agr1=False, arg2=False, arg3=False, arg4=False, arg5=False):
    global loadingStatus
    loadingPopup, loadingStatus = sg.Window("", [[sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", background_color='#1b2838', key='loadingGIFImage')], [sg.Text("Loading...", font='Any 16', background_color='#1b2838', key='loadingScreenText')]], background_color='#1b2838', element_justification='c', no_titlebar=True, keep_on_top=True), "Start"
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
        elif loadingStatus == "Done":
            loadingPopup.close()
            break

def downloadYouTube(youtubeLink, downloadLocation, audioFile, videoFile, renameFile):
    global audioSavedPath, loadingStatus, youtubeTitle
    try: YouTube(youtubeLink).streams.filter(file_extension="mp4").get_highest_resolution().download(downloadLocation) ## Download Video
    except:
        loadingStatus = "Failed"
    youtubeTitle = (YouTube(youtubeLink).title).replace("|", "").replace("'", "").replace("/", "").replace("#", "").replace(".", "") ## Downloaded Files Name
    if audioFile: ## Convert MP4 Video to MP3 Audio
        loadingStatus = "Downloading YouTube Audio..."
        audioSavedPath = downloadLocation + "\\" + youtubeTitle + ".mp3" ## MP3 File Name
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
    ## Remove extra characters from YouTube title for Music Search
    youtubeTitle = re.sub("([\(\[]).*?([\)\]])", "\g<1>\g<2>", youtubeTitle)
    loadingStatus = "Done"






def messagePopupTimed(EMMAMessage, title, message, imageFile, clickAction, timeOpen, messageImportant):
    global messagePopupActive 
    if messagePopupActive: messageWindow.close() ## Close Opened Message Window
    if clickAction == None: clickAction = "" ## Fix clickAction Format
    wrapper = textwrap.TextWrapper(width=43, max_lines=4, placeholder='...')
    ## Change Height of Window on Message Size
    if len(wrapper.wrap(message)) == 1: messageHeight, screenHeightSub = 135, 165
    elif len(wrapper.wrap(message)) == 2: messageHeight, screenHeightSub = 165, 195
    elif len(wrapper.wrap(message)) == 3: messageHeight, screenHeightSub = 185, 215
    elif len(wrapper.wrap(message)) == 4: messageHeight, screenHeightSub = 210, 240
    message = '\n'.join(wrapper.wrap(message)) ## Wrap Message Text
    timeOpen += 500 ## Extend Time for Fading
    ## Create Message Window
    if EMMAMessage: alpha, messageWindow, messagePopupActive, timeOpened = 0.9, sg.Window("Message", [[sg.Column([[sg.Text("E.M.M.A. | Oszust Industries", font=('Any', 12), text_color='White', background_color='#696969'), sg.Push(background_color='#696969'), sg.Text("X", font=('Any', 14, 'bold'), enable_events=True, text_color='White', background_color='#696969', key='closeWindowButton')], [sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\EMMA\\" + imageFile + ".png", background_color='#696969'), sg.Text(title, font=('Any', 16, 'bold'), text_color='White', background_color='#696969')], [sg.Column([[]], size=(400, 3), background_color='#696969')]], background_color='#696969')], [sg.Text(message, font=('Any', 14), size=(430, None), text_color='White', background_color='#696969')]], background_color='#696969', location=(screenWidth-445,screenHeight-screenHeightSub), size=(430,messageHeight), alpha_channel=0, no_titlebar=True, resizable=False, finalize=True, keep_on_top=True, element_justification='l'), True, 0
    else: alpha, messageWindow, messagePopupActive, timeOpened = 0.9, sg.Window("Message", [[sg.Column([[sg.Text(systemName + " | Oszust Industries", font=('Any', 12), text_color='White', background_color='#696969'), sg.Push(background_color='#696969'), sg.Text("X", font=('Any', 14, 'bold'), enable_events=True, text_color='White', background_color='#696969', key='closeWindowButton')], [sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\" + imageFile + ".png", background_color='#696969'), sg.Text(title, font=('Any', 16, 'bold'), text_color='White', background_color='#696969')], [sg.Column([[]], size=(400, 3), background_color='#696969')]], background_color='#696969')], [sg.Text(message, font=('Any', 14), size=(430, None), text_color='White', background_color='#696969')]], background_color='#696969', location=(screenWidth-445,screenHeight-screenHeightSub), size=(430,messageHeight), alpha_channel=0, no_titlebar=True, resizable=False, finalize=True, keep_on_top=True, element_justification='l'), True, 0
    ## Window Shortcuts
    messageWindow.bind('<Delete>', '_Delete')            ## Close Window shortcut
    messageWindow.bind('<FocusOut>', '_FocusOut')        ## Window Focus Out
    messageWindow.bind('<ButtonRelease-1>', '_Clicked')  ## Window Clicked
    ## Mouse Icon Changes
    messageWindow["closeWindowButton"].Widget.config(cursor="hand2") ## Hover icon
    ## Fade In
    for i in range(1,int(alpha*100)):
        try:
            messageWindow.set_alpha(i/100)
            event, values = messageWindow.read(timeout=20)
            if (messageImportant == False and event != sg.TIMEOUT_KEY) or event == 'closeWindowButton' or (event == '_Delete'): ## Clicking Away Enabled
                messageWindow.close()
                messagePopupActive = False
                break
            elif event == '_Clicked': ## Clicked Action
                messageWindow.close()
                messagePopupActive = False
                break
        except: ## Issue with Fade in Effect
            messageWindow.close()
            messagePopupActive = False
            break
    while True:
        event, values = messageWindow.read(timeout=10)
        if messageImportant == True and (event == sg.WIN_CLOSED or event == 'closeWindowButton' or (event == '_Delete')): ## Message Important - No Clicking Away
            messageWindow.close()
            messagePopupActive = False
            break
        elif messageImportant == False and (event == sg.WIN_CLOSED or event == 'closeWindowButton' or (event == '_Delete') or (event == '_FocusOut')): ## Clicking Away Enabled
            messageWindow.close()
            messagePopupActive = False
            break
        elif event == '_Clicked': ## Clicked Action
            messageWindow.close()
            messagePopupActive = False
            break
        elif timeOpened >= timeOpen: ## Fade Out Window
            for i in range(int(alpha*100),1,-1): ## Start Fade Out
                messageWindow.set_alpha(i/150)
                event, values = messageWindow.read(timeout=20)
                if event != sg.TIMEOUT_KEY:
                    break
            messagePopupActive = False
            messageWindow.close()
            break
        timeOpened += 10



def loadGeniusMusicList(userInput):
    from PIL import Image
    import cloudscraper, io
    global geniusSongIDs, geniusURLs, layout, loadingAction, resultNumbers, songArtists, songNames
    artistSearch, geniusSongIDs, geniusURLs, layout, resultNumber, resultNumbers, songArtists, songNames = False, [], [], [[sg.Push(), sg.Text('Music Search Results:', font='Any 20'), sg.Push()]], 0, [], [], []
    if "genius.com" in userInput: userInput = userInput.split("https://genius.com/",1)[1].split("-lyrics",1)[0] ## Genius Website URL
    resp = requests.get("https://genius.p.rapidapi.com/search", params={'q': userInput.split("-featuring")[0]}, headers={'x-rapidapi-key':"a7197c62b1msh4b44e18fc9bc9dfp1421b0jsn91a22a0b0e9a",'x-rapidapi-host':"genius.p.rapidapi.com"})
    content = json.loads((resp.content).decode('utf8'))
    try: ## Test if bad API key
        if 'You are not subscribed to this API' in content['message']:
           loadingAction = "Genius_Page_Down"
           return
    except: pass
    ## No Song Found
    if len(content["response"]["hits"]) == 0:
        loadingAction = "No_Result_Found"
        return
    ## Find Number of Hits
    if len(content["response"]["hits"]) <= 8: hitCount = len(content["response"]["hits"]) ## Set Max to Max Results
    else: hitCount = 8 ## Set Max to 8 if More Than 8 Results Returned
    while hitCount > 0 and resultNumber < 10:
        geniusMusicSearchArtists = str(content["response"]["hits"][resultNumber]["result"]["artist_names"]).replace("(Rock)", "") ## Song Artists
        songArtists.append(geniusMusicSearchArtists) ## Add Artists to List 
        geniusMusicSearchPrimeArtist = str(content["response"]["hits"][resultNumber]["result"]["primary_artist"]["name"]).split('(')[0] ## Song Main Artist
        if str(content["response"]["hits"][0]["result"]["artist_names"]).replace(" ", "-").lower() == userInput: artistSearch = True ## Find if Search is an Artist
        geniusMusicSearchDate = str(content["response"]["hits"][resultNumber]["result"]["release_date_for_display"]) ## Result Release Date
        if geniusMusicSearchDate == "None": geniusMusicSearchDate = None ## Fix Release Date if None Found
        geniusMusicSearchSongNameInfo = str(content["response"]["hits"][resultNumber]["result"]["title_with_featured"]) ## Result Full Title
        songNames.append(geniusMusicSearchSongNameInfo) ## Add Song Full Title to List
        geniusMusicSearchGeniusURL = str(content["response"]["hits"][resultNumber]["result"]["url"]) ## Result Genius URL
        geniusURLs.append(geniusMusicSearchGeniusURL) ## Add Genius URL to List
        geniusMusicSearchGeniusSongID = str(content["response"]["hits"][resultNumber]["result"]["api_path"]) ## Song ID
        geniusSongIDs.append(geniusMusicSearchGeniusSongID) ## Add Song ID to List
        ## Shorten Results
        longSongNameInfo = geniusMusicSearchSongNameInfo
        longArtists = geniusMusicSearchArtists
        if len(geniusMusicSearchSongNameInfo) > 30: geniusMusicSearchSongNameInfo = geniusMusicSearchSongNameInfo[:29] + "..." ## Shorten Song Name
        if len(geniusMusicSearchArtists) > 30: geniusMusicSearchArtists = geniusMusicSearchArtists[:29] + "..." ## Shorten Artists Names
        ## Song Artwork
        try:
            geniusMusicSearchArtworkURL = str(content["response"]["hits"][resultNumber]["result"]["song_art_image_url"])
            if "https://assets.genius.com/images/default_cover_image.png" in geniusMusicSearchArtworkURL: png_data = str(pathlib.Path(__file__).resolve().parent) + "\\data\\defaultMusicArtwork.png"
            else:
                try: ## Look in Cache for Artwork
                    pil_image = Image.open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Music Search\\" + str(content["response"]["hits"][resultNumber]["result"]["song_art_image_url"]).split(".com/",1)[1].split(".",1)[0] + "-small.png") ## Open Artwork from Cache
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
                        png_data = pil_image.save(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Music Search\\" + str(content["response"]["hits"][resultNumber]["result"]["song_art_image_url"]).split(".com/",1)[1].split(".",1)[0] + "-small.png")
                    except: pass
                    png_data = png_bio.getvalue()
        except: png_data = str(pathlib.Path(__file__).resolve().parent) + "\\data\\defaultMusicArtwork.png" ## Default Artwork if Retrieval Fails
        ## Song Lyrics
        geniusMusicSearchLyricsState = str(content["response"]["hits"][resultNumber]["result"]["lyrics_state"]) ## Result Song Lyrics
        if geniusMusicSearchLyricsState.lower() == "complete": lyricsImage, lyricsHoverMessage = "checked", "Lyrics Found" ## Lyrics Found
        else: lyricsImage, lyricsHoverMessage = "failed", "Lyrics Not Found" ## No Lyrics Found
        ## Music Service
        if musicSub == "Apple": musicServiceImage = "musicSearchListenApple" ## Set Listening Link to Apple
        elif musicSub == "Spotify": musicServiceImage = "musicSearchListenSpotify" ## Set Listening Link to Spotify
        ## Song Window
        if (artistSearch == False or (artistSearch == True and geniusMusicSearchPrimeArtist.replace(" ", "-").split('(')[0].lower() == userInput)) and geniusMusicSearchArtists.lower() not in ["spotify", "genius"] and "genius" not in geniusMusicSearchArtists.lower():
            if geniusMusicSearchDate != None: layout += [[sg.Image(png_data), sg.Column([[sg.Text(str(geniusMusicSearchSongNameInfo), font='Any 16', tooltip=longSongNameInfo)], [sg.Text(str(geniusMusicSearchArtists), font='Any 14', tooltip=longArtists)], [sg.Text(str(geniusMusicSearchDate), font='Any 12')]]), sg.Push(), sg.Column([[sg.Image(str(pathlib.Path(__file__).resolve().parent)+'\\data\\' + lyricsImage + '.png', tooltip=lyricsHoverMessage), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchGenius.png', border_width=0, button_color='#2B475D', key='searchmusicListSearchGenius_' + str(resultNumber), tooltip="Open Genius Lyrics page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\' + musicServiceImage + '.png', border_width=0, button_color='#2B475D', key='searchmusicListPlaySong_' + str(resultNumber), tooltip="Play Song"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\openView.png', border_width=0, button_color='#2B475D', key='searchMusicListOpenSong_' + str(resultNumber), tooltip="Open Music Search Result")]])]]
            else: layout += [[sg.Image(png_data), sg.Column([[sg.Text(str(geniusMusicSearchSongNameInfo), font='Any 16', tooltip=longSongNameInfo)], [sg.Text(str(geniusMusicSearchArtists), font='Any 14', tooltip=longArtists)]]), sg.Push(), sg.Column([[sg.Image(str(pathlib.Path(__file__).resolve().parent)+'\\data\\' + lyricsImage + '.png', tooltip=lyricsHoverMessage), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchGenius.png', border_width=0, button_color='#2B475D', key='searchmusicListSearchGenius_' + str(resultNumber), tooltip="Open Genius Lyrics page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\' + musicServiceImage + '.png', border_width=0, button_color='#2B475D', key='searchmusicListPlaySong_' + str(resultNumber), tooltip="Play Song"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\openView.png', border_width=0, button_color='#2B475D', key='searchMusicListOpenSong_' + str(resultNumber), tooltip="Open Music Search Result")]])]]
            resultNumbers.append(resultNumber)
        elif len(content["response"]["hits"]) > 8: hitCount += 1
        else: hitCount -= 1
        resultNumber += 1
        hitCount -= 1
    layout += [[sg.Push(), sg.Text("Music Search powered by Genius", font='Any 11'), sg.Push()]] ## Credits
    ## Check if Any Good Results Found
    if len(resultNumbers) == 0: loadingAction = "No_Result_Found"
    elif len(resultNumbers) == 1: loadingAction = "Only_One_Result"
    else: loadingAction = "Search_Finished"

def geniusMusicSearchList(userInput):
    global geniusSongIDs, geniusURLs, layout, loadingAction, resultNumbers, songArtists, songNames
    ## Loading Screen
    loadingPopup, loadingAction = sg.Window("", [[sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", key='loadingGIFImage')]], transparent_color=sg.theme_background_color(), element_justification='c', no_titlebar=True, keep_on_top=True), "Start"
    loadingPopup["loadingGIFImage"].update_animation_no_buffering(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", time_between_frames=30) ## Start Loading Screen Faster
    while True:
        event, values = loadingPopup.read(timeout=10)
        loadingPopup["loadingGIFImage"].update_animation_no_buffering(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", time_between_frames=30) ## Load Loading GIF
        ## Actions from Thread
        if loadingAction == "Start": ## Start Music Search List Thread
            loadGeniusMusicListThread = threading.Thread(name="loadGeniusMusicList", target=loadGeniusMusicList, args=(userInput,))
            loadGeniusMusicListThread.start()
            loadingAction = "Running"
        elif loadingAction == "No_Result_Found": ## No Music Search Result Found
            loadingPopup.close() ## Close Loading Popup
            MusicSearchSongWindow = sg.Window("*", [[sg.Text("No results found.", font='Any 14')], [sg.Button("Close", button_color=('White', 'Red'), key='closeFailedMusicSearchButton')]], resizable=False, finalize=True, keep_on_top=True, element_justification='c')
            MusicSearchSongWindow.bind('<Delete>', '_Delete')  ## Close Window shortcut
            for key in ['closeFailedMusicSearchButton']: MusicSearchSongWindow[key].Widget.config(cursor="hand2") ## Hover icons
            while True:
                event, values = MusicSearchSongWindow.read()
                if event == sg.WIN_CLOSED or event == 'closeFailedMusicSearchButton' or (event == '_Delete'): ## Window Closed
                    MusicSearchSongWindow.close()
                    return
        elif loadingAction == "Genius_Page_Down": ## Genius's Service is Down
            loadingPopup.close() ## Close Loading Popup
            MusicSearchSongWindow = sg.Window("*", [[sg.Text("            Genius service down.      \n       Please try again a little later.      ", font='Any 14')], [sg.Button("Close", button_color=('White', 'Red'), key='closeFailedMusicSearchButton')]], resizable=False, finalize=True, keep_on_top=True, element_justification='c')
            MusicSearchSongWindow.bind('<Delete>', '_Delete')  ## Close Window shortcut
            for key in ['closeFailedMusicSearchButton']: MusicSearchSongWindow[key].Widget.config(cursor="hand2") ## Hover icons
            while True:
                event, values = MusicSearchSongWindow.read()
                if event == sg.WIN_CLOSED or event == 'closeFailedMusicSearchButton' or (event == '_Delete'): ## Window Closed
                    MusicSearchSongWindow.close()
                    return
        elif loadingAction == "Search_Finished": ## Show Music Search List Window
            loadingPopup.close()
            break
        elif loadingAction == "Only_One_Result": ## Only One Result Found, Open It
            loadingPopup.close()
            geniusMusicSearch(geniusSongIDs[0], True)
            return
    MusicSearchListWindow = sg.Window("Music Search - List Results", layout, resizable=False, finalize=True, keep_on_top=True, element_justification='l')
    ## Window Shortcuts
    MusicSearchListWindow.bind('<Delete>', '_Delete')  ## Close Window shortcut
    ## Mouse Icon Changes
    for resultNumber in resultNumbers:
        MusicSearchListWindow["searchmusicListSearchGenius_" + str(resultNumber)].Widget.config(cursor="hand2")  ## Genius Page Hover icon
        MusicSearchListWindow["searchmusicListPlaySong_" + str(resultNumber)].Widget.config(cursor="hand2")      ## Listen Music Hover icon
        MusicSearchListWindow["searchMusicListOpenSong_" + str(resultNumber)].Widget.config(cursor="hand2")      ## Open Song Hover icon
    while True:
        event, values = MusicSearchListWindow.read(timeout=10)
        if event == sg.WIN_CLOSED or (event == '_Delete'): ## Window Closed
            MusicSearchListWindow.close()
            break
        elif 'searchmusicListSearchGenius' in event: webbrowser.open(geniusURLs[int(event.split("_")[-1])], new=2, autoraise=True) ## Open Genius Page
        elif 'searchmusicListPlaySong_' in event: ## Play Song Online
            if musicSub == "Apple": webbrowser.open("https://music.apple.com/us/search?term=" + songArtists[int(event.split("_")[-1])].replace(" ", "%20") + "%20" + songNames[int(event.split("_")[-1])].replace(" ", "%20"), new=2, autoraise=True)
            elif musicSub == "Spotify": webbrowser.open("https://open.spotify.com/search/" + songArtists[int(event.split("_")[-1])].replace(" ", "%20") + "%20" + songNames[int(event.split("_")[-1])].replace(" ", "%20"), new=2, autoraise=True)
        elif 'searchMusicListOpenSong' in event: ## Open Song in Music Search
            HomeWindow.Element('songSearchBox').Update(songNames[int(event.split("_")[-1])] + " - " + songArtists[int(event.split("_")[-1])])
            MusicSearchListWindow.close()
            geniusMusicSearch(geniusSongIDs[int(event.split("_")[-1])], True)
            break

def loadGeniusMusic(userInput, forceResult):
    from PIL import Image
    import bs4, cloudscraper, io, re
    global badWordCount, clearMusicSearch, geniusMusicSearchAlbum, geniusMusicSearchAlbumCurrent, geniusMusicSearchAlbumLength, geniusMusicSearchArtistURL, geniusMusicSearchArtists, geniusMusicSearchDate, geniusMusicSearchGeniusURL, geniusMusicSearchGenre, geniusMusicSearchLabels, geniusMusicSearchPrimeArtist, geniusMusicSearchSongName, geniusMusicSearchSongNameInfo, loadingAction, lyrics, lyricsListFinal, png_data
    artistSearch, goodResult, resultCount = False, False, 0
    if "genius.com" in userInput: userInput = userInput.split("https://genius.com/",1)[1].split("-lyrics",1)[0] ## Genius Website URL
    if "/songs/" in userInput: ## Song ID Search
        resp = requests.get("https://genius.p.rapidapi.com" + userInput, headers={'x-rapidapi-key':"a7197c62b1msh4b44e18fc9bc9dfp1421b0jsn91a22a0b0e9a",'x-rapidapi-host':"genius.p.rapidapi.com"})
        content = json.loads((resp.content).decode('utf8'))
        try: ## Test if bad API key
            if 'You are not subscribed to this API' in content['message']:
               loadingAction = "Genius_Page_Down"
               return
        except: pass
        musicSearchJsonContent = content["response"]["song"]
    else: ## Normal Search
        resp = requests.get("https://genius.p.rapidapi.com/search", params={'q': userInput.split("-featuring")[0]}, headers={'x-rapidapi-key':"a7197c62b1msh4b44e18fc9bc9dfp1421b0jsn91a22a0b0e9a",'x-rapidapi-host':"genius.p.rapidapi.com"})
        content = json.loads((resp.content).decode('utf8'))
        try: ## Test if bad API key
            if 'You are not subscribed to this API' in content['message']:
               loadingAction = "Genius_Page_Down"
               return
        except: pass
        ## No Song Found
        hitsFound = len(content["response"]["hits"])
        if hitsFound == 0: ## No Results Found
            loadingAction = "No_Result_Found"
            print("HI")
            return
        musicSearchJsonContent = content["response"]["hits"][resultCount]["result"]
    while goodResult == False:
        badWordCount, lyricsList, lyricsListFinal = 0, [], []
        if artistSearch == False or str(musicSearchJsonContent["artist_names"]).replace("\u200b","").replace(" ", "-").split('(')[0].lower() == userInput: ## Check if Search is Artist
            try: geniusMusicSearchArtists = str(musicSearchJsonContent["artist_names"]).replace("(Rock)", "") ## Song Artists
            except: ## No Results Left
                loadingAction = "No_Result_Found"
                print("HI")
                return
            geniusMusicSearchPrimeArtist = str(musicSearchJsonContent["primary_artist"]["name"]).split('(')[0] ## Song Main Artist
        ## Move to List Results
            if forceResult == False and str(musicSearchJsonContent["artist_names"]).replace(" ", "-").lower() == userInput: ## Change to Artist Search
                loadingAction = "Artist_Search"
                return
            geniusMusicSearchDate = str(musicSearchJsonContent["release_date_for_display"]) ## Song Release Date
            if geniusMusicSearchDate == "None": geniusMusicSearchDate = None ## Fix Release Date if None Found
            geniusMusicSearchSongNameInfo = str(musicSearchJsonContent["title_with_featured"]) ## Song Full Title
            geniusMusicSearchArtistURL = str(musicSearchJsonContent["primary_artist"]["url"])
            geniusMusicSearchGeniusURL = str(musicSearchJsonContent["url"]) ## Song Genius URL
            geniusMusicSearchSongName = str(musicSearchJsonContent["title"]) ## Song Title
            ## Song Artwork
            try:
                geniusMusicSearchArtworkURL = str(musicSearchJsonContent["song_art_image_url"])
                if "https://assets.genius.com/images/default_cover_image.png" in geniusMusicSearchArtworkURL: png_data = str(pathlib.Path(__file__).resolve().parent) + "\\data\\defaultMusicArtwork.png"
                else:
                    try: ## Look in Cache for Artwork
                        pil_image = Image.open(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Music Search\\" + str(musicSearchJsonContent["song_art_image_url"]).split(".com/",1)[1].split(".",1)[0] + ".png")
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
                            pathlib.Path(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Music Search").mkdir(parents=True, exist_ok=True) ## Create Music Search Cache Folder
                            png_data = pil_image.save(str(pathlib.Path(__file__).resolve().parent) + "\\cache\\Music Search\\" + str(musicSearchJsonContent["song_art_image_url"]).split(".com/",1)[1].split(".",1)[0] + ".png")
                        except: pass
                        png_data = png_bio.getvalue()
            except: png_data = str(pathlib.Path(__file__).resolve().parent) + "\\data\\defaultMusicArtwork.png"
            ## Album, Album List, Genre, and Label
            html = bs4.BeautifulSoup((requests.get(geniusMusicSearchGeniusURL)).text, "html.parser") # Scrape the info from the HTML
            if "Genius is down for a quick minute!" in str(html): ## Check if Genius's Service is Down
                loadingAction = "Genius_Page_Down"
                return
            elif "make sure you're a human" in str(html): ## Check if Genius's Service is Down
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
                geniusMusicSearchLabels = (re.sub(r'<.+?>', '', str(songScrapedInfo))).replace(" &amp; ", ",,,").replace(" ,,,", ",,,").replace(" (Label)", "") ## Song's Labels
                geniusMusicSearchLabels = str(geniusMusicSearchLabels).split(", Release Date")[0].split(", Copyright")[0].split(',,,') ## Put Labels in List
                geniusMusicSearchLabels = str(geniusMusicSearchLabels).split(',') ## Split Labels
                if len(geniusMusicSearchLabels) > 3: geniusMusicSearchLabels = geniusMusicSearchLabels[:3] ## Shorten Labels List
            except: geniusMusicSearchLabels = None
            ## Song Lyrics
            if str(musicSearchJsonContent["lyrics_state"]).lower() == "complete":
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
    import eyed3, re
    global badWordCount, clearMusicSearch, geniusMusicSearchAlbum, geniusMusicSearchAlbumCurrent, geniusMusicSearchAlbumLength, geniusMusicSearchArtistURL, geniusMusicSearchArtists, geniusMusicSearchDate, geniusMusicSearchGeniusURL, geniusMusicSearchGenre, geniusMusicSearchLabels, geniusMusicSearchPrimeArtist, geniusMusicSearchSongName, geniusMusicSearchSongNameInfo, loadingAction, lyrics, lyricsListFinal, png_data
    ## Loading Screen
    loadingPopup, loadingAction, loadingStatus = sg.Window("", [[sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", background_color='#1b2838', key='loadingGIFImage')], [sg.Text("Loading...", font='Any 16', background_color='#1b2838', key='loadingScreenText')]], background_color='#1b2838', element_justification='c', no_titlebar=True, keep_on_top=True), "Start", "Start"
    loadingPopup["loadingGIFImage"].UpdateAnimation(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", time_between_frames=30) ## Start Loading Screen Faster
    ## Refresh Home Screen's Time
    while True:
        event, values = loadingPopup.read(timeout=10)
        loadingPopup["loadingGIFImage"].UpdateAnimation(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", time_between_frames=30) ## Load Loading GIF
        ## Actions from Thread
        if loadingAction == "Start": ## Start Music Search Thread
            loadGeniusMusicThread = threading.Thread(name="loadGeniusMusic", target=loadGeniusMusic, args=(userInput,forceResult,))
            loadGeniusMusicThread.start()
            loadingAction = "Running"
        elif loadingAction == "No_Result_Found": ## No Music Search Result Found
            print("FFFF")
            loadingPopup.close() ## Close Loading Popup
            MusicSearchSongWindow = sg.Window("*", [[sg.Text("No results found.", font='Any 14')], [sg.Button("Close", button_color=('White', 'Red'), key='closeFailedMusicSearchButton')]], resizable=False, finalize=True, keep_on_top=True, element_justification='c')
            MusicSearchSongWindow.bind('<Delete>', '_Delete')  ## Close Window shortcut
            for key in ['closeFailedMusicSearchButton']: MusicSearchSongWindow[key].Widget.config(cursor="hand2") ## Hover icons
            while True:
                event, values = MusicSearchSongWindow.read()
                if event == sg.WIN_CLOSED or event == 'closeFailedMusicSearchButton' or (event == '_Delete'): ## Window Closed
                    MusicSearchSongWindow.close()
                    return
        elif loadingAction == "Genius_Page_Down": ## Genius's Service is Down
            loadingPopup.close() ## Close Loading Popup
            MusicSearchSongWindow = sg.Window("*", [[sg.Text("            Genius service down.      \n       Please try again a little later.      ", font='Any 14')], [sg.Button("Close", button_color=('White', 'Red'), key='closeFailedMusicSearchButton')]], resizable=False, finalize=True, keep_on_top=True, element_justification='c')
            MusicSearchSongWindow.bind('<Delete>', '_Delete')  ## Close Window shortcut
            for key in ['closeFailedMusicSearchButton']: MusicSearchSongWindow[key].Widget.config(cursor="hand2") ## Hover icons
            while True:
                event, values = MusicSearchSongWindow.read()
                if event == sg.WIN_CLOSED or event == 'closeFailedMusicSearchButton' or (event == '_Delete'): ## Window Closed
                    MusicSearchSongWindow.close()
                    return
        elif loadingAction == "Genius_Robot_Check": ## Genius is Checking Robot
            loadingPopup.close() ## Close Loading Popup
            MusicSearchSongWindow = sg.Window("*", [[sg.Text("      Genius thinks you're a robot.      \n         Please disable your VPN.        ", font='Any 14')], [sg.Button("Fix", button_color=('White', 'Blue'), key='openGeniusLink'), sg.Button("Close", button_color=('White', 'Red'), key='closeFailedMusicSearchButton')]], resizable=False, finalize=True, keep_on_top=True, element_justification='c')
            MusicSearchSongWindow.bind('<Delete>', '_Delete')  ## Close Window shortcut
            for key in ['closeFailedMusicSearchButton', 'openGeniusLink']: MusicSearchSongWindow[key].Widget.config(cursor="hand2") ## Hover icons
            while True:
                event, values = MusicSearchSongWindow.read()
                if event == sg.WIN_CLOSED or event == 'closeFailedMusicSearchButton' or (event == '_Delete'): ## Window Closed
                    MusicSearchSongWindow.close()
                    return
                elif event == 'openGeniusLink':
                    os.chdir("C:\\Program Files\\NordVPN\\")
                    os.system('nordvpn -d')
        elif loadingAction == "Artist_Search": ## Start Artist Search
            loadingPopup.close()
            geniusMusicSearchList(userInput)
            return
        elif loadingAction == "Search_Finished": ## Show Music Search Window
            loadingPopup.close()
            break
    ## Shorten Results
    longSongNameInfo = geniusMusicSearchSongNameInfo
    longArtists = geniusMusicSearchArtists
    longAlbum = geniusMusicSearchAlbum
    if geniusMusicSearchSongNameInfo != None and len(geniusMusicSearchSongNameInfo) > 42: geniusMusicSearchSongNameInfo = geniusMusicSearchSongNameInfo[:39] + "..." ## Shorten Song Name
    if geniusMusicSearchArtists != None and len(geniusMusicSearchArtists) > 45: geniusMusicSearchArtists = geniusMusicSearchArtists[:42] + "..." ## Shorten Artists Names
    if geniusMusicSearchAlbum != None and len(geniusMusicSearchAlbum) > 45: geniusMusicSearchAlbum = geniusMusicSearchAlbum[:42] + "..." ## Shorten Album Name
    ## Song Window
    if lyrics != None: lyricsRightClickMenu = ['', ['Copy', 'Lookup Definition', 'Add to Profanity Engine', 'Remove from Profanity Engine']] ## Lyrics Right Click Menu - Profanity Engine
    else: lyricsRightClickMenu = ['', ['Copy', 'Lookup Definition']] ## Lyrics Right Click Menu - No Profanity Engine
    layout = [[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchMenu.png', border_width=0, button_color='#2B475D', key='musicSearchResultsMenu', tooltip="All Results"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\personSearch.png', border_width=0, button_color='#2B475D', key='musicSearchArtistResultsMenu', tooltip="Search Artist"), sg.Push(background_color='#2B475D'), sg.Text("Music Search Result", font='Any 20', background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Push(background_color='#2B475D'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchMP3Opener.png', border_width=0, button_color='#2B475D', key='downloadMetadataMp3Button', tooltip="Burn Metadata to MP3")]]
    if musicSub == "Apple": layout += [[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchArtist.png', border_width=0, button_color='#2B475D', key='musicSearchArtistButton', tooltip="Open Artist page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchGenius.png', border_width=0, button_color='#2B475D', key='searchmusicSearchGenius', tooltip="Open Genius Lyrics page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchListenApple.png', border_width=0, button_color='#2B475D', key='musicSearchListenButton', tooltip="Play Song - Apple Music")]]
    elif layout == "Spotify": layout += [[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchArtist.png', border_width=0, button_color='#2B475D', key='musicSearchArtistButton', tooltip="Open Artist page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchGenius.png', border_width=0, button_color='#2B475D', key='searchmusicSearchGenius', tooltip="Open Genius Lyrics page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchListenSpotify.png', border_width=0, button_color='#2B475D', key='musicSearchListenButton', tooltip="Play Song - Spotify")]]
    if geniusMusicSearchAlbum != None and geniusMusicSearchDate != None: layout += [[sg.Image(png_data)], [sg.Text(geniusMusicSearchSongNameInfo, font='Any 20 bold', background_color='#2B475D', enable_events=True, key='geniusMusicSearchSongNameInfoText', tooltip=longSongNameInfo)], [sg.Text(geniusMusicSearchAlbum, font='Any 18', background_color='#2B475D', enable_events=True, key='geniusMusicSearchAlbumText', tooltip=longAlbum)], [sg.Text(geniusMusicSearchArtists, font='Any 16', background_color='#2B475D', enable_events=True, key='geniusMusicSearchArtistsText', tooltip=longArtists)], [sg.Text(geniusMusicSearchGenre.upper() + " " + u"\N{Dot Operator}" + " " + geniusMusicSearchDate, font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchGenreText')]] ## Album Name Found
    elif geniusMusicSearchAlbum != None and geniusMusicSearchDate == None: layout += [[sg.Image(png_data)], [sg.Text(geniusMusicSearchSongNameInfo, font='Any 20 bold', background_color='#2B475D', enable_events=True, key='geniusMusicSearchSongNameInfoText', tooltip=longSongNameInfo)], [sg.Text(geniusMusicSearchAlbum, font='Any 18', background_color='#2B475D', enable_events=True, key='geniusMusicSearchAlbumText', tooltip=longAlbum)], [sg.Text(geniusMusicSearchArtists, font='Any 16', background_color='#2B475D', enable_events=True, key='geniusMusicSearchArtistsText', tooltip=longArtists)], [sg.Text(geniusMusicSearchGenre.upper(), font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchGenreText')]] ## Album Name Found and No Release Date
    elif geniusMusicSearchAlbum == None and geniusMusicSearchDate != None: layout += [[sg.Image(png_data)], [sg.Text(geniusMusicSearchSongNameInfo, font='Any 20 bold', background_color='#2B475D', enable_events=True, key='geniusMusicSearchSongNameInfoText', tooltip=longSongNameInfo)], [sg.Text(geniusMusicSearchArtists, font='Any 16', background_color='#2B475D', enable_events=True, key='geniusMusicSearchArtistsText', tooltip=longArtists)], [sg.Text(geniusMusicSearchGenre.upper() + " " + u"\N{Dot Operator}" + " " + geniusMusicSearchDate, font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchGenreText')]] ## Album Name not Found
    else: layout += [[sg.Image(png_data)], [sg.Text(geniusMusicSearchSongNameInfo, font='Any 20 bold', background_color='#2B475D', enable_events=True, key='geniusMusicSearchSongNameInfoText', tooltip=longSongNameInfo)], [sg.Text(geniusMusicSearchArtists, font='Any 16', background_color='#2B475D', enable_events=True, key='geniusMusicSearchArtistsText', tooltip=longArtists)], [sg.Text(geniusMusicSearchGenre.upper(), font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchGenreText')]] ## No Album Name and No Release Date
    if lyrics != None: layout += [[sg.Multiline("", size=(55,20), font='Any 11', autoscroll=False, disabled=True, right_click_menu=lyricsRightClickMenu, key='MusicSearchSongWindowLyrics')]] ## Add Empty Lyrics Box
    else: layout += [[sg.Text("Lyrics couldn't be found on Genius.", font='Any 12 bold', background_color='#2B475D')]] ## No Lyrics Found Message
    if lyrics != None: layout += [[sg.Text("Profanity Engine: Lyrics are 100% clean.", font='Any 11', background_color='#2B475D', key='songUsableText')]] ## Default Profanity Engine Text
    if geniusMusicSearchLabels != None and len(geniusMusicSearchLabels) > 1: layout += [[sg.Text("Labels: " + str(geniusMusicSearchLabels).replace("&amp;", "&").replace("[", "").replace("]", "").replace('"', "").replace("'", ""), font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchLabels')]] ## Song's Labels
    elif geniusMusicSearchLabels != None and len(geniusMusicSearchLabels) == 1: layout += [[sg.Text("Label: " + str(geniusMusicSearchLabels).replace("&amp;", "&").replace("[", "").replace("]", "").replace('"', "").replace("'", ""), font='Any 11', background_color='#2B475D', enable_events=True, key='geniusMusicSearchLabels')]] ## Song's Label
    layout += [[sg.Text("Music Search powered by Genius", font='Any 11', background_color='#2B475D')]] ## Credits
    MusicSearchSongWindow = sg.Window("Music Search - Song", layout, background_color='#2B475D', resizable=False, finalize=True, keep_on_top=True, element_justification='c')
    ## Lyrics Right Click Menu
    if lyrics != None: lyricsLine:sg.Multiline = MusicSearchSongWindow['MusicSearchSongWindowLyrics']
    ## Window Shortcuts
    MusicSearchSongWindow.bind('<Tab>', '_Tab')            ## List Result shortcut
    MusicSearchSongWindow.bind('<PageDown>', '_PageDown')  ## List Result shortcut
    MusicSearchSongWindow.bind('<Delete>', '_Delete')      ## Close Window shortcut
    MusicSearchSongWindow.bind('<Home>', '_Home')          ## Genius Lyrics shortcut
    MusicSearchSongWindow.bind('<End>', '_End')            ## Artist shortcut
    MusicSearchSongWindow.bind('<`>', '_`')                ## Listen shortcut
    ## Mouse Icon Changes
    for key in ['downloadMetadataMp3Button','musicSearchArtistButton','musicSearchArtistResultsMenu','musicSearchListenButton','musicSearchResultsMenu','searchmusicSearchGenius']: MusicSearchSongWindow[key].Widget.config(cursor="hand2") ## Hover icons
    if geniusMusicSearchSongNameInfo != None: MusicSearchSongWindow["geniusMusicSearchSongNameInfoText"].Widget.config(cursor="hand2")  ## Song Name Text Hover icon
    if geniusMusicSearchAlbum != None: MusicSearchSongWindow["geniusMusicSearchAlbumText"].Widget.config(cursor="hand2")                ## Song Album Text Hover icon
    if geniusMusicSearchArtists != None: MusicSearchSongWindow["geniusMusicSearchArtistsText"].Widget.config(cursor="hand2")            ## Song Artist Text Hover icon
    if geniusMusicSearchGenre != None: MusicSearchSongWindow["geniusMusicSearchGenreText"].Widget.config(cursor="hand2")                ## Song Genre Text Hover icon
    if geniusMusicSearchLabels != None: MusicSearchSongWindow["geniusMusicSearchLabels"].Widget.config(cursor="hand2")                  ## Song Label Hover icon
    ## Print Lyrics and Check for Profanity
    if lyrics != None:
        try:
            ## Load Profanity Engine Dictionary
            for word in range(len(profanityEngineDefinitions)): profanityEngineDefinitions[word] = profanityEngineDefinitions[word].lower().replace("\n", "")
            ## Print Each Lyric Line and Check for Profanity
            for i in range(len(lyricsListFinal)):
                badLine = False ## Reset Bad Line for each Line
                for phrase in profanityEngineDefinitions:
                    if badLine == False and phrase[len(phrase)-1] == "~" and re.search(r"\b{}\b".format(phrase.replace("~", "")), lyricsListFinal[i].replace(",", ""), re.IGNORECASE) is not None: ## Check Words and Phrases for Bad Words, Ending with '
                        MusicSearchSongWindow['MusicSearchSongWindowLyrics'].print(lyricsListFinal[i], autoscroll=False, text_color='Red')
                        badWordCount += 1
                        badLine = True
                    elif badLine == False and phrase[len(phrase)-1] != "~" and re.search(r"\b{}\b".format(phrase.replace("~", "'")), lyricsListFinal[i].replace(",", ""), re.IGNORECASE) is not None: ## Check Words and Phrases for Bad Words
                        MusicSearchSongWindow['MusicSearchSongWindowLyrics'].print(lyricsListFinal[i], autoscroll=False, text_color='Red')
                        badWordCount += 1
                        badLine = True
                if badLine == False: MusicSearchSongWindow['MusicSearchSongWindowLyrics'].print(lyricsListFinal[i], autoscroll=False) ## Clean Line
        except: ## Profanity Engine Dictionary Failed to Load
            profanityEngineDefinitions = "Failed"
            for i in range(len(lyricsListFinal)): MusicSearchSongWindow['MusicSearchSongWindowLyrics'].print(lyricsListFinal[i], autoscroll=False)
    ## Update Profanity Engine Text
    if lyrics != None and profanityEngineDefinitions != "Failed":
        MusicSearchSongWindow['songUsableText'].update("Profanity Engine: Lyrics are " + str(round((1 - (badWordCount/len(lyricsListFinal))) * 100)) + "% clean.")
        if round((1 - (badWordCount/len(lyricsListFinal))) * 100) == 100: MusicSearchSongWindow['songUsableText'].update(text_color='#00C957')
        elif round((1 - (badWordCount/len(lyricsListFinal))) * 100) >= 95: MusicSearchSongWindow['songUsableText'].update(text_color='#FFD700')
        elif round((1 - (badWordCount/len(lyricsListFinal))) * 100) >= 90: MusicSearchSongWindow['songUsableText'].update(text_color='#FF6103')
        elif round((1 - (badWordCount/len(lyricsListFinal))) * 100) < 90: MusicSearchSongWindow['songUsableText'].update(text_color='#DC143C')
    elif lyrics != None and profanityEngineDefinitions == "Failed": MusicSearchSongWindow['songUsableText'].update("Profanity Engine failed to load.", font='Any 13 bold')
    while True:
        event, values = MusicSearchSongWindow.read(timeout=10)
        if event == sg.WIN_CLOSED or (event == '_Delete'): ## Window Closed
            MusicSearchSongWindow.close()
            clearMusicSearch = True
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
        elif event in lyricsRightClickMenu[1]:
            try:
                if event == 'Copy': ## Copy Lyrics Text
                    try:
                        selectedText = lyricsLine.Widget.selection_get() ## Selected Text
                        MusicSearchSongWindow.TKroot.clipboard_clear()
                        MusicSearchSongWindow.TKroot.clipboard_append(selectedText)
                    except: pass
                elif event == 'Lookup Definition':
                    selectedText = lyricsLine.Widget.selection_get().split(" ")[0] ## Selected Text
                    webbrowser.open("https://www.dictionary.com/browse/" + selectedText.replace(",", "").replace(".", "").replace("?", "").replace("!", "").replace(" ", "-"), new=2, autoraise=True)
                elif event == 'Add to Profanity Engine':
                    try:
                        headers, profanityEngineDefinitionsNew, selectedText, updatedProfanityEngineDefinitions = CaseInsensitiveDict(), [], lyricsLine.Widget.selection_get(), []
                        updatedProfanityEngineDefinitions = getServerData("profanityList") ## Get Server Values
                        for phrase in updatedProfanityEngineDefinitions: profanityEngineDefinitionsNew.append(phrase.replace("'", "~").lower()) ## Remove ' for List
                        profanityEngineDefinitionsNew.append(selectedText.strip().replace("'", "~").replace(",", "").replace(".", "").replace("?", "").replace("!", ""))
                        jsonData = '{"sessionID":"'+sessionID+'","field":"profanityList","data":"'+str(profanityEngineDefinitionsNew)+'"}'
                        resp = requests.post('https://881theparkserver.com/api/importantValues/write', headers=headers, data=jsonData)
                        ## Reload Music Search's Lyrics
                        MusicSearchSongWindow['MusicSearchSongWindowLyrics'].update("")
                        try:
                            ## Load Profanity Engine Dictionary
                            badWordCount, profanityEngineDefinitions = 0, getServerData("profanityList")
                            for word in range(len(profanityEngineDefinitions)): profanityEngineDefinitions[word] = profanityEngineDefinitions[word].lower().replace("\n", "")
                            ## Print Each Lyric Line and Check for Profanity
                            for i in range(len(lyricsListFinal)):
                                badLine = False ## Reset Bad Line for each Line
                                for phrase in profanityEngineDefinitions:
                                    if badLine == False and phrase[len(phrase)-1] == "~" and re.search(r"\b{}\b".format(phrase.replace("~", "")), lyricsListFinal[i].replace(",", ""), re.IGNORECASE) is not None: ## Check Words and Phrases for Bad Words, Ending with '
                                        MusicSearchSongWindow['MusicSearchSongWindowLyrics'].print(lyricsListFinal[i], autoscroll=False, text_color='Red')
                                        badWordCount += 1
                                        badLine = True
                                    elif badLine == False and phrase[len(phrase)-1] != "~" and re.search(r"\b{}\b".format(phrase.replace("~", "'")), lyricsListFinal[i].replace(",", ""), re.IGNORECASE) is not None: ## Check Words and Phrases for Bad Words
                                        MusicSearchSongWindow['MusicSearchSongWindowLyrics'].print(lyricsListFinal[i], autoscroll=False, text_color='Red')
                                        badWordCount += 1
                                        badLine = True
                                if badLine == False: MusicSearchSongWindow['MusicSearchSongWindowLyrics'].print(lyricsListFinal[i], autoscroll=False) ## Clean Line
                        except: ## Profanity Engine Dictionary Failed to Load
                            profanityEngineDefinitions = "Failed"
                            for i in range(len(lyricsListFinal)): MusicSearchSongWindow['MusicSearchSongWindowLyrics'].print(lyricsListFinal[i], autoscroll=False)
                        ## Update Profanity Engine Text
                        if lyrics != None and profanityEngineDefinitions != "Failed":
                            MusicSearchSongWindow['songUsableText'].update("Profanity Engine: Lyrics are " + str(round((1 - (badWordCount/len(lyricsListFinal))) * 100)) + "% clean.")
                            if round((1 - (badWordCount/len(lyricsListFinal))) * 100) == 100: MusicSearchSongWindow['songUsableText'].update(text_color='#00C957')
                            elif round((1 - (badWordCount/len(lyricsListFinal))) * 100) >= 95: MusicSearchSongWindow['songUsableText'].update(text_color='#FFD700')
                            elif round((1 - (badWordCount/len(lyricsListFinal))) * 100) >= 90: MusicSearchSongWindow['songUsableText'].update(text_color='#FF6103')
                            elif round((1 - (badWordCount/len(lyricsListFinal))) * 100) < 90: MusicSearchSongWindow['songUsableText'].update(text_color='#DC143C')
                        elif profanityEngineDefinitions == "Failed": MusicSearchSongWindow['songUsableText'].update("Profanity Engine failed to load.", font='Any 13 bold')
                        if selectedText[0] == " ": selectedText = selectedText[1:]
                        if selectedText[len(selectedText)-1] == " ": selectedText = selectedText[:-1]
                        messagePopupTimed(False, "Profanity Engine",'"' + selectedText + '" was successfully added to Profanity Engine.', "saved", None, 2000, False) ## Show Success Message
                    except:
                        if selectedText[0] == " ": selectedText = selectedText[1:]
                        if selectedText[len(selectedText)-1] == " ": selectedText = selectedText[:-1]
                        messagePopupTimed(False, "Profanity Engine", "Failed to add " + selectedText + " to Profanity Engine.", "error", None, 2000, False)
                elif event == 'Remove from Profanity Engine':
                    try:
                        headers, profanityEngineDefinitionsNew, profanityEngineMatches, selectedText, updatedProfanityEngineDefinitions = CaseInsensitiveDict(), [], [], lyricsLine.Widget.selection_get(), []
                        updatedProfanityEngineDefinitions = getServerData("profanityList") ## Get Server Values
                        for phrase in updatedProfanityEngineDefinitions: profanityEngineDefinitionsNew.append(phrase) ## Add All Phrases to profanityEngineDefinitionsNew
                        try:
                            profanityEngineDefinitionsNew.remove(selectedText.strip().replace("'", "~").lower().replace(",", "").replace(".", "").replace("?", "").replace("!", ""))
                            profanityEngineMatches.append(selectedText.replace("'", "~"))
                        except:
                            try:
                                for word in selectedText.split():
                                    if word.strip().replace("'", "~").replace(",", "").replace(".", "").replace("?", "").replace("!", "").lower() in profanityEngineDefinitionsNew:
                                        profanityEngineMatches.append(word.replace("'", "~"))
                                        try: profanityEngineDefinitionsNew.remove(word.strip().replace("'", "~").replace(",", "").replace(".", "").replace("?", "").replace("!", "").lower())
                                        except: pass
                            except: pass
                        if len(profanityEngineMatches) > 0:
                            jsonData = '{"sessionID":"'+sessionID+'","field":"profanityList","data":"'+str(profanityEngineDefinitionsNew)+'"}'
                            resp = requests.post('https://881theparkserver.com/api/importantValues/write', headers=headers, data=jsonData)
                            ## Reload Music Search's Lyrics
                            MusicSearchSongWindow['MusicSearchSongWindowLyrics'].update("")
                            try:
                                ## Load Profanity Engine Dictionary
                                badWordCount, profanityEngineDefinitions = 0, getServerData("profanityList")
                                for word in range(len(profanityEngineDefinitions)): profanityEngineDefinitions[word] = profanityEngineDefinitions[word].lower().replace("\n", "")
                                ## Print Each Lyric Line and Check for Profanity
                                for i in range(len(lyricsListFinal)):
                                    badLine = False ## Reset Bad Line for each Line
                                    for phrase in profanityEngineDefinitions:
                                        if badLine == False and re.search(r"\b{}\b".format(phrase.replace("~", "'")), lyricsListFinal[i], re.IGNORECASE) is not None: ## Check Words and Phrases for Bad Words
                                            MusicSearchSongWindow['MusicSearchSongWindowLyrics'].print(lyricsListFinal[i], autoscroll=False, text_color='Red')
                                            badWordCount += 1
                                            badLine = True
                                    if badLine == False: MusicSearchSongWindow['MusicSearchSongWindowLyrics'].print(lyricsListFinal[i], autoscroll=False) ## Clean Line
                            except: ## Profanity Engine Dictionary Failed to Load
                                profanityEngineDefinitions = "Failed"
                                for i in range(len(lyricsListFinal)): MusicSearchSongWindow['MusicSearchSongWindowLyrics'].print(lyricsListFinal[i], autoscroll=False)
                            ## Update Profanity Engine Text
                            if lyrics != None and profanityEngineDefinitions != "Failed":
                                MusicSearchSongWindow['songUsableText'].update("Profanity Engine: Lyrics are " + str(round((1 - (badWordCount/len(lyricsListFinal))) * 100)) + "% clean.")
                                if round((1 - (badWordCount/len(lyricsListFinal))) * 100) == 100: MusicSearchSongWindow['songUsableText'].update(text_color='#00C957')
                                elif round((1 - (badWordCount/len(lyricsListFinal))) * 100) >= 95: MusicSearchSongWindow['songUsableText'].update(text_color='#FFD700')
                                elif round((1 - (badWordCount/len(lyricsListFinal))) * 100) >= 90: MusicSearchSongWindow['songUsableText'].update(text_color='#FF6103')
                                elif round((1 - (badWordCount/len(lyricsListFinal))) * 100) < 90: MusicSearchSongWindow['songUsableText'].update(text_color='#DC143C')
                            elif profanityEngineDefinitions == "Failed": MusicSearchSongWindow['songUsableText'].update("Profanity Engine failed to load.", font='Any 13 bold')
                            ## Show Success Message
                            if str(profanityEngineMatches)[2] == " ": profanityEngineMatches = str(profanityEngineMatches)[3:]
                            if str(profanityEngineMatches)[len(profanityEngineMatches)-3] == " ": profanityEngineMatches = str(profanityEngineMatches)[:-3]
                            if len(profanityEngineMatches) == 1: messagePopupTimed(False, "Profanity Engine",'"' + str(profanityEngineMatches).replace("[", "").replace("]", "").replace("'", "").replace('"', "").replace("~", "'") + '" was successfully removed from Profanity Engine.', "saved", None, 2000, False)
                            else: messagePopupTimed(False, "Profanity Engine",'"' + str(profanityEngineMatches).replace("[", "").replace("]", "").replace("'", "").replace('"', "").replace("~", "'") + '" were successfully removed from Profanity Engine.', "saved", None, 2000, False)
                        else: messagePopupTimed(False, "Profanity Engine","No words needed to be removed from Profanity Engine.", "saved", None, 2000, False)
                    except: messagePopupTimed(False, "Profanity Engine", 'Failed to remove "' + selectedText + '" from Profanity Engine.', "error", None, 2000, False)
            except: pass
        elif event == 'musicSearchResultsMenu' or (event == '_Tab'): ## Move Song to List Results
            MusicSearchSongWindow.close()
            if "/songs/" in userInput: geniusMusicSearchList(geniusMusicSearchSongNameInfo + " - " + geniusMusicSearchArtists)
            else: geniusMusicSearchList(userInput)
            break
        elif event == 'musicSearchArtistResultsMenu': ## Move Artist to List Results
            MusicSearchSongWindow.close()
            geniusMusicSearchList(geniusMusicSearchPrimeArtist)
            break
        elif event == 'downloadMetadataMp3Button' or (event == '_PageDown'): ## Download Metadata to MP3
            lyricsText, metadataBurnLyricsOnlyValue, metadataChangeFileNameValue, metadataMultipleArtistsValue = "", False, True, False
            musicSearchMetadataWindow = sg.Window("Music Search - Metadata Burner", [[sg.Text("Oszust OS Metadata Burner", font=('Helvetica', 20), background_color='#696969')], [sg.HorizontalSeparator()], [sg.Text("Choose Audio File: ", font=("Helvetica", 14), background_color='#696969')], [sg.Input("", do_not_clear=True, size=(38,1), enable_events=True, key='metadataBurnerFileChooserInput'), sg.FileBrowse(file_types=(("Audio Files", "*.mp3"),), key='metadataBurnerFileChooser')], [sg.HorizontalSeparator()], [sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\crossMark.png', border_width=0, button_color='#696969', key='metadataBurnLyricsOnlyCheckbox', tooltip="Burn lyrics only - No"), sg.Text("Burn Lyrics Only", font=('Helvetica', 11), background_color='#696969', key='metadataBurnLyricsOnlyText')], [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\crossMark.png', border_width=0, button_color='#696969', key='metadataMultipleArtistsCheckbox', tooltip="Multiple artists - No"), sg.Text("Album Includes Multiple Artists?", font=('Helvetica', 11), background_color='#696969', key='metadataMultipleArtistsText')], [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\checkMark.png', border_width=0, button_color='#696969', key='metadataChangeFileNameCheckbox', tooltip="Change file name - Yes"), sg.Text("Change Audio File's Name", font=('Helvetica', 11), background_color='#696969', key='metadataChangeFileNameText')]], element_justification='l', background_color='#696969')], [sg.Button("Burn Metadata", button_color=("White", "Blue"), key='burnMetadataInfo'), sg.Button("Cancel", button_color=("White", "Red"), key='closeMetadataWindow')]], background_color='#696969', no_titlebar=True, resizable=False, finalize=True, keep_on_top=True, element_justification='c')
            for key in ['metadataBurnerFileChooser', 'metadataBurnLyricsOnlyCheckbox', 'metadataMultipleArtistsCheckbox', 'metadataChangeFileNameCheckbox', 'burnMetadataInfo', 'closeMetadataWindow']: musicSearchMetadataWindow[key].Widget.config(cursor="hand2") ## Hover icons
            musicSearchMetadataWindow.bind('<Delete>', '_Delete')  ## Close Window shortcut
            while True:
                event, values = musicSearchMetadataWindow.read(timeout=10)
                if event == sg.WIN_CLOSED or event == 'closeMetadataWindow' or (event == '_Delete'): ## Close Settings Window
                    musicSearchMetadataWindow.close()
                    break
                elif event == 'metadataBurnLyricsOnlyCheckbox' and metadataBurnLyricsOnlyValue == True: ## Set Burn Lyrics Only to False
                    musicSearchMetadataWindow['metadataBurnLyricsOnlyCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\crossMark.png')
                    musicSearchMetadataWindow['metadataBurnLyricsOnlyCheckbox'].set_tooltip("Burn lyrics only - No")
                    metadataBurnLyricsOnlyValue = False
                elif event == 'metadataBurnLyricsOnlyCheckbox' and metadataBurnLyricsOnlyValue == False: ## Set Burn Lyrics Only to True
                    musicSearchMetadataWindow['metadataBurnLyricsOnlyCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\checkMark.png')
                    musicSearchMetadataWindow['metadataBurnLyricsOnlyCheckbox'].set_tooltip("Burn lyrics only - Yes")
                    metadataBurnLyricsOnlyValue = True
                elif event == 'metadataMultipleArtistsCheckbox' and metadataMultipleArtistsValue == True: ## Set Multiple Artists to False
                    musicSearchMetadataWindow['metadataMultipleArtistsCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\crossMark.png')
                    musicSearchMetadataWindow['metadataMultipleArtistsCheckbox'].set_tooltip("Multiple artists - No")
                    metadataMultipleArtistsValue = False
                elif event == 'metadataMultipleArtistsCheckbox' and metadataMultipleArtistsValue == False: ## Set Multiple Artists to True
                    musicSearchMetadataWindow['metadataMultipleArtistsCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\checkMark.png')
                    musicSearchMetadataWindow['metadataMultipleArtistsCheckbox'].set_tooltip("Multiple artists - Yes")
                    metadataMultipleArtistsValue = True
                elif event == 'metadataChangeFileNameCheckbox' and metadataChangeFileNameValue == True: ## Set Change File Name to False
                    musicSearchMetadataWindow['metadataChangeFileNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\crossMark.png')
                    musicSearchMetadataWindow['metadataChangeFileNameCheckbox'].set_tooltip("Change file name - No")
                    metadataChangeFileNameValue = False
                elif event == 'metadataChangeFileNameCheckbox' and metadataChangeFileNameValue == False: ## Set Change File Name to True
                    musicSearchMetadataWindow['metadataChangeFileNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\checkMark.png')
                    musicSearchMetadataWindow['metadataChangeFileNameCheckbox'].set_tooltip("Change file name - Yes")
                    metadataChangeFileNameValue = True
                elif event == 'burnMetadataInfo': ## Burn Metadata
                    if values['metadataBurnerFileChooserInput'] != None and len(values['metadataBurnerFileChooserInput']) > 0: ## Check if input has value
                        try:
                            for i in range(len(lyricsListFinal)): ## Get Lyrics
                                if len(lyricsListFinal[i]) == 0: lyricsText += "\n"
                                else: lyricsText += lyricsListFinal[i] + "\n"
                            audiofile = eyed3.load(values['metadataBurnerFileChooserInput']) ## Load MP3
                            audiofile.initTag(version=(2, 3, 0)) ## Version is Important
                            if metadataBurnLyricsOnlyValue == False: ## Save All Details
                                audiofile.tag.artist = longArtists ## Artist
                                if metadataMultipleArtistsValue: audiofile.tag.album_artist = "Various Artists" ## Album's Artists (Various Artists)
                                else: audiofile.tag.album_artist = geniusMusicSearchPrimeArtist ## Album's Artists
                                audiofile.tag.title = longSongNameInfo ## Title
                                if geniusMusicSearchDate != "Unknown Release Date": audiofile.tag.recording_date = geniusMusicSearchDate[-4:] ## Year
                                audiofile.tag.genre = geniusMusicSearchGenre ## Genre
                                audiofile.tag.album = longAlbum ## Album
                                if geniusMusicSearchLabels != None: audiofile.tag.publisher = geniusMusicSearchLabels[0].replace("[", "").replace("]", "").replace("'", "") ## Label
                                if geniusMusicSearchAlbumCurrent != None: audiofile.tag.track_num = geniusMusicSearchAlbumCurrent ## Curent Song Position
                                if geniusMusicSearchAlbumLength != None: audiofile.tag.track_total = geniusMusicSearchAlbumLength ## Album length
                                audiofile.tag.images.set(4, png_data, "image/png") ## Artwork - Back Cover
                                audiofile.tag.images.set(3, png_data, "image/png") ## Artwork - Front Cover
                                audiofile.tag.images.set(0, png_data, "image/png") ## Artwork - Other
                                audiofile.tag.images.set(4, png_data, "image/jpeg", "cover") ## Artwork - Back Cover
                                audiofile.tag.images.set(3, png_data, "image/jpeg", "cover") ## Artwork - Front Cover
                                audiofile.tag.images.set(0, png_data, "image/jpeg", "cover") ## Artwork - Other
                            if lyrics != None: audiofile.tag.lyrics.set(lyricsText) ## Save Lyrics
                            audiofile.tag.comments.set(u"Metadata: Oszust Industries") ## Comment
                            audiofile.tag.save() ## Save File
                            if metadataChangeFileNameValue: ## Change the audio file's name
                                try: os.rename(values['metadataBurnerFileChooserInput'], values['metadataBurnerFileChooserInput'].rsplit('/', 1)[0] + "/" + geniusMusicSearchSongNameInfo + "." + values['metadataBurnerFileChooserInput'].rsplit('.', 1)[1]) ## Raname MP3 to Song Name
                                except: pass
                            musicSearchMetadataWindow.close()
                            messagePopupTimed(False, "Metadata Burner", "Metadata has been saved to " + values['metadataBurnerFileChooserInput'] + ".", "saved", None, 2000, False) ## Metadata Worked
                            break
                        except:
                            musicSearchMetadataWindow.close()
                            messagePopupTimed(False, "Metadata Burner", "Metadata failed.\nPlease try again.", "error", None, 2000, False) ## Metadata Failed
                            break
                    else:
                        musicSearchMetadataWindow.close()
                        break
        elif event == 'musicSearchArtistButton' or (event == '_End'): webbrowser.open(geniusMusicSearchArtistURL, new=2, autoraise=True)  ## Open Artist's Genius Page
        elif event == 'searchmusicSearchGenius' or (event == '_Home'): webbrowser.open(geniusMusicSearchGeniusURL, new=2, autoraise=True) ## Open Genius Page
        elif event == 'musicSearchListenButton' or (event == '_`'): ## Play Song Online
            if musicSub == "Apple": webbrowser.open("https://music.apple.com/us/search?term=" + geniusMusicSearchPrimeArtist.replace(" ", "%20") + "%20" + geniusMusicSearchSongName.replace(" ", "%20"), new=2, autoraise=True)
            elif musicSub == "Spotify": webbrowser.open("https://open.spotify.com/search/" + geniusMusicSearchPrimeArtist.replace(" ", "%20") + "%20" + geniusMusicSearchSongName.replace(" ", "%20"), new=2, autoraise=True)

def burnAudioData():
    try:
        lyricsText = "" ## Reset Variables
        for i in range(len(lyricsListFinal)): ## Get Lyrics
            if len(lyricsListFinal[i]) == 0: lyricsText += "\n"
            else: lyricsText += lyricsListFinal[i] + "\n"
        audiofile = eyed3.load(audioSavedPath) ## Load MP3
        audiofile.initTag(version=(2, 3, 0)) ## Version is Important
        audiofile.tag.artist = geniusMusicSearchArtists ## Artist
        audiofile.tag.album_artist = geniusMusicSearchPrimeArtist ## Album's Artists
        audiofile.tag.title = geniusMusicSearchSongNameInfo ## Title
        if geniusMusicSearchDate != None and geniusMusicSearchDate != "Unknown Release Date": audiofile.tag.recording_date = geniusMusicSearchDate[-4:] ## Year
        audiofile.tag.genre = geniusMusicSearchGenre ## Genre
        audiofile.tag.album = geniusMusicSearchAlbum ## Album
        if geniusMusicSearchLabels != None: audiofile.tag.publisher = geniusMusicSearchLabels[0].replace("[", "").replace("]", "").replace("'", "") ## Label
        if geniusMusicSearchAlbumCurrent != None: audiofile.tag.track_num = geniusMusicSearchAlbumCurrent ## Curent Song Position
        if geniusMusicSearchAlbumLength != None: audiofile.tag.track_total = geniusMusicSearchAlbumLength ## Album length
        audiofile.tag.images.set(4, png_data, "image/png") ## Artwork - Back Cover
        audiofile.tag.images.set(3, png_data, "image/png") ## Artwork - Front Cover
        audiofile.tag.images.set(0, png_data, "image/png") ## Artwork - Other
        audiofile.tag.images.set(4, png_data, "image/jpeg", "cover") ## Artwork - Back Cover
        audiofile.tag.images.set(3, png_data, "image/jpeg", "cover") ## Artwork - Front Cover
        audiofile.tag.images.set(0, png_data, "image/jpeg", "cover") ## Artwork - Other
        if lyrics != None: audiofile.tag.lyrics.set(lyricsText) ## Save Lyrics
        audiofile.tag.comments.set(u"Metadata: Oszust Industries") ## Comment
        audiofile.tag.save() ## Save File
        ## Change the audio file's name
        try: os.rename(audioSavedPath, audioSavedPath.replace(audioSavedPath.rsplit('\\', 1)[1], "") + "\\" + geniusMusicSearchSongNameInfo + "." + audioSavedPath.rsplit('.', 1)[1]) ## Raname MP3 to Song Name
        except: pass
        print("Burn Worked")
    except Exception as Argument: crashMessage("Error Burner: " + str(Argument))


## Start System
try: softwareSetup()
except Exception as Argument: crashMessage("Error 00: " + str(Argument))