## Oszust OS Setup Installer - v3.0.0(11.29.23) - Oszust Industries
installerVersion = "v2.4.1"
import os, subprocess, sys
def fixPython():
    print("Installing Python Packages...")
    install, packagesList = "Python", ["--upgrade pip", "pycrosskit", "pysimplegui", "requests"]
    try: subprocess.run(['py -m pip install --upgrade pip setuptools > /dev/null'], check = True) ## Test which Python is installed
    except: install = "Windows"
    for package in packagesList:
        try:
            if package == "--upgrade pip": os.system('python.exe -m pip install ' + package) ## Update pip
            elif install == "Python": os.system('py -m pip install ' + package + ' > /dev/null')
            elif install == "Windows": os.system('pip install ' + package + ' -q')
        except:
            exitText = input("Error 01: The installer(" + package + ") has failed. You seem to not have the correct Python installed. Press enter to quit installer...")
            exit()
    os.startfile(sys.argv[0])
    sys.exit()
try:
    from pycrosskit.shortcuts import Shortcut
    import PySimpleGUI as sg
    import requests
except: fixPython()
try: import ctypes, datetime, json, pathlib, pickle, platform, shutil, threading, urllib.request, webbrowser, win32com.client, zipfile
except: ## Python isn't on Environment Variables Fix
    exitText = input("\nPLEASE READ:\n\nError 01F: Please reinstall Python.\nClick Modify > Next > Check the box for 'Add Python to environment variables'\nThen click Install to fix Python\n\nPress enter to quit installer...")
    exit()

def setupConfig():
    global availableBranches, installLocation, recommendedBranch, systemBuild, systemName
    availableBranches, recommendedBranch, systemBuild, systemName = [], "", "", "Oszust OS Music Tools"
    installLocation = os.environ["ProgramFiles"] + "\\Oszust Industries\\" + systemName

def crashMessage(message):
    errorWindow = sg.Window("ERROR", [[sg.Text(message, font=("Any", 13))], [sg.Button("Report Error", button_color=("White", "Blue"), key='Report'), sg.Button("Quit", button_color=("White", "Red"), key='Quit')]], resizable=False, finalize=True, keep_on_top=True, element_justification='c')
    errorWindow["Report"].Widget.config(cursor="hand2")  ## Report Button Hover icon
    errorWindow["Quit"].Widget.config(cursor="hand2")    ## Quit Button Hover icon
    errorWindow.bind('<Insert>', '_Insert')  ## Report Error shortcut
    errorWindow.bind('<Delete>', '_Delete')  ## Close Window shortcut
    while True:
        event, values = errorWindow.read()
        if event == sg.WIN_CLOSED or event == 'Quit' or (event == '_Delete'):
            exit()
        elif event == 'Report' or (event == '_Insert'): webbrowser.open("https://github.com/Oszust-Industries/" + systemName.replace(" ", "-") + "/issues/new", new=2, autoraise=True)

def setupInstall():
    global availableBranches, desktopShortcut, errorCode, installLocation, installStatus, installText, systemBuild
    desktopShortcut, errorCode, installStatus, installText, lastStatus = True, "", 0, "Starting Setup", 0
    print("Starting Installer...\nLaunching Interface...")
    theme_dict = {'BACKGROUND': '#2B475D','TEXT': '#FFFFFF','INPUT': '#F2EFE8','TEXT_INPUT': '#000000','SCROLL': '#F2EFE8','BUTTON': ('#000000', '#C2D4D8'),'PROGRESS': ('#FFFFFF', '#C7D5E0'),'BORDER': 1,'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0}
    sg.theme_add_new('Dashboard', theme_dict)
    sg.LOOK_AND_FEEL_TABLE['Dashboard'] = theme_dict
    sg.theme('Dashboard')
    DARK_HEADER_COLOR = '#1B2838'
    setupConfig() ## Get Setup's Configs
    if os.name not in ["nt"]: crashMessage("Error 04: This program is built only for Windows devices.") ## Check Device Type
    if sys.version_info >= (3, 7) == False: crashMessage("Error 05: You seem to have an old version of Python installed. The program requires v3.7.0 or higher.") ## Check Python Version
    try: urllib.request.urlopen("http://google.com", timeout=3) ## Check WIFI Connection
    except: crashMessage("Error 07: There doesn't seem to be any internet connection on your device.")
    ## Get GitHub Branches
    resp = requests.get("https://api.github.com/repos/Oszust-Industries/" + systemName.replace(" ", "-") + "/branches")
    content = json.loads((resp.content).decode('utf8'))
    for branch in range(len(content)):
        if content[branch]["protected"] == False and content[branch]["name"].lower() not in ["devTesting", "main"]: availableBranches.append(content[branch]["name"])
    if len(availableBranches) < 1: ## Check for any public builds
        installationWindow = sg.Window("Installer - Error", [[sg.Text(systemName + " doesn't have any public builds.", font=("Helvetica", 14))], [sg.Button("Ok", button_color=('White', 'Green'), key='doneButton')]], size=(430, 120), resizable=False, finalize=True, element_justification='c')
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0) ## Hide Console
        ## Window Shortcuts / Mouse Icon Changes
        installationWindow.bind('<Delete>', '_Delete')                  ## Close Window shortcut
        installationWindow.bind('<Insert>', '_Insert')                  ## Confirm Window shortcut
        installationWindow['doneButton'].Widget.config(cursor="hand2")  ## Done Button Hover icon
        while True:
            event, values = installationWindow.read()
            if event == sg.WIN_CLOSED or event == 'doneButton' or (event == '_Delete') or (event == '_Insert'): ## Window Closed
                if (os.path.dirname(__file__)).split("\\")[-1] == systemName.replace(" ", "-") + "-main": shutil.rmtree(os.path.dirname(__file__))
                else: os.remove(__file__)
                exit()
    elif recommendedBranch != "": systemBuild = recommendedBranch ## Set Default to Recommended
    else: systemBuild = availableBranches[0] ## Set Default to First Branch
    ## Interface Creator
    layout = [[sg.Text(systemName+" Installer", font=("Helvetica", 18))],
              [sg.Text("Install program to:", font=("Helvetica", 12), key='installProgramText'), sg.InputText(installLocation, size=(60, 20), key='installLocation'), sg.FolderBrowse(target='installLocation', key='folderBrowserButton')],
              [sg.Text("Build:", font=("Helvetica", 12), key='buildText'), sg.Combo(availableBranches, default_value=systemBuild, key='buildInput')],
              [sg.Text("Desktop Shortcut?", font=("Helvetica", 12), key='desktopShortcutText'), sg.Checkbox("", default=True, key='desktopShortcutCheckbox')],
              [sg.Column([[]], size=(1,30))], [sg.Button("Start Install", button_color=('White', 'Green'), key='startInstallButton')],
              [sg.Text(installText + "...", key='installText', font=("Ariel", 12), visible=False)], [sg.ProgressBar(50, orientation='h', size=(20, 10), border_width=4, key='progbar', bar_color=['Green','White'], visible=False)],
              [sg.Column([[]], size=(1,130))],
              [sg.Column([[sg.Text(platform.system() + " " + platform.release() + " | " + installerVersion + " | Online", key='homeBottomInfoText', font=('Any 13'), background_color=DARK_HEADER_COLOR), sg.Push(background_color=DARK_HEADER_COLOR), sg.Text("Oszust Industries", key='creditsTextHomeBottom', font=('Any 13'), background_color=DARK_HEADER_COLOR)], [sg.Column([[]], size=(700, 1), pad=(0,0), background_color=DARK_HEADER_COLOR)]], size=(700, 30), pad=(0,0), background_color=DARK_HEADER_COLOR)]]
    installationWindow = sg.Window(systemName + " Installer", layout, resizable=False, finalize=True, element_justification='c')
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0) ## Hide Console
    ## Window Shortcuts / Mouse Icon Changes
    installationWindow.bind('<Delete>', '_Delete')                               ## Close Window shortcut
    installationWindow['folderBrowserButton'].Widget.config(cursor="hand2")      ## Folder Browser Hover icon
    installationWindow['desktopShortcutCheckbox'].Widget.config(cursor="hand2")  ## Desktop Checkbox Hover icon
    installationWindow['startInstallButton'].Widget.config(cursor="hand2")       ## Start Install Button Hover icon
    ## Move Window to Center
    screen_width, screen_height = installationWindow.get_screen_dimensions()
    win_width, win_height = installationWindow.size
    x, y = (screen_width - win_width)//2, (screen_height - win_height)//2
    installationWindow.move(x, y)
    while True:
        event, values = installationWindow.read()
        if event == sg.WIN_CLOSED or (event == '_Delete'): exit() ## Window Closed
        elif event == 'startInstallButton': ## Start Install
            desktopShortcut, installLocation, systemBuild = values['desktopShortcutCheckbox'], values['installLocation'], values['buildInput']
            for key in ['buildInput' ,'buildText' ,'desktopShortcutCheckbox' ,'desktopShortcutText' ,'folderBrowserButton' ,'installLocation' ,'installProgramText' ,'startInstallButton' ]: installationWindow[key].update(visible=False) ## Hide Input Elements
            for key in ['installText', 'progbar']: installationWindow[key].update(visible=True) ## Show Installer Progress Elements
            break
    if systemBuild not in availableBranches: ## Check systemBuild
        installationWindow['installText'].update("Error.")
        sg.Popup("The requested build does not exist.", title="No App Build")
        installationWindow.close()
        setupInstall()
        return
    OszustOSSetupInstallerThread = threading.Thread(name='OszustOSSetupInstaller', target=OszustOSSetupInstaller)
    OszustOSSetupInstallerThread.start()
    while installStatus < 10 and errorCode == "":
        if installStatus != lastStatus:
            installationWindow['installText'].update(installText + "...")
            installationWindow['progbar'].UpdateBar(installStatus, 10)
            lastStatus = installStatus
    if errorCode == "No_Internet": crashMessage("Error 07: There doesn't seem to be any internet connection on your device.") ## No Internet Connection
    elif errorCode == "Packages_Failed": crashMessage("Error 08: A required package failed to install.") ## Required Package Failed to Install
    installationWindow['installText'].update("Done.")
    installationWindow['progbar'].UpdateBar(10, 10)
    installationWindow.close() ## Close Main Install Window
    installationWindowFinish = sg.Window("Installer - FINISH", [[sg.Text(systemName + " has finished installing!", font=("Helvetica", 14))], [sg.Button("Done", button_color=('White', 'Green'), key='doneButton')], [sg.Column([[]], size=(1,60))], [sg.Column([[sg.Push(background_color=DARK_HEADER_COLOR), sg.Text("Oszust Industries", key='creditsTextHomeBottom', font=('Any 13'), background_color=DARK_HEADER_COLOR), sg.Push(background_color=DARK_HEADER_COLOR)], [sg.Column([[]], size=(410, 1), pad=(0,0), background_color=DARK_HEADER_COLOR)]], size=(410, 30), pad=(0,0), background_color=DARK_HEADER_COLOR)]], size=(410, 180), resizable=False, finalize=True, element_justification='c')
    ## Window Shortcuts / Mouse Icon Changes
    installationWindowFinish.bind('<Delete>', '_Delete')      ## Close Window shortcut
    installationWindowFinish.bind('<Insert>', '_Insert')      ## Confirm Window shortcut
    installationWindowFinish['doneButton'].Widget.config(cursor="hand2")  ## Done Button Hover icon
    while True:
        event, values = installationWindowFinish.read()
        if event == sg.WIN_CLOSED or event == 'doneButton' or (event == '_Delete') or (event == '_Insert'): ## Window Closed
            try:
                if (os.path.dirname(__file__)).split("\\")[-1] == systemName.replace(" ", "-") + "-main": shutil.rmtree(os.path.dirname(__file__), ignore_errors=False) ## Check if in GitHub Folder
                else: os.remove(__file__) ## Not in GitHub Folder
            except:
                for i in next(os.walk(os.path.dirname(__file__)), (None, None, []))[2]: ## Delete Each File/Folder in Installer Folder
                    try: os.remove(os.path.dirname(__file__) + "\\" + i) ## Delete File
                    except: shutil.rmtree(os.path.dirname(__file__) + "\\" + i) ## Delete Folder
                    finally: pass
            exit()

def OszustOSSetupInstaller():
    global errorCode, installStatus, installText
    installStatus, installText = 1, "Checking Internet"
    try: urllib.request.urlopen("http://google.com", timeout=3) ## Test Internet
    except:
        errorCode = "No_Internet"
        return
    installStatus, installText = 2, "Creating Save Location"
    startMenuFolderLocation, systemNameDownload, systemNameFile, tempDownloadFolder = "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs", systemName.replace(" ", "_"), systemName.replace(" ", "-"), os.getenv('APPDATA') + "\\Oszust Industries"
## Create Folders in Appdata
    pathlib.Path(tempDownloadFolder + "\\" + systemName).mkdir(parents=True, exist_ok=True) ## Create Folder in Appdata for Program
    pathlib.Path(tempDownloadFolder + "\\temp").mkdir(parents=True, exist_ok=True)          ## Create Temp Folder
## Create Installation Folder
    if os.path.exists(installLocation): shutil.rmtree(installLocation) ## Remove Current Folder
    pathlib.Path(installLocation).mkdir(parents=True, exist_ok=True) ## Create Parents and Install Location
    os.system('ICACLS "'+installLocation+'" /grant Users:(OI)(CI)F /T') ## Give Write Permission
## Download Update
    installStatus, installText = 3, "Downloading"
    urllib.request.urlretrieve("https://github.com/Oszust-Industries/" + systemNameFile + "/archive/refs/heads/" + systemBuild + ".zip", (tempDownloadFolder + "\\temp\\" + systemNameDownload + ".zip"))
    installStatus, installText = 5, "Extracting Files"
    with zipfile.ZipFile(tempDownloadFolder + "\\temp\\" + systemNameDownload + ".zip", 'r') as zip_ref: zip_ref.extractall(tempDownloadFolder + "\\temp")
    os.remove(tempDownloadFolder + "\\temp\\" + systemNameDownload + ".zip")
    try: shutil.rmtree(tempDownloadFolder + "\\temp\\" + systemNameFile + "-Main") ## Remove temp folder if already there
    except: pass
    if systemBuild.lower() != "main": os.rename(tempDownloadFolder + "\\temp\\" + systemNameFile + "-" + systemBuild, tempDownloadFolder + "\\temp\\" + systemNameFile + "-Main")
## Move Required Files
    try: shutil.move(tempDownloadFolder + "\\temp\\" + systemNameFile + "-Main\\data", installLocation)
    except: pass
    filenames = next(os.walk(tempDownloadFolder + "\\temp\\" + systemNameFile + "-Main"), (None, None, []))[2]
    for i in filenames:
        if i not in [".gitattributes", ".gitignore", systemName+".pyproj", systemName+".sln", systemName.replace(" ", "")+"Setup.py", "README.md"]: ## Blacklisted File List
            try: os.remove(installLocation + "\\" + i)
            except: pass
            shutil.move(tempDownloadFolder + "\\temp\\" + systemNameFile + "-Main\\" + i, installLocation)
## Create Shortcut
    installStatus, installText = 7, "Creating Shortcut"
    try: os.remove(startMenuFolderLocation + "\\Oszust Industries\\" + systemName + ".lnk") ## Delete Start Menu Shortcut
    except: pass
    try: Shortcut.delete(shortcut_name = systemName, desktop=True, start_menu=False) ## Delete Desktop Shortcut
    except: pass
    pathlib.Path(startMenuFolderLocation + "\\Oszust Industries").mkdir(parents=True, exist_ok=True) ## Create Shortcut Folder
    try:
        if desktopShortcut == True: Shortcut(shortcut_name = systemName, exec_path = installLocation + "\\" + systemNameDownload + ".py", description = "Oszust Industries - Radio Software", icon_path = installLocation + "\\data\\" + systemName.replace(" ", "_") + ".ico", desktop=True, start_menu=False) ## Desktop Shortcut
    except: pass
    try:
        shortcut = win32com.client.Dispatch('WScript.Shell').CreateShortCut(startMenuFolderLocation + "\\Oszust Industries\\" + systemName + ".lnk") ## Start Menu Shortcut
        shortcut.Targetpath = installLocation + "\\" + systemName.replace(" ", "_") + ".py"
        shortcut.IconLocation = installLocation + "\\data\\" + systemName.replace(" ", "_") + ".ico"
        shortcut.save()
    except: pass
## Install Required Packages
    installStatus, installText = 8, "Installing Required Packages"
    if installPackages() == "FAIL":
        errorCode = "Packages_Failed"
        return
    try:
        pathlib.Path(installLocation + "\\cache").mkdir(parents=True, exist_ok=True) ## Create Cache Folder
        try: os.remove(installLocation + "\\cache\\updater.p") ## Delete Old Log
        except: pass
        pickle.dump(1, open(installLocation + "\\cache\\updater.p", "wb"))
    except: pass
## Clean Update
    installStatus, installText = 9, "Finishing Setup"
    shutil.rmtree(tempDownloadFolder + "\\temp")
    try: pickle.dump(str(datetime.datetime.now()).split(".")[0], open(installLocation + "\\releaseDate.p", "wb"))
    except: pass
    installStatus, installText = 10, "Done"

def installPackages():
    ## Install/Update Required Packages
    packagesList = ["billboard.py", "cloudscraper", "eyed3", "geocoder", "Pillow", "psutil", "PySimpleGUI", "pycrosskit", "requests"]
    try:
        subprocess.run(['py -m pip install --upgrade pip setuptools > /dev/null'], check=True)
        for package in packagesList: os.system('py -m pip install ' + package + ' > /dev/null')
    except:
        try:
            os.system('pip install pywin32 -q')
            for package in packagesList: os.system('pip install ' + package + ' -q')
        except: return "FAIL"


## Start System
try:
    if ctypes.windll.shell32.IsUserAnAdmin(): setupInstall()
    else: ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
except Exception as Argument: crashMessage("Error 00: " + str(Argument))