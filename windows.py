import PySimpleGUI as sg
import pandas as pd
import perfonitor.calculations as calculations
import perfonitor.data_acquisition as data_acquisition
import perfonitor.data_treatment as data_treatment
import perfonitor.file_creation as file_creation
import perfonitor.inputs as inputs
import event_tracker.event_tracker_manager as event_tracker_manager
import os
from itertools import compress

# <editor-fold desc="ET Functions">

def collapse(layout, key, visible):
    """
    Helper function that creates a Column that can be later made hidden, thus appearing "collapsed"
    :param layout: The layout for the section
    :param key: Key used to make this section visible / invisible
    :param visible: visible determines if section is rendered visible or invisible on initialization
    :return: A pinned column that can be placed directly into your layout
    :rtype: sg.pin
    """
    return sg.pin(sg.Column(layout, key=key, visible=visible, pad=(0,0)))


def process_selection(geofolder_path, geography, site_list, pre_selection, pre_selection_path):
    sg.theme('DarkAmber')  # Add a touch of color
    # All the stuff inside your window.
    layout = [[sg.Text('Welcome to the GP&M tool-kit, what do you want to do?', pad=((2, 10), (2, 5)))],
              [sg.Button('Daily monitoring report'), sg.Push()],
              [sg.Button('Event tracker manager'), sg.Push()],
              [sg.Button('Curtailment calculation'), sg.Push()],
              [sg.Button('Clipping calculation'), sg.Push()],
              [sg.Push(), sg.Exit()]]

    # Create the Window
    window = sg.Window('LSbp GP&M tool-kit', layout)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read(timeout=100)

        if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks exit
            break
        if event == 'Daily monitoring report':
            daily_monitoring_report(site_list, pre_selection, geography, pre_selection_path)

        if event == 'Event tracker manager':
            event_tracker_manager.main()

    window.close()
    return


def daily_monitoring_report(site_list, pre_selection, geography, pre_selection_path):
    sg.theme('DarkAmber')  # Add a touch of color
    # All the stuff inside your window.
    options_layout = [[sg.Text('Welcome to the DMR tool, what do you want to do?', pad=((2, 10), (2, 5)))],
                      [sg.Button('Create Incidents List')],
                      [sg.Button('Create final report')],
                      [sg.Exit()]]

    sites_layout = [[sg.Checkbox(site, size=(20, 1), default=site in pre_selection,
                                 key=site.replace(" ","_"))] for site in site_list]

    layout = [[sg.Column(options_layout),
               sg.VSeperator(),
               sg.Column(sites_layout, scrollable=True)]]

    # Create the Window
    window = sg.Window('Daily Monitoring Report', layout)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read(timeout=100)

        if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks exit
            break
        if event == 'Create Incidents List':
            site_selection = list(compress(site_list, list(values.values())))
            print("You selected: \n", site_selection)
            pd.DataFrame(site_selection).to_csv(pre_selection_path, header=None, index=None, sep=' ', mode='a')

            incidents_file, tracker_incidents_file, geography, date, df_component_code = \
                file_creation.dmrprocess1(site_selection)

        if event == 'Create final report':
            try:
                dmr_report = file_creation.dmrprocess2_new(incidents_file, tracker_incidents_file, site_selection,
                                                           geography, date)

            except NameError:
                dmr_report = file_creation.dmrprocess2_new()

            if dmr_report:
                event, values = sg.Window('Choose an option', [[sg.Text('Process complete, open file?')],
                                                               [sg.Button('Yes'), sg.Button('Cancel')]]).read(
                    close=True)

                if event == 'Yes':
                    command = 'start "EXCEL.EXE" "' + str(dmr_report) + '"'
                    os.system(command)
                    break
                else:
                    break

    window.close()



    return


def update_event_tracker():
    sg.theme('DarkAmber')  # Add a touch of color
    # All the stuff inside your window.

    end_date_calendar_section = [[sg.Text('Enter end date of period you want to add', pad=((2, 10), (2, 5)))],
                                 [sg.CalendarButton('Choose date', target='-ECAL-', format="%Y-%m-%d"),
                                  sg.In(key='-ECAL-', text_color='black', size=(16, 1), enable_events=True,
                                        readonly=True, visible=True)]]

    layout = [[sg.Text('Enter date of report you want to add', pad=((2, 10), (2, 5)))],
              [sg.CalendarButton('Choose date', target='-SCAL-', format="%Y-%m-%d"),
               sg.In(key='-SCAL-', text_color='black', size=(16, 1), enable_events=True, readonly=True, visible=True),
               sg.Checkbox('Multiple reports', enable_events=True, size=(13, 1), key='chk_multr')],
              [collapse(end_date_calendar_section, '-EXCAL-', False)],
              [sg.Text('Choose Event Tracker to update', pad=((0, 10), (10, 2)))],
              [sg.FileBrowse(target='-ETFILE-'),
               sg.In(key='-ETFILE-', text_color='black', size=(20, 1), enable_events=True, readonly=True,
                     visible=True)],
              [sg.Text('Choose location folder of DMRs', pad=((0, 10), (10, 2)))],
              [sg.FolderBrowse(target='-DMRFOLDER-'),
               sg.In(key='-DMRFOLDER-', text_color='black', size=(20, 1), enable_events=True, readonly=True,
                     visible=True)],
              [sg.Text('Enter geography ', pad=((0, 10), (10, 2))), sg.Push(),
               sg.Checkbox('Update All Export\n& Irradiance', default=True, enable_events=True, size=(13, 3),
                           pad=((20, 0), (0, 10)), key='chk_updt')],
              [sg.Combo(['AUS', 'ES', 'USA'], size=(4, 3), readonly=True, key='-GEO-', pad=((5, 10), (2, 10))),
               sg.Push(), sg.Checkbox('Recalculate All', enable_events=True, size=(13, 3), pad=((20, 0), (0, 10)),
                                      key='chk_recalc')],
              [sg.Button('Submit'), sg.Exit()]]

    # Create the Window
    window = sg.Window('Update Event Tracker', layout)

    toggle_sec1 = False
    toggle_updt = True
    toggle_recalc = False

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read(timeout=100)

        if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks exit
            window.close()
            return "None", "None", "None", "None", "None", "None", "None"

        if event == 'chk_multr':
            toggle_sec1 = not toggle_sec1
            window['-EXCAL-'].update(visible=toggle_sec1)

        if event == 'chk_updt':
            toggle_updt = not toggle_updt

        if event == 'chk_recalc':
            toggle_recalc = not toggle_recalc

        if event == 'Submit':
            date_start = values['-SCAL-']  # date is string
            date_end = values['-ECAL-']
            event_tracker_path = values['-ETFILE-']
            dmr_folder = values['-DMRFOLDER-']
            geography = values['-GEO-']

            if date_end == "":
                date_end = None
                print('date end value changed to none')
            if toggle_sec1 is False:
                date_end = None
            window.close()
            return date_start, date_end, event_tracker_path, dmr_folder, geography, toggle_updt, toggle_recalc

    # window.close()

    return


def event_tracker():
    username = os.getlogin()

    sg.theme('DarkAmber')  # Add a touch of color
    # All the stuff inside your window.

    layout = [[sg.Text('Choose the source of information:', pad=((2, 10), (2, 5)))],
              [sg.Radio('Database', group_id="source", disabled=True, default=False, key="-SRCDB-"),
               sg.Radio('Event Tracker file', group_id="source", default=True, key="-SRCFILE-")],
              [sg.Text('Select source on Desktop', pad=((0, 10), (10, 2)))],
              [sg.FolderBrowse(target='-SRCFOLDER-',
                               initial_folder="C:/Users/" + username + "/OneDrive - Lightsource BP/Desktop"),
               sg.In(key='-SRCFOLDER-', text_color='black', size=(20, 1), enable_events=True, readonly=True,
                     visible=True)],
              [sg.Text('Enter geography ', pad=((0, 10), (10, 2))), sg.Push()],
              [sg.Combo(['AUS', 'ES', 'USA'], size=(4, 3), readonly=True, key='-GEO-', pad=((5, 10), (2, 10))),
               sg.Push(), sg.Checkbox('Recalculate All', enable_events=True, size=(13, 3), pad=((20, 0), (0, 10)),
                                      key='chk_recalc')],
              [sg.Button('Submit'), sg.Exit()]]

    # Create the Window
    window = sg.Window('Event Tracker', layout)

    #toggle_sec1 = False
    #toggle_updt = True
    toggle_recalc = False

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read(timeout=100)

        if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks exit
            window.close()
            return "None", "None", "None", "None"

        if event == 'chk_recalc':
            toggle_recalc = not toggle_recalc

        if event == 'Submit':

            source_folder = values['-SRCFOLDER-']
            geography = values['-GEO-']
            geopgraphy_folder = source_folder + "/" + geography

            for key in values.keys():
                if "SRC" in key and values[key] == True:
                    if "FILE" in key:
                        source_type = "file"
                    elif "DB" in key:
                        source_type = "database"

            return source_folder, geography, geopgraphy_folder, toggle_recalc

    window.close()

    return


def underperformance_report():
    username = os.getlogin()

    sg.theme('DarkAmber')  # Add a touch of color
    # All the stuff inside your window.

    month_calendar_section = [[sg.Text('Enter month of analysis', pad=((2, 10), (2, 5)))],
                              [sg.CalendarButton('Choose date', target='-ECAL-', format="%Y-%m-%d"),
                               sg.In(key='-SCAL-', text_color='black', size=(16, 1), enable_events=True,
                                     readonly=True, visible=True)]]

    custom_calendar_section = [[sg.Text('Enter start date of period you want to analyse', pad=((2, 10), (2, 5)))],
                               [sg.CalendarButton('Choose date', target='-SCAL-', format="%Y-%m-%d"),
                                sg.In(key='-SCAL-', text_color='black', size=(16, 1), enable_events=True,
                                      readonly=True, visible=True)],
                               [sg.Text('Enter end date of period you want to analyse', pad=((2, 10), (2, 5)))],
                               [sg.CalendarButton('Choose date', target='-ECAL-', format="%Y-%m-%d"),
                                sg.In(key='-ECAL-', text_color='black', size=(16, 1), enable_events=True,
                                      readonly=True, visible=True)]]

    layout = [[sg.Text('Choose the source of information:', pad=((2, 10), (2, 5)))],
              [sg.Radio('Month', group_id="period", default=False, key="-PERMON-"),
               sg.Radio('Choose', group_id="period", default=True, key="-PERCHO-")],
              [sg.Text('Choose the period of analysis:', pad=((2, 10), (2, 5)))],
              [sg.Radio('Database', group_id="source", disabled=True, default=False, key="-SRCDB-"),
               sg.Radio('Event Tracker file', group_id="source", default=True, key="-SRCFILE-")],
              [sg.Text('Select source on Desktop', pad=((0, 10), (10, 2)))],
              [sg.FolderBrowse(target='-SRCFOLDER-',
                               initial_folder="C:/Users/" + username + "/OneDrive - Lightsource BP/Desktop"),
               sg.In(key='-SRCFOLDER-', text_color='black', size=(20, 1), enable_events=True, readonly=True,
                     visible=True)],
              [sg.Text('Enter geography ', pad=((0, 10), (10, 2))), sg.Push()],
              [sg.Combo(['AUS', 'ES', 'USA'], size=(4, 3), readonly=True, key='-GEO-', pad=((5, 10), (2, 10))),
               sg.Push(),
               sg.Checkbox('Recalculate All', enable_events=True, size=(13, 3), pad=((20, 0), (0, 10)),
                           key='chk_recalc')],
              [sg.Text('Select level of analysis', pad=((0, 10), (10, 2))), sg.Push(),
               sg.Text('Select Irradiance Threshold', pad=((0, 10), (10, 2))), sg.Push()],
              [sg.Combo(['All', 'Inverter level', 'Inverter only'], default_value="All", size=(11, 3), readonly=True,
                        key='-LVL-', pad=((5, 10), (2, 10))),
               sg.Combo([20, 50, 85, 100], default_value=50, size=(11, 3), readonly=True, key='-THR-',
                        pad=((50, 10), (2, 10)))],
              [sg.Button('Submit'), sg.Exit()]]

    # Create the Window
    window = sg.Window('Event Tracker', layout)

    #toggle_sec1 = False
    #toggle_updt = True
    toggle_recalc = False

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read(timeout=100)

        if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks exit
            break

        if event == 'chk_recalc':
            toggle_recalc = not toggle_recalc

        if event == 'Submit':

            source_folder = values['-SRCFOLDER-']
            level = values['-LVL-']
            irradiance_threshold = values['-THR-']
            geography = values['-GEO-']
            geopgraphy_folder = source_folder + "/" + geography

            for key in values.keys():
                if "SRC" in key and values[key] is True:
                    if "FILE" in key:
                        source_type = "file"
                    elif "DB" in key:
                        source_type = "database"

                elif "PER" in key and values[key] is True:
                    if "CHO" in key:
                        period_list = ["choose"]
                    elif "MON" in key:
                        period_list = ["monthly"]

            return source_folder, geography, geopgraphy_folder, toggle_recalc, period_list, level, irradiance_threshold

    window.close()

    return


def mondaycom_file():
    sg.theme('DarkAmber')  # Add a touch of color
    # All the stuff inside your window.

    end_date_calendar_section = [[sg.Text('Enter end date of period you want to add', pad=((2, 10), (2, 5)))],
                                 [sg.CalendarButton('Choose date', target='-ECAL-', format="%Y-%m-%d"),
                                  sg.In(key='-ECAL-', text_color='black', size=(16, 1), enable_events=True,
                                        readonly=True, visible=True)]]

    layout = [[sg.Text('Enter date of report you want to add', pad=((2, 10), (2, 5)))],
              [sg.CalendarButton('Choose date', target='-SCAL-', format="%Y-%m-%d"),
               sg.In(key='-SCAL-', text_color='black', size=(16, 1), enable_events=True, readonly=True, visible=True),
               sg.Checkbox('Multiple reports', enable_events=True, size=(13, 1), key='chk_multr')],
              [collapse(end_date_calendar_section, '-EXCAL-', False)],
              [sg.Text('Choose location folder of Event Tracker', pad=((0, 10), (10, 2)))],
              [sg.FolderBrowse(target='-ETFOLDER-'),
               sg.In(key='-ETFOLDER-', text_color='black', size=(20, 1), enable_events=True, readonly=True,
                     visible=True)],
              [sg.Text('Enter geography ', pad=((0, 10), (10, 2))), sg.Push()],
              [sg.Combo(['AUS', 'ES', 'USA'], size=(4, 3), readonly=True, key='-GEO-', pad=((5, 10), (2, 10))),
               sg.Push()],
              [sg.Button('Submit'), sg.Exit()]]

    # Create the Window
    window = sg.Window('Monday.com files', layout)

    toggle_sec1 = False

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read(timeout=100)

        if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks exit
            window.close()
            return "None", "None", "None", "None"
            break
        if event == 'chk_multr':
            toggle_sec1 = not toggle_sec1
            window['-EXCAL-'].update(visible=toggle_sec1)

        if event == 'Submit':
            date_start = values['-SCAL-']  # date is string
            date_end = values['-ECAL-']
            event_tracker_folder = values['-ETFOLDER-']
            geography = values['-GEO-']

            if date_end == "":
                date_end = date_start
            if toggle_sec1 == False:
                date_end = date_start

            return date_start, date_end, event_tracker_folder, geography,

            window.close()

    window.close()

    return

# </editor-fold>



