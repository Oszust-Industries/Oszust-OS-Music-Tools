## Oszust OS AutoUpdater - v4.0.0 (5.01.24) - Oszust Industries
import datetime, json, os, pathlib, pickle, requests, shutil, subprocess, threading, urllib.request, zipfile, webbrowser
import PySimpleGUI as sg

def setupUpdate(systemName, systemBuild, softwareVersion, newestVersion):
    if systemBuild.lower() in ["dev", "main"]: return ## STOPS THE UPDATER
    if os.name not in ["nt"]: return "Update Failed: (Not supported platform)" ## Platform isn't Windows
    ## Setup Thread and Return to Main App
    global loadingStatus, loadingStep
    loadingPopup, loadingStatus, loadingStep = sg.Window("", [[sg.Text("Installing " + systemName, font='Any 16', background_color='#1b2838', key='updaterTitleText')], [sg.Text(newestVersion, font='Any 16', background_color='#1b2838', key='updaterVersionText')], [sg.Image(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", background_color='#1b2838', key='updaterGIFImage')], [sg.Text("Starting Updater...", font='Any 16', background_color='#1b2838', key='updaterText')], [sg.Text("Step 0 of 7", font='Any 14', background_color='#1b2838', key='updaterStepText')], [sg.Button("Ok", font='Any 16', visible=False, key='doneButton')]], background_color='#1b2838', element_justification='c', no_titlebar=True, keep_on_top=True), "Starting Updater...", 0
    loadingPopup["updaterGIFImage"].UpdateAnimation(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", time_between_frames=10) ## Load Loading GIF
    while True:
        event, values = loadingPopup.read(timeout=10)
        try: loadingPopup["updaterGIFImage"].UpdateAnimation(str(pathlib.Path(__file__).resolve().parent) + "\\data\\loading.gif", time_between_frames=30) ## Load Loading GIF
        except: pass
        loadingPopup["updaterText"].update(loadingStatus)
        loadingPopup["updaterStepText"].update("Step " + str(loadingStep) + " of 7")
        if event == sg.WIN_CLOSED: exit()
        elif loadingStatus == "Starting Updater...":
                OszustOSAutoUpdaterThread = threading.Thread(name="OszustOSAutoUpdater", target=OszustOSAutoUpdater, args=(systemName, systemBuild, softwareVersion, newestVersion,))
                OszustOSAutoUpdaterThread.start()
                loadingStatus, loadingStep = "Checking Internet...", 1
        elif loadingStatus == "Done":
            loadingPopup["updaterGIFImage"].update(visible=False)
            loadingPopup['doneButton'].update(visible=True)
        elif event == 'doneButton':
            loadingPopup.close()
            break

def crashMessage(message, systemName):
    RightClickMenu = ['', ['Copy']] ## Right Click Menu - Crash Message
    errorWindow = sg.Window(message.split(':')[0], [[sg.Text(systemName + " AutoUpdater has crashed.", font=("Any", 13))], [sg.Multiline(message, size=(50,5), font=("Any", 13), disabled=True, autoscroll=False, right_click_menu=RightClickMenu, key='crashMessageErrorCodeText')], [sg.Button("Report Error", button_color=("White", "Blue"), key='Report'), sg.Button("Quit", button_color=("White", "Red"), key='Quit')]], resizable=False, finalize=True, keep_on_top=True, element_justification='c')
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
                if event == 'Copy': ## Copy Error Text
                    try:
                        errorWindow.TKroot.clipboard_clear()
                        errorWindow.TKroot.clipboard_append(errorLine.Widget.selection_get())
                    except: pass
            except: pass

def OszustOSAutoUpdater(systemName, systemBuild, softwareVersion, newestVersion):
    global loadingStatus, loadingStep
    try: urllib.request.urlopen("http://google.com", timeout=3) ## Test Internet
    except: crashMessage("No Internet.", systemName)
    try: ## Start Main Update System
        current, loadingStatus, loadingStep, tempDownloadFolder = str(pathlib.Path(__file__).resolve().parent), "Checking Newest Version...", 2, os.getenv('APPDATA') + "\\Oszust Industries"
        try: newestVersion = ((requests.get("https://api.github.com/repos/Oszust-Industries/" + systemName.replace(" ", "-") + "/releases/latest")).json())['tag_name'] ## Get Newest Release Tag
        except: crashMessage("Bad API call was made to GitHub's releases.", systemName) ## Bad API Call
        if newestVersion != softwareVersion:
        ## Create Temp Folder for Update in Appdata
            loadingStatus, loadingStep = "Creating Temp Folder...", 3    
            if os.path.exists(tempDownloadFolder) == False: os.mkdir(tempDownloadFolder)
            if os.path.exists(tempDownloadFolder + "\\temp") == False: os.mkdir(tempDownloadFolder + "\\temp")
            else:
                shutil.rmtree(tempDownloadFolder + "\\temp")
                os.mkdir(tempDownloadFolder + "\\temp")
        ## Download Update
            loadingStatus, loadingStep = "Downloading Update...", 4
            urllib.request.urlretrieve("https://github.com/Oszust-Industries/" + systemName.replace(" ", "-") + "/archive/refs/heads/" + systemBuild + ".zip", (tempDownloadFolder + "\\temp\\" + systemName.replace(" ", "_") + ".zip"))
            with zipfile.ZipFile(tempDownloadFolder + "\\temp\\" + systemName.replace(" ", "_") + ".zip", 'r') as zip_ref: zip_ref.extractall(tempDownloadFolder + "\\temp")
            os.remove(tempDownloadFolder + "\\temp\\" + systemName.replace(" ", "_") + ".zip")
            if systemBuild.lower() != "main": os.rename(tempDownloadFolder + "\\temp\\" + systemName.replace(" ", "-") + "-" + systemBuild, tempDownloadFolder + "\\temp\\" + systemName.replace(" ", "-") + "-Main")
        ## Update Required Files
            loadingStatus, loadingStep = "Installing Update...", 5 
            try: shutil.rmtree(current)
            except: crashMessage("Unable to delete current files. You will have to remove them yourself.", systemName)
            try: shutil.move(tempDownloadFolder + "\\temp\\" + systemName.replace(" ", "-") + "-Main", current)
            except: crashMessage("Unable to copy update files. You will have to copy them yourself.", systemName)
        ## Clean Update
            loadingStatus, loadingStep = "Cleaning Update...", 6
            shutil.rmtree(tempDownloadFolder + "\\temp")
            try: ## Changelog File
                releaseInfo = json.loads(urllib.request.urlopen(f"https://api.github.com/repos/Oszust-Industries/" + systemName.replace(" ", "-") + "/releases?per_page=1").read().decode())
                pickle.dump(str(releaseInfo[:1][0]['body']), open(str(pathlib.Path(__file__).resolve().parent) + "\\" + releaseInfo[:1][0]['tag_name'] + "_changelog.p", "wb"))
            except: pass
        loadingStatus, loadingStep = "Done", 7 ## Update done or not needed
    except Exception as Argument: crashMessage(Argument, systemName)


## Start System
def main(systemName, systemBuild, softwareVersion, newestVersion):
    try: setupUpdate(systemName, systemBuild, softwareVersion, newestVersion)
    except Exception as Argument: print("AutoUpdater Error: " + str(Argument))
    input("Press enter to close the window. >")