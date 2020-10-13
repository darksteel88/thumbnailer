def log_skipping(verbose, video):
    if verbose:
        print("Skipping file {}".format(video))

def log_global_timer(verbose, start, end):
    if verbose:
        print("Total processing took {} seconds".format((end-start).seconds))

def log_individual_timer(verbose, f, start, end):
    if verbose:
        print("Processing of {} took {} seconds".format(f, (end-start).seconds))

def log_counter(verbose, counter, num_files, video):
    if verbose:
        print("File {} of {}: {}".format(counter, num_files, video))