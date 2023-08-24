def coordinate(runner_names, message, run_type):
    from ironforge.worker import process_message

    process_message(runner_names, message, run_type)
