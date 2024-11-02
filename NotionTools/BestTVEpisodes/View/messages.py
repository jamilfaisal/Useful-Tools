interface_messages = dict(
    main_interface_autosave_on="\n1. Add Episodes\n2. Display Database\n3. Import\n4. Export\n5. Turn Autosave "
                               "Off\n6. Exit",
    main_interface_autosave_off="\n1. Add Episodes\n2. Display Database\n3. Import\n4. Export\n5. Turn Autosave "
                                "On\n6. Exit "
)

user_input_messages = dict(
    main_interface="Enter option: ",
    enter_episode_format="Enter:  (Format: SEASON EPISODE - TITLE) (TITLE is optional) (enter 'q' to go back)\n",
    enter_export_file_name="Enter file name: ",
    enter_autosave_number_of_seconds="Enter the frequency of auto save (Minimum 5 seconds): "
)

error_messages = dict(
    invalid_choice="Please enter a valid choice!",
    invalid_entry="Enter a valid entry!",
    import_fail="No entries imported.",
    export_fail="Export failure!",
    invalid_file_path="Invalid file path selected!",
    autosave_fail="Failed to turn autosave on!",
    autosave_invalid_timer="Please enter a valid time in seconds."
)

information_messages = dict(
    no_episodes_found="No episodes entered!",
    import_success="Import successful!",
    export_success="Export successful!",
    autosave_turned_off="Autosave successfully turned off.",
    autosave_turned_on="Autosave successfully turned on."
)
