#!/usr/bin/env python2.7
# coding: utf-8
import os
from os.path import join, exists
import multiprocessing
import hashlib
import cv2


files = ['facescrub_actors.txt', 'facescrub_actresses.txt']
RESULT_ROOT = './download'
if not exists(RESULT_ROOT):
    os.mkdir(RESULT_ROOT)


def download((names, imageids, faceids, urls, bboxes, sha256s)):
    """
        download from urls into folder names using wget
    """

    assert(len(names) == len(urls))
    assert(len(names) == len(bboxes))
    assert(len(names) == len(sha256s))
    assert(len(names) == len(imageids))
    assert(len(names) == len(faceids))

    # download using external wget
    # CMD = 'http_proxy=http://localhost:8118 https_proxy=http://localhost:8118 wget -c -t 1 -T 5 "%s" -O "%s"'
    CMD = 'wget -c -t 1 -T 5 "%s" -O "%s"'
    for i in range(len(names)):
        directory = join(RESULT_ROOT, names[i])
        if not exists(directory):
            os.mkdir(directory)
        # fname = hashlib.sha256(urls[i]).hexdigest() + '.jpg'
        # fname = sha256s[i] + '.jpg'
        fname = "%s_%d_%d.jpg" % (names[i], imageids[i], faceids[i])
        dst = join(directory, fname)
        print "downloading", dst
        if exists(dst) and sha256s[i] != hashlib.sha256(
                    open(dst, 'rb').read()).hexdigest():
            os.remove(dst)
        if exists(dst):
            print "already downloaded, skipping..."
            continue
        else:
            res = os.system(CMD % (urls[i], dst))
            if res != 0:
                os.remove(dst)
                print "Download failed for %s" % dst
                continue
            elif exists(dst) and sha256s[i] != hashlib.sha256(
                    open(dst, 'rb').read()).hexdigest():
                os.remove(dst)
                print "Delete incomplete file for %s" % dst
                continue
        # get face
        face_directory = join(directory, 'face')
        if not exists(face_directory):
            os.mkdir(face_directory)
        img = cv2.imread(dst)
        if img is None:
            # no image data
            os.remove(dst)
        else:
            face_path = join(face_directory, fname)
            face = img[bboxes[i][1]:bboxes[i][3], bboxes[i][0]:bboxes[i][2]]
            cv2.imwrite(face_path, face)
            # write bbox to file
            with open(join(directory, '_bboxes.txt'), 'a') as fd:
                bbox_str = ','.join([str(_) for _ in bboxes[i]])
                fd.write('%s %s\n' % (fname, bbox_str))


if __name__ == '__main__':
    for f in files:
        with open(f, 'r') as fd:
            # strip first line
            fd.readline()
            names = []
            urls = []
            bboxes = []
            imageids = []
            faceids = []
            sha256s = []
            for line in fd.readlines():
                components = line.split('\t')
                assert(len(components) == 6)
                name = components[0].replace(' ', '_')
                imageid = int(components[1])
                faceid = int(components[2])
                url = components[3]
                bbox = [int(_) for _ in components[4].split(',')]
                sha256 = components[-1][:-1]
                names.append(name)
                imageids.append(imageid)
                faceids.append(faceid)
                urls.append(url)
                bboxes.append(bbox)
                sha256s.append(sha256)
        # every name gets a task
        last_name = names[0]
        task_names = []
        task_imageids = []
        task_faceids = []
        task_urls = []
        task_bboxes = []
        task_sha256s = []
        tasks = []
        for i in range(len(names)):
            if names[i] == last_name:
                task_names.append(names[i])
                task_imageids.append(imageids[i])
                task_faceids.append(faceids[i])
                task_urls.append(urls[i])
                task_bboxes.append(bboxes[i])
                task_sha256s.append(sha256s[i])
            else:
                tasks.append((task_names, task_imageids, task_faceids,
                              task_urls, task_bboxes, task_sha256s))
                task_names = [names[i]]
                task_imageids = [imageids[i]]
                task_faceids = [faceids[i]]
                task_urls = [urls[i]]
                task_bboxes = [bboxes[i]]
                task_sha256s = [sha256s[i]]
                last_name = names[i]
        tasks.append((task_names, task_imageids, task_faceids,
                      task_urls, task_bboxes, task_sha256s))

        pool_size = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(processes=pool_size, maxtasksperchild=2)
        pool.map(download, tasks)
        pool.close()
        pool.join()
