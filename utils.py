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


def check_for_thumbnail(name, path=None):
    if os.path.exists(name + "_thumbnail.jpg"):
        return True
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
