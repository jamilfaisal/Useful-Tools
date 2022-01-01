interface_messages = dict(
    main_interface="\n1. Add Episodes\n2. Display Database\n3. Import\n4. Export\n5. Autosave\n6. Exit",
)

user_input_messages = dict(
    main_interface="Enter option: ",
    enter_episode_format="Enter:  (Format: SEASON EPISODE - TITLE) (TITLE is optional) (enter 'q' to go back)\n",
    enter_export_file_name="Enter file name: "
)

error_messages = dict(
    invalid_choice="Please enter a valid choice!",
    invalid_entry="Enter a valid entry!",
    import_fail="Import failure!",
    export_fail="Export failure!"
)

information_messages = dict(
    no_episodes_found="No episodes entered!",
    import_success="Import successful!",
    export_success="Export successful!"
)
