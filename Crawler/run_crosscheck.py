from argparse import ArgumentParser
import glob
import json
import os
import sys

def crosscheck_videos(video_path, ann_file):
    # Get existing videos
    existing_vids = glob.glob("%s/*.mp4" % video_path)
    for idx, vid in enumerate(existing_vids):
        basename = os.path.basename(vid).split(".mp4")[0]
        if len(basename) == 13:
            existing_vids[idx] = basename[2:]
        elif len(basename) == 11:
            existing_vids[idx] = basename
        else:
            raise RuntimeError("Unknown filename format: %s", vid)
    # Read an get video IDs from annotation file
    with open(ann_file, "r") as fobj:
        anet_v_1_0 = json.load(fobj)
    all_vids = anet_v_1_0["database"].keys()
    non_existing_videos = []
    for vid in all_vids:
        if vid in existing_vids:
            continue
        else:
            non_existing_videos.append(vid)
    return non_existing_videos

def parse_args():
    """Parse input arguments."""
    parser = ArgumentParser(description="Script to double check video content.")
    parser.add_argument("--video_path", dest='video_path', help="Where are located the videos? (Full path)", required=True, type=str)
    parser.add_argument("--ann_file", dest='ann_file', help="Where is the annotation file?", required=True, type=str)
    parser.add_argument("--num_workers", dest='num_workers', help="Number of workers to download the videos.", default=1, type=int)
    parser.add_argument("--outfile_prefix", dest='outfile_prefix', help="Output script location.", default='cmd_list', type=str)

    args = parser.parse_args()

    return args

def main():
    
    args = parse_args()
    video_path = args.video_path
    ann_file = args.ann_file
    outfile_prefix = args.outfile_prefix
    num_workers = args.num_workers
    
    if num_workers < 1:
        print('Number of workers must be at least 1')
        sys.exit(-1)
    
    non_existing_videos = crosscheck_videos(video_path, ann_file)
    num_videos = len(non_existing_videos)
    process_step = num_videos/num_workers
    
    for worker in xrange(num_workers):
        output_filename = '%s_worker%d.txt' % (outfile_prefix, worker)
        start_ind = worker * process_step
        if worker == num_workers - 1:
            end_ind = num_videos
        else:
            end_ind = (worker + 1) * process_step
        vid_chunk = non_existing_videos[start_ind:end_ind]
        
        filename = os.path.join(video_path, "v_%s.mp4")
        cmd_base = "youtube-dl -f 'bestvideo[height <=? 144][ext = mp4]' "
        #cmd_base = "youtube-dl -f 'best[ext = mp4]' "
        cmd_base += '"https://www.youtube.com/watch?v=%s" '
        cmd_base += '-o "%s"' % filename
        with open(output_filename, "w") as fobj:
            for vid in vid_chunk:
                cmd = cmd_base % (vid, vid)
                fobj.write("%s\n" % cmd)

if __name__ == "__main__":
    main()