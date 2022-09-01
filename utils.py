# from moviepy.video import Vi
import os
# import threading


def merge_videos(video_clip_paths, output_path, method="compose", callback=None):

    from moviepy.editor import concatenate_videoclips, VideoFileClip
    clips = [VideoFileClip(clip) for clip in video_clip_paths]
    if method == 'reduce':
        min_height = min([c.h for c in clips])
        min_width = min([c.w for c in clips])

        clips = [c.resize(newsize=(min_width, min_height)) for c in clips]
        final_clip = concatenate_videoclips(clips)

    elif method == 'compose':

        final_clip = concatenate_videoclips(clips)
    # thread = threading.Thread(
    #     target=final_clip.write_videofile, args=(output_path,))
    # thread.start()

    final_clip.write_videofile(output_path)
    for cl in clips:
        cl.close()
    callback('completed merging files')


def extract_thumbnail(file, thumbnail_path):
    from ffmpeg import probe
    from ffmpeg import input as n
    probe = probe(file)
    duration = float(probe['streams'][0]['duration'])
    width = probe['streams'][0]['width']

    thmb = check_for_thumbnail(os.path.basename(file), thumbnail_path)
    if thmb:
        return duration
    thmb = os.path.join(
        thumbnail_path, os.path.basename(file) + "_thumbnail.jpg")
    good, err = (n(file).filter(
        'scale', width, -1).output(thmb, vframes=1).run())
    return duration


def check_for_thumbnail(name, path):
    thmb = os.path.join(path, name + "_thumbnail.jpg")
    if os.path.exists(thmb):
        return thmb
    return False


def verify_video(file):
    _, ext = os.path.splitext(file)
    if ext in ['.mp4', '.webm', '.avi']:
        return True
    return False


def create_merge_actions(merge_list, file_clicked):

    if file_clicked in merge_list:
        name = "remove from merge list"
        icon = 'vector-polyline-remove'
        callback = 'remove'
        return name, icon, callback

    name = "Add to merge list"
    icon = "merge"
    callback = "merge"
    return name, icon, callback


def create_file_action(file_clicked):
    if verify_video(file_clicked):
        name = "Play"
        icon = "video-image"
        callback = "play-video"

        return name, icon, callback
    name = "View"
    icon = "image-size-select-actual"
    callback = "view-image"
    return name, icon, callback


# extract_clips('/home/famira/Music/untitled.mp4', 'thumbnails')
