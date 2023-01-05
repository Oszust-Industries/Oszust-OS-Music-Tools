## Oszust OS Music Tools - Oszust Industries
## Created on: 1-02-23 - Last update: 1-04-23
softwareVersion = "v1.0.0.000"
import ctypes, eyed3, json, os, pathlib, platform, psutil, re, requests, threading, urllib.request, webbrowser, win32clipboard
from moviepy.editor import *
from pytube import YouTube
import PySimpleGUI as sg

def softwareConfig():
    ## System Configuration
    global deactivateFileOpening, exitSystem, systemBuild, systemName
    exitSystem, systemName, systemBuild = False, "Oszust OS Music Tools", "dev"
    deactivateFileOpening = False

def getScaling():
    # Get Scaling Infomation
    root = sg.tk.Tk()
    scaling = root.winfo_fpixels('1i')/72
    root.destroy()
    return scaling

def softwareSetup():
    ## Setup Software
    global exitSystem, screenHeight, screenWidth
    print("Loading...\nLaunching Interface...")
    ## Fix Screen Size
    ctypes.windll.user32.SetProcessDPIAware(False) ## DPI Awareness
    scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100 ## Get Windows Scale Factor
    screenWidth, screenHeight = sg.Window.get_screen_size() ## Get WxH of Pixels
    sg.set_options(scaling = (getScaling() * min(screenWidth / (screenWidth * scaleFactor), screenHeight / (1080 * scaleFactor)))) ## Apply Fix to Windows
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0) ## Hide Console
    ## Setup Commands
    softwareConfig() ## Get User's Configs
    quickActions("wifiTest") ## Check for WIFI
    homeScreen("Music_Downloader")

def quickActions(Action):
    if Action == "wifiTest": ## Test if Device has Internet
        try: urllib.request.urlopen("http://google.com", timeout=3)
        except: quickActions("noWifi")
    elif Action in ["noWifi"]: ## No Internet
        failedSetupWindow = sg.Window("NO WIFI", [[sg.Text("There doesn't seem to be any internet connection on your device.\n" + systemName + " requires an internet connection.", justification='c', font='Any 16')], [sg.Button("Retry Connection", button_color=("White", "Blue"), key='RetryWIFI'), sg.Button("Quit App", button_color=("White", "Red"), key='Quit')]], resizable=False, finalize=True, keep_on_top=True, element_justification='c')
        while True:
            event, values = failedSetupWindow.read()
            if event == sg.WIN_CLOSED or event == 'Quit': exit()
            elif event in ['RetryWIFI']: ## Retry Internet Test
                failedSetupWindow.close()
                softwareSetup()

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

def homeScreenAppPanels(appName):
    if appName == "Music_Downloader":
        return [[sg.Push(background_color='#4d4d4d'), sg.Text("Music Downloader:", font='Any 20', background_color='#4d4d4d'), sg.Push(background_color='#4d4d4d')],
        [sg.Text("YouTube Link:", font='Any 13', background_color='#4d4d4d'), sg.Input("", do_not_clear=True, size=(48,1),enable_events=True, key='musicDownloaderYoutubeLink'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\clipboard.png', border_width=0, key='musicDownloaderLinkClipboard', tooltip="Paste Link"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\youtubeDownloader.png', border_width=0, key='musicDownloaderOpenYoutube', tooltip="Open YouTube")],
        [sg.Text("Download Location:", font='Any 13', background_color='#4d4d4d'), sg.Input("", do_not_clear=True, size=(50,1),enable_events=True, key='musicDownloaderLocation'), sg.FolderBrowse()],
        [sg.HorizontalSeparator()], [sg.Push(background_color='#4d4d4d'), sg.Text("Downloader Settings:", font='Any 15', background_color='#4d4d4d'), sg.Push(background_color='#4d4d4d'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\reset.png', border_width=0, key='musicDownloaderResetSettings', tooltip="Paste Link")],
        [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\true.png', border_width=0, key='musicDownloaderAudioDownloadCheckbox', tooltip="Paste Link"), sg.Text("Burn lyrics to the audio file", font='Any 14', background_color='#4d4d4d')],
        [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\false.png', border_width=0, key='musicDownloaderVideoDownloadCheckbox', tooltip="Paste Link"), sg.Text("Song's album is a compilation by various artists", font='Any 14', background_color='#4d4d4d')],
        [sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\false.png', border_width=0, key='musicDownloaderDownloadNameCheckbox', tooltip="Paste Link"), sg.Text("Rename download to:", font='Any 14', background_color='#4d4d4d'), sg.Input("", do_not_clear=True, size=(31,1), enable_events=True, visible=False, key='musicDownloaderDownloadNameInput'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\clipboard_Small.png', border_width=0, visible=False, key='musicDownloaderDownloadNameClipboard', tooltip="Paste Link"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\clearInput.png', border_width=0, visible=False, key='musicDownloaderDownloadNameClear', tooltip="Paste Link")],
        [sg.HorizontalSeparator()], [sg.Text("", font='Any 4', background_color='#4d4d4d')], [sg.Push(background_color='#4d4d4d'), sg.Button("Download", button_color=("White", "Blue"), font='Any 15', size=(10, 1), key='musicDownloaderDownloadButton'), sg.Push(background_color='#4d4d4d')]]
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
    ## Oszust OS Music Tools List
    applist, apps = [[]], ["Music Downloader", "YouTube Downloader"] ##["Music Search", "Metadata Burner", "Music Downloader", "YouTube Downloader", "Top Music", "Music Player"]
    for app in apps: applist += [[sg.Column([[sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent) + "\\data\\" + app.lower().replace(" ", "") + ".png", button_color='#64778D', border_width=0, key=app.replace(" ", "_") + "_AppSelector", tooltip='Open ' + app)]], pad=((5,5), (5, 5)))]] ## Add apps to side panel
    ## Home Window
    appWindow = homeScreenAppPanels(appSelected) ## App Panel Loading Based on App
    layout = [[sg.Column(applist, size=(72,390), pad=((10,10), (10, 10)), background_color='#4d4d4d', scrollable=False, vertical_scroll_only=True), sg.Column(appWindow, size=(600,390), pad=((10,10), (10, 10)), background_color='#4d4d4d', scrollable=False, vertical_scroll_only=True)]]
    layout += [[sg.Column([[sg.Text(platform.system() + " | " + softwareVersion + " | " + systemBuild + " | Online", enable_events=True, font='Any 13', key='versionTextHomeBottom'), sg.Push(), sg.Text("Oszust Industries", enable_events=True, font='Any 13', key='creditsTextHomeBottom')], [sg.Column([[]], size=(715, 1), pad=(0,0))]], size=(715, 30), pad=(0,0))]]
    HomeWindow = sg.Window('Oszust OS Music Tools', layout, background_color='#1b2838', margins=(0,0), finalize=True, resizable=True, text_justification='r')
    ## Mouse Icon Changes, Key Binds, Mouse Binds, App Variables
    if appSelected == "Music_Downloader":
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
## Credits Window
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
## Music Downloader (Buttons/Events)
        elif appSelected == "Music_Downloader":
            if event == 'youtubeDownloaderLinkClipboard':
                win32clipboard.OpenClipboard()
                HomeWindow.Element('youtubeDownloaderYoutubeLink').Update(win32clipboard.GetClipboardData())
                win32clipboard.CloseClipboard()
            elif event == 'youtubeDownloaderOpenYoutube': webbrowser.open("youtube.com", new=2, autoraise=True)
            elif event == 'youtubeDownloaderDownloadNameClipboard':
                win32clipboard.OpenClipboard()
                HomeWindow.Element('youtubeDownloaderDownloadNameInput').Update(win32clipboard.GetClipboardData())
                win32clipboard.CloseClipboard()
            elif event == 'youtubeDownloaderDownloadNameClear': HomeWindow.Element('youtubeDownloaderDownloadNameInput').Update("")
            elif event == 'youtubeDownloaderResetSettings':
                youtubeAudioDownload = False
                HomeWindow['youtubeDownloaderAudioDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                HomeWindow['youtubeDownloaderVideoDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png')
                youtubeVideoDownload = True
                HomeWindow['youtubeDownloaderDownloadNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                HomeWindow.Element('youtubeDownloaderDownloadNameInput').Update("")
                for key in ['youtubeDownloaderDownloadNameInput', 'youtubeDownloaderDownloadNameClipboard', 'youtubeDownloaderDownloadNameClear']: HomeWindow.Element(key).Update(visible=False)
                youtubeDownloadName = False
            elif event == 'youtubeDownloaderAudioDownloadCheckbox' and youtubeAudioDownload == True:
                HomeWindow['youtubeDownloaderAudioDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                youtubeAudioDownload = False
            elif event == 'youtubeDownloaderAudioDownloadCheckbox' and youtubeAudioDownload == False:
                HomeWindow['youtubeDownloaderAudioDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png')
                youtubeAudioDownload = True
            elif event == 'youtubeDownloaderVideoDownloadCheckbox' and youtubeVideoDownload == True:
                HomeWindow['youtubeDownloaderVideoDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                youtubeVideoDownload = False
            elif event == 'youtubeDownloaderVideoDownloadCheckbox' and youtubeVideoDownload == False:
                HomeWindow['youtubeDownloaderVideoDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png')
                youtubeVideoDownload = True
            elif event == 'youtubeDownloaderDownloadNameCheckbox' and youtubeDownloadName == True:
                HomeWindow['youtubeDownloaderDownloadNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                for key in ['youtubeDownloaderDownloadNameInput', 'youtubeDownloaderDownloadNameClipboard', 'youtubeDownloaderDownloadNameClear']: HomeWindow.Element(key).Update(visible=False)
                youtubeDownloadName = False
            elif event == 'youtubeDownloaderDownloadNameCheckbox' and youtubeDownloadName == False:
                HomeWindow['youtubeDownloaderDownloadNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png')
                for key in ['youtubeDownloaderDownloadNameInput', 'youtubeDownloaderDownloadNameClipboard', 'youtubeDownloaderDownloadNameClear']: HomeWindow.Element(key).Update(visible=True)
                youtubeDownloadName = True
            elif event == 'youtubeDownloaderDownloadButton':
                if youtubeDownloadName: youtubeDownloadName = values['youtubeDownloaderDownloadNameInput']
                downloadYouTube(values['youtubeDownloaderYoutubeLink'], values['youtubeDownloaderLocation'], youtubeAudioDownload, youtubeVideoDownload, youtubeDownloadName)
## YouTube Downloader (Buttons/Events)
        elif appSelected == "YouTube_Downloader":
            if event == 'youtubeDownloaderLinkClipboard':
                win32clipboard.OpenClipboard()
                HomeWindow.Element('youtubeDownloaderYoutubeLink').Update(win32clipboard.GetClipboardData())
                win32clipboard.CloseClipboard()
            elif event == 'youtubeDownloaderOpenYoutube': webbrowser.open("youtube.com", new=2, autoraise=True)
            elif event == 'youtubeDownloaderDownloadNameClipboard':
                win32clipboard.OpenClipboard()
                HomeWindow.Element('youtubeDownloaderDownloadNameInput').Update(win32clipboard.GetClipboardData())
                win32clipboard.CloseClipboard()
            elif event == 'youtubeDownloaderDownloadNameClear': HomeWindow.Element('youtubeDownloaderDownloadNameInput').Update("")
            elif event == 'youtubeDownloaderResetSettings':
                youtubeAudioDownload = False
                HomeWindow['youtubeDownloaderAudioDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                HomeWindow['youtubeDownloaderVideoDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png')
                youtubeVideoDownload = True
                HomeWindow['youtubeDownloaderDownloadNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                HomeWindow.Element('youtubeDownloaderDownloadNameInput').Update("")
                for key in ['youtubeDownloaderDownloadNameInput', 'youtubeDownloaderDownloadNameClipboard', 'youtubeDownloaderDownloadNameClear']: HomeWindow.Element(key).Update(visible=False)
                youtubeDownloadName = False
            elif event == 'youtubeDownloaderAudioDownloadCheckbox' and youtubeAudioDownload == True and youtubeVideoDownload == True:
                HomeWindow['youtubeDownloaderAudioDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                youtubeAudioDownload = False
            elif event == 'youtubeDownloaderAudioDownloadCheckbox' and youtubeAudioDownload == False:
                HomeWindow['youtubeDownloaderAudioDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png')
                youtubeAudioDownload = True
            elif event == 'youtubeDownloaderVideoDownloadCheckbox' and youtubeVideoDownload == True and youtubeAudioDownload == True:
                HomeWindow['youtubeDownloaderVideoDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                youtubeVideoDownload = False
            elif event == 'youtubeDownloaderVideoDownloadCheckbox' and youtubeVideoDownload == False:
                HomeWindow['youtubeDownloaderVideoDownloadCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png')
                youtubeVideoDownload = True
            elif event == 'youtubeDownloaderDownloadNameCheckbox' and youtubeDownloadName == True:
                HomeWindow['youtubeDownloaderDownloadNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\false.png')
                for key in ['youtubeDownloaderDownloadNameInput', 'youtubeDownloaderDownloadNameClipboard', 'youtubeDownloaderDownloadNameClear']: HomeWindow.Element(key).Update(visible=False)
                youtubeDownloadName = False
            elif event == 'youtubeDownloaderDownloadNameCheckbox' and youtubeDownloadName == False:
                HomeWindow['youtubeDownloaderDownloadNameCheckbox'].update(image_filename=str(pathlib.Path(__file__).resolve().parent) + '\\data\\true.png')
                for key in ['youtubeDownloaderDownloadNameInput', 'youtubeDownloaderDownloadNameClipboard', 'youtubeDownloaderDownloadNameClear']: HomeWindow.Element(key).Update(visible=True)
                youtubeDownloadName = True
            elif event == 'youtubeDownloaderDownloadButton':
                if youtubeDownloadName: youtubeDownloadName = values['youtubeDownloaderDownloadNameInput']
                downloadYouTube(values['youtubeDownloaderYoutubeLink'], values['youtubeDownloaderLocation'], youtubeAudioDownload, youtubeVideoDownload, youtubeDownloadName)

def downloadYouTube(youtubeLink, downloadLocation, audioFile, videoFile, renameFile):
    global audioSavedPath, youtubeTitle
    YouTube(youtubeLink).streams.filter(file_extension="mp4").get_highest_resolution().download(downloadLocation) ## Download Video
    youtubeTitle = (YouTube(youtubeLink).title).replace("|", "").replace("'", "").replace("/", "").replace("#", "").replace(".", "")
    if audioFile:
        ## Convert MP4 Video to MP3 Audio
        audioSavedPath = downloadLocation + "\\" + youtubeTitle + ".mp3"
        FILETOCONVERT = AudioFileClip(downloadLocation + "\\" + youtubeTitle + ".mp4")
        FILETOCONVERT.write_audiofile(audioSavedPath)
        FILETOCONVERT.close()
        if renameFile != False:
            try: os.rename(audioSavedPath, audioSavedPath.replace(audioSavedPath.rsplit('\\', 1)[1], "") + "\\" + renameFile + "." + audioSavedPath.rsplit('.', 1)[1]) ## Raname MP3 to Chosen Name
            except: pass
    if renameFile != False:
        videoSavedLocation = downloadLocation + "\\" + youtubeTitle + ".mp4"
        try: os.rename(videoSavedLocation, videoSavedLocation.replace(videoSavedLocation.rsplit('\\', 1)[1], "") + "\\" + renameFile + "." + videoSavedLocation.rsplit('.', 1)[1]) ## Raname MP4 to Chosen Name
        except: pass
    if videoFile == False: os.remove(downloadLocation + "\\" + youtubeTitle + ".mp4") ## Delete Video File
    youtubeTitle = re.sub("([\(\[]).*?([\)\]])", "\g<1>\g<2>", youtubeTitle)

def loadGeniusMusicList(userInput):
    from PIL import Image
    import cloudscraper, io
    global geniusSongIDs, geniusURLs, layout, loadingPopupAction, resultNumbers, songArtists, songNames
    artistSearch, geniusSongIDs, geniusURLs, layout, resultNumber, resultNumbers, songArtists, songNames = False, [], [], [[sg.Push(), sg.Text('Music Search Results:', font='Any 20'), sg.Push()], [sg.Push(), sg.Input(userInput, do_not_clear=True, size=(40,1),enable_events=True, key='songSearchBox'), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\search.png', border_width=0, key='searchSongSearchButton', tooltip="Search Music"), sg.Push()]], 0, [], [], []
    resp = requests.get("https://genius.p.rapidapi.com/search", params={'q': userInput.split("-featuring")[0]}, headers={'x-rapidapi-key':"a7197c62b1msh4b44e18fc9bc9dfp1421b0jsn91a22a0b0e9a",'x-rapidapi-host':"genius.p.rapidapi.com"})
    content = json.loads((resp.content).decode('utf8'))
    try: ## Test if bad API key
        if 'You are not subscribed to this API' in content['message']:
           loadingPopupAction = "Genius_Page_Down"
           return
    except: pass
    ## No Song Found
    if len(content["response"]["hits"]) == 0:
        loadingPopupAction = "No_Result_Found"
        layout += [[sg.Push(), sg.Text("No results found", font='Any 14'), sg.Push()]]
        return
    ## Find Number of Hits
    if len(content["response"]["hits"]) <= 8: hitCount = len(content["response"]["hits"]) ## Set Max to Max Results
    else: hitCount = 8 ## Set Max to 8 if More Than 8 Results Returned
    while hitCount > 0 and resultNumber < hitCount:
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
        ## Song Window
        if (artistSearch == False or (artistSearch == True and geniusMusicSearchPrimeArtist.replace(" ", "-").split('(')[0].lower() == userInput)) and geniusMusicSearchArtists.lower() not in ["spotify", "genius"] and "genius" not in geniusMusicSearchArtists.lower():
            if geniusMusicSearchDate != None: layout += [[sg.Image(png_data), sg.Column([[sg.Text(str(geniusMusicSearchSongNameInfo), font='Any 16', tooltip=longSongNameInfo)], [sg.Text(str(geniusMusicSearchArtists), font='Any 14', tooltip=longArtists)], [sg.Text(str(geniusMusicSearchDate), font='Any 12')]]), sg.Push(), sg.Column([[sg.Image(str(pathlib.Path(__file__).resolve().parent)+'\\data\\' + lyricsImage + '.png', tooltip=lyricsHoverMessage), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchGenius.png', border_width=0, key='searchmusicListSearchGenius_' + str(resultNumber), tooltip="Open Genius Lyrics page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\openView.png', border_width=0, key='searchMusicListOpenSong_' + str(resultNumber), tooltip="Open Music Search Result")]])]]
            else: layout += [[sg.Image(png_data), sg.Column([[sg.Text(str(geniusMusicSearchSongNameInfo), font='Any 16', tooltip=longSongNameInfo)], [sg.Text(str(geniusMusicSearchArtists), font='Any 14', tooltip=longArtists)]]), sg.Push(), sg.Column([[sg.Image(str(pathlib.Path(__file__).resolve().parent)+'\\data\\' + lyricsImage + '.png', tooltip=lyricsHoverMessage), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\musicSearchGenius.png', border_width=0, key='searchmusicListSearchGenius_' + str(resultNumber), tooltip="Open Genius Lyrics page"), sg.Button("", image_filename=str(pathlib.Path(__file__).resolve().parent)+'\\data\\openView.png', border_width=0, key='searchMusicListOpenSong_' + str(resultNumber), tooltip="Open Music Search Result")]])]]
            resultNumbers.append(resultNumber)
        elif len(content["response"]["hits"]) > 8: hitCount += 1
        else: hitCount -= 1
        resultNumber += 1
        hitCount -= 1
    layout += [[sg.Push(), sg.Text("Music Search powered by Genius", font='Any 11'), sg.Push()]] ## Credits
    loadingPopupAction = "Search_Finished"

def geniusMusicSearchList(userInput):
    global geniusSongIDs, geniusURLs, layout, loadingPopupAction, resultNumbers, songArtists, songNames
    ## Loading Screen
    loadingPopup, loadingPopupAction = sg.Window("", [[sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", key='loadingGIFImage')]], transparent_color=sg.theme_background_color(), element_justification='c', no_titlebar=True, keep_on_top=True), "Start"
    loadingPopup["loadingGIFImage"].update_animation_no_buffering(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", time_between_frames=30) ## Start Loading Screen Faster
    while True:
        event, values = loadingPopup.read(timeout=10)
        loadingPopup["loadingGIFImage"].update_animation_no_buffering(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", time_between_frames=30) ## Load Loading GIF
        ## Actions from Thread
        if loadingPopupAction == "Start": ## Start Music Search List Thread
            loadGeniusMusicListThread = threading.Thread(name="loadGeniusMusicList", target=loadGeniusMusicList, args=(userInput,))
            loadGeniusMusicListThread.start()
            loadingPopupAction = "Running"
        elif loadingPopupAction == "Genius_Page_Down": ## Genius's Service is Down
            loadingPopup.close() ## Close Loading Popup
            MusicSearchSongWindow = sg.Window("*", [[sg.Text("            Genius service down.      \n       Please try again a little later.      ", font='Any 14')], [sg.Button("Close", button_color=('White', 'Red'), key='closeFailedMusicSearchButton')]], resizable=False, finalize=True, keep_on_top=True, element_justification='c')
            MusicSearchSongWindow.bind('<Delete>', '_Delete')  ## Close Window shortcut
            for key in ['closeFailedMusicSearchButton']: MusicSearchSongWindow[key].Widget.config(cursor="hand2") ## Hover icons
            while True:
                event, values = MusicSearchSongWindow.read()
                if event == sg.WIN_CLOSED or event == 'closeFailedMusicSearchButton' or (event == '_Delete'): ## Window Closed
                    MusicSearchSongWindow.close()
                    return
        elif loadingPopupAction in ["Search_Finished", "Only_One_Result", "No_Result_Found"]: ## Show Music Search List Window
            loadingPopup.close()
            break
    MusicSearchListWindow = sg.Window("Music Search - List Results", layout, resizable=False, finalize=True, keep_on_top=True, element_justification='l')
    ## Window Shortcuts
    MusicSearchListWindow.bind('<Delete>', '_Delete')  ## Close Window shortcut
    ## Mouse Icon Changes
    for key in ['searchSongSearchButton']: MusicSearchListWindow[key].Widget.config(cursor="hand2") ## Hover icons
    for resultNumber in resultNumbers:
        MusicSearchListWindow["searchmusicListSearchGenius_" + str(resultNumber)].Widget.config(cursor="hand2")  ## Genius Page Hover icon
        MusicSearchListWindow["searchMusicListOpenSong_" + str(resultNumber)].Widget.config(cursor="hand2")      ## Open Song Hover icon
    while True:
        event, values = MusicSearchListWindow.read(timeout=10)
        if event == sg.WIN_CLOSED or (event == '_Delete'): ## Window Closed
            MusicSearchListWindow.close()
            break
        elif event == 'searchSongSearchButton':
            MusicSearchListWindow.close()
            geniusMusicSearchList(values['songSearchBox'])
            break
        elif 'searchmusicListSearchGenius' in event: webbrowser.open(geniusURLs[int(event.split("_")[-1])], new=2, autoraise=True) ## Open Genius Page
        elif 'searchMusicListOpenSong' in event: ## Open Song in Music Search
            MusicSearchListWindow.close()
            loadGeniusMusic(geniusSongIDs[int(event.split("_")[-1])], True)
            break

def loadGeniusMusic(userInput, forceResult):
    from PIL import Image
    import bs4, cloudscraper, io, re
    global audioSavedPath, badWordCount, geniusMusicSearchAlbum, geniusMusicSearchAlbumCurrent, geniusMusicSearchAlbumLength, geniusMusicSearchArtistURL, geniusMusicSearchArtists, geniusMusicSearchDate, geniusMusicSearchGeniusURL, geniusMusicSearchGenre, geniusMusicSearchLabels, geniusMusicSearchPrimeArtist, geniusMusicSearchSongName, geniusMusicSearchSongNameInfo, loadingPopupAction, lyrics, lyricsListFinal, png_data
    artistSearch, goodResult = False, False
    if "/songs/" in userInput: ## Song ID Search
        resp = requests.get("https://genius.p.rapidapi.com" + userInput, headers={'x-rapidapi-key':"a7197c62b1msh4b44e18fc9bc9dfp1421b0jsn91a22a0b0e9a",'x-rapidapi-host':"genius.p.rapidapi.com"})
        content = json.loads((resp.content).decode('utf8'))
        try: ## Test if bad API key
            if 'You are not subscribed to this API' in content['message']:
               loadingPopupAction = "Genius_Page_Down"
               return
        except: pass
        musicSearchJsonContent = content["response"]["song"]
    while goodResult == False:
        badWordCount, lyricsList, lyricsListFinal = 0, [], []
        if artistSearch == False or str(musicSearchJsonContent["artist_names"]).replace("\u200b","").replace(" ", "-").split('(')[0].lower() == userInput: ## Check if Search is Artist
            try: geniusMusicSearchArtists = str(musicSearchJsonContent["artist_names"]).replace("(Rock)", "") ## Song Artists
            except: ## No Results Left
                loadingPopupAction = "No_Result_Found"
                return
            geniusMusicSearchPrimeArtist = str(musicSearchJsonContent["primary_artist"]["name"]).split('(')[0] ## Song Main Artist
        ## Move to List Results
            if forceResult == False and str(musicSearchJsonContent["artist_names"]).replace(" ", "-").lower() == userInput: ## Change to Artist Search
                loadingPopupAction = "Artist_Search"
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
                loadingPopupAction = "Genius_Page_Down"
                return
            elif "make sure you're a human" in str(html): ## Check if Genius's Service is Down
                loadingPopupAction = "Genius_Robot_Check"
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
                    else: geniusMusicSearchAlbumCurrent = 1
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
            burnAudioData()
            return

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