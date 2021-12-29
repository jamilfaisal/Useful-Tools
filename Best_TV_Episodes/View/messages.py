interface_messages = dict(
    main_interface="\n1. Add Episodes\n2. Display Database\n3. Import\n4. Autosave\n5. Exit",
)

user_input_messages = dict(
    main_interface="Enter option: ",
    enter_episode_format="Enter:  (Format: SEASON EPISODE - TITLE) (TITLE is optional) (enter 'q' to go back)\n",
)

error_messages = dict(
    invalid_choice="Please enter a valid choice!",
    invalid_entry="Enter a valid entry!",
    import_fail="Import failure!"
)

information_messages = dict(
    no_episodes_found="No episodes entered!",
    import_success="Import successful!"
)
