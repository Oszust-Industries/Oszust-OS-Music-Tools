## Oszust OS AutoUpdater - v4.0.0 (4.30.24) - Oszust Industries
import datetime, json, os, pathlib, pickle, requests, shutil, subprocess, threading, urllib.request, zipfile, webbrowser
import PySimpleGUI as sg

def setupUpdate(systemName, systemBuild, softwareVersion, newestVersion):
    if systemBuild.lower() in ["dev", "main"]: return ## STOPS THE UPDATER
    if os.name not in ["nt"]: return "Update Failed: (Not supported platform)" ## Platform isn't Windows
    ## Setup Thread and Return to Main App
    global loadingStatus, loadingStep
    loadingPopup, loadingStatus, loadingStep = sg.Window("", [[sg.Text("Installing " + systemName, font='Any 16', background_color='#1b2838', key='updaterTitleText')], [sg.Text(newestVersion, font='Any 16', background_color='#1b2838', key='updaterVersionText')], [sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", background_color='#1b2838', key='updaterGIFImage')], [sg.Text("Starting Updater...", font='Any 16', background_color='#1b2838', key='updaterText')], [sg.Text("Step 0 of 6", font='Any 14', background_color='#1b2838', key='updaterStepText')], [sg.Button("Ok", font='Any 16', visible=False, key='doneButton')]], background_color='#1b2838', element_justification='c', no_titlebar=True, keep_on_top=True), "Starting Updater...", 0
    loadingPopup["updaterGIFImage"].UpdateAnimation(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", time_between_frames=10) ## Load Loading GIF
    while True:
        event, values = loadingPopup.read(timeout=10)
        try: loadingPopup["updaterGIFImage"].UpdateAnimation(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", time_between_frames=30) ## Load Loading GIF
        except: pass
        loadingPopup["updaterText"].update(loadingStatus)
        loadingPopup["updaterStepText"].update("Step " + str(loadingStep) + " of 6")
        if event == sg.WIN_CLOSED: exit()
        elif loadingStatus == "Starting Updater...":
                OszustOSAutoUpdaterThread = threading.Thread(name="OszustOSAutoUpdater", target=OszustOSAutoUpdater, args=(systemName, systemBuild, softwareVersion, newestVersion,))
                OszustOSAutoUpdaterThread.start()
                "Checking Internet..." 
        elif loadingStatus == "Done": loadingPopup['doneButton'].update(visible=True)
        elif event == 'doneButton':
            loadingPopup.close()
            break

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
        event, values = errorWindow.read()
        if event == sg.WIN_CLOSED or event == 'Quit' or (event == '_Delete'): exit()
        elif event == 'Report' or (event == '_Insert'): webbrowser.open("https://github.com/Oszust-Industries/" + systemName.replace(" ", "-") + "/issues/new", new=2, autoraise=True)
        elif event in RightClickMenu[1]: ## Right Click Menu Actions
            try:
                if event == 'Copy': ## Copy Lyrics Text
                    try:
                        errorWindow.TKroot.clipboard_clear()
                        errorWindow.TKroot.clipboard_append(errorLine.Widget.selection_get())
                    except: pass
            except: pass

def OszustOSAutoUpdater(systemName, systemBuild, softwareVersion, newestVersion):
    global updateStatus
    
    return

    ## Update Statuses: -5 - API Limit, -4 - Invalid Commit Name, -3 - No AppBuild, -2 - No Internet, 0 - None, 1 - Normal Update, 2 - Hotfix, 3 - Emergency
    try: urllib.request.urlopen("http://google.com", timeout=3) ## Test Internet
    except:
        updateStatus = -2
        return "No Internet"
    ## Get GitHub Branches
    resp = requests.get("https://api.github.com/repos/Oszust-Industries/" + systemName.replace(" ", "-") + "/branches")
    content = json.loads((resp.content).decode('utf8'))
    try:
        if "API rate limit exceeded" in content["message"]: ## Too Many API Calls
            updateStatus = -5
            return "API Limit"
    except: pass
    for branch in range(len(content)):
        if content[branch]["protected"] == False and content[branch]["name"].lower() not in ["dev", "devTesting","main"]: availableBranches.append(content[branch]["name"]) ## Builds that Aren't Protected
    try: ## Start Main Update System
        current, systemNameDownload, systemNameFile, tempDownloadFolder = str(pathlib.Path(__file__).resolve().parent), systemName.replace(" ", "_"), systemName.replace(" ", "-"), os.getenv('APPDATA') + "\\Oszust Industries"
        if systemBuild in availableBranches:
            ## Get Newest Commit Name
            resp = requests.get("https://api.github.com/repos/Oszust-Industries/" + systemName.replace(" ", "-") + "/commits/" + systemBuild)
            content = json.loads((resp.content).decode('utf8'))
            newestVersion = (content["commit"]["message"]).split(' (', 1)[0]
            if newestVersion[0] != "v" and "pull request" not in newestVersion:
                updateStatus = -4
                return "Invalid Commit Name"
            elif "pull request" in newestVersion:
                newestVersion = newestVersion.rsplit('\n', 1)[1] ## Remove Pull Request Text
                if newestVersion[0] != "v":
                    updateStatus = -4
                    return "Invalid Commit Name"
        else:
             updateStatus = -3
             return "No AppBuild"
        if newestVersion != appVersion or forceReinstallation == True:
        ## Create Temp Folder for Update in Appdata
            if os.path.exists(tempDownloadFolder) == False: os.mkdir(tempDownloadFolder)
            if os.path.exists(tempDownloadFolder + "\\temp") == False: os.mkdir(tempDownloadFolder + "\\temp")
            else:
                shutil.rmtree(tempDownloadFolder + "\\temp")
                os.mkdir(tempDownloadFolder + "\\temp")
        ## Download Update
            urllib.request.urlretrieve("https://github.com/Oszust-Industries/" + systemNameFile + "/archive/refs/heads/" + systemBuild + ".zip", (tempDownloadFolder + "\\temp\\" + systemNameDownload + ".zip"))
            with zipfile.ZipFile(tempDownloadFolder + "\\temp\\" + systemNameDownload + ".zip", 'r') as zip_ref: zip_ref.extractall(tempDownloadFolder + "\\temp")
            os.remove(tempDownloadFolder + "\\temp\\" + systemNameDownload + ".zip")
            if systemBuild.lower() != "main": os.rename(tempDownloadFolder + "\\temp\\" + systemNameFile + "-" + systemBuild, tempDownloadFolder + "\\temp\\" + systemNameFile + "-Main")
        ## Update Required Files
            try: shutil.rmtree(current + "\\data")
            except: pass
            try: shutil.move(tempDownloadFolder + "\\temp\\" + systemNameFile + "-Main\\data", current)
            except: pass
            filenames = next(os.walk(tempDownloadFolder + "\\temp\\" + systemNameFile + "-Main"), (None, None, []))[2]
            for i in filenames:
                if i not in [".gitattributes", ".gitignore", systemName+".pyproj", systemName+".sln", systemName.replace(" ", "")+"Setup.py", "README.md"]:
                    try: os.remove(current + "\\" + i)
                    except: pass
                    shutil.move(tempDownloadFolder + "\\temp\\" + systemNameFile + "-Main\\" + i, current)
        ## Clean Update
            shutil.rmtree(tempDownloadFolder + "\\temp")
            try: pickle.dump(str(datetime.datetime.now()).split(".")[0], open(str(pathlib.Path(__file__).resolve().parent) + "\\releaseDate.p", "wb"))
            except: pass
            try: ## Changelog File
                releaseInfo = json.loads(urllib.request.urlopen(f"https://api.github.com/repos/Oszust-Industries/" + systemName.replace(" ", "-") + "/releases?per_page=1").read().decode())
                pickle.dump(str(releaseInfo[:1][0]['body']), open(str(pathlib.Path(__file__).resolve().parent) + "\\" + releaseInfo[:1][0]['tag_name'] + "_changelog.p", "wb"))
            except: pass
            updateStatus = 1
        else: updateStatus = 0
    except Exception as Argument: print("Update Failed: (" + str(Argument) + ")")


## Start System
def main(systemName, systemBuild, softwareVersion, newestVersion):
    try: setupUpdate(systemName, systemBuild, softwareVersion, newestVersion)
    except Exception as Argument: print("Error 00: " + str(Argument))
    input("Press enter to close the window. >")