class Messages:
    ADDED_TO_QUEUE = (
        "Your request has been added to the queue. If you have more than {per_user_process_count} "
        "ongoing processes, then this process will only start after one of them finishes."
    )
    MEDIA_MESSAGE_DELETED = "Why did you delete the file 😠, Now i cannot help you 😒."
    CANNOT_OPEN_FILE = "😟 Sorry! I cannot open the file."
    PROCESS_TIMEOUT = (
        "😟 Sorry! process failed due to timeout. Your process was "
        "taking too long to complete, hence cancelled."
    )
    TRACK_USER_ACTIVITY = "User id: `{chat_id}`"
    PROCESSING_REQUEST = "Processing your request, Please wait! 😴"
    SCREENSHOT_AT = "ScreenShot at {time}"
    SCREENSHOT_PROCESS_FAILED = "😟 Sorry! Screenshot generation failed possibly due to some infrastructure failure 😥."
    SCREENSHOT_PROCESS_SUCCESS = (
        "🤓 You requested {count} screenshots and "
        "{total_count} screenshots generated, "
        "Now starting to upload!"
    )
    PROCESS_UPLOAD_CONFIRM = (
        "Successfully completed process in {total_process_duration}\n\n"
        "If You find me helpful, please rate me [here](tg://resolve?domain=botsarchive&post=1206)."
    )
    WRONG_FORMAT = "Please follow the specified format"
    VIDEO_PROCESS_CAPTION = "Sample video. {duration}s from {start}"
    SCREENSHOTS_START = "😀 Generating screenshots!."

    SAMPLE_VIDEO_PROCESS_START = "😀 Generating Sample Video! This might take some time."
    SAMPLE_VIDEO_PROCESS_FAILED = "😟 Sorry! Sample video generation failed possibly due to some infrastructure failure 😥."
    SAMPLE_VIDEO_PROCESS_SUCCESS = (
        "🤓 Sample video was generated successfully!, Now starting to upload!"
    )
    SAMPLE_VIDEO_PROCESS_FAILED_GENERATION = (
        "stream link : {file_link}\n\n duration {sample_duration} sample video "
        "generation failed\n\n{ffmpeg_output}"
    )
    SAMPLE_VIDEO_PROCESS_OPEN_ERROR = (
        "stream link : {file_link}\n\nSample video requested\n\n{duration}"
    )

    SCREENSHOTS_PROGRESS = "😀 `{current}` of `{total}` generated!"
    MANUAL_SCREENSHOTS_OPEN_ERROR = (
        "stream link : {file_link}\n\nRequested manual screenshots\n\n{duration}"
    )
    MANUAL_SCREENSHOTS_NO_VALID_POSITIONS = (
        "😟 Sorry! None of the given positions where valid!"
    )
    MANUAL_SCREENSHOTS_VALID_PISITIONS_ABOVE_LIMIT = (
        "😟 Sorry! Only 10 screenshots can be generated. Found {valid_positions_count} "
        "valid positions in your request"
    )
    MANUAL_SCREENSHOTS_INVALID_POSITIONS_ALERT = (
        "Found {invalid_positions_count} invalid positions ({invalid_positions}).\n\n"
        "😀 Generating screenshots after ignoring these!."
    )
    MANUAL_SCREENSHOTS_FAILED_GENERATION = (
        "stream link : {file_link}\n\nmanual screenshots {raw_user_input}."
    )

    TRIM_VIDEO_INVALID_RANGE = "The range you provided is invalid!"
    TRIM_VIDEO_DURATION_ERROR = (
        "Please provide any range that's upto {max_duration}s."
        " Your requested range **{start}:{end}** is `{request_duration}s` long!"
    )
    TRIM_VIDEO_OPEN_ERROR = "stream link : {file_link}\n\ntrim video requested\n\n{start}:{end}\n\n{duration}"
    TRIM_VIDEO_RANGE_OUT_OF_VIDEO_DURATION = (
        "😟 Sorry! The requested range is out of the video's duration!."
    )
    TRIM_VIDEO_PROCESS_FAILED = (
        "😟 Sorry! video trimming failed possibly due to some infrastructure failure 😥."
    )
    TRIM_VIDEO_PROCESS_FAILED_GENERATION = "stream link : {file_link}\n\nVideo trim failed.\n\n{start}:{end}\n\n{ffmpeg_output}"
    TRIM_VIDEO_PROCESS_SUCCESS = (
        "🤓 Video trimmed successfully!, Now starting to upload!"
    )
    TRIM_VIDEO_START = "😀 Trimming Your Video! This might take some time."

    SCREENSHOTS_OPEN_ERROR = "stream link : {file_link}\n\nRequested screenshots: {num_screenshots}.\n\n{duration}"
    SCREENSHOTS_FAILED_GENERATION = (
        "stream link : {file_link}\n\n{num_screenshots} screenshots where requested "
        "and Screen shots where not generated."
    )

    MEDIAINFO_START = "Finding the media info, media info will be send here shortly!"
