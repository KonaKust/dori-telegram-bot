from logs.watcher import LogFileWatcher


def main():
    watcher = LogFileWatcher(
        redis_key="factorio_log_position",
        log_file_path="/srv/factorio",
        file_name="factorio.log",
        target_words=["JOIN", "LEAVE"],
        ignored_words=["KonaKust"],
    )
    watcher.start_observer()


if __name__ == "__main__":
    main()
