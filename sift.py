import time
import os
from os import path

import pickle
import configparser
import cv2
import numpy as np

config = configparser.ConfigParser()
config.read('CONFIG.ini')

UPLOAD_FOLDER = config.get('Folders', 'UPLOAD_FOLDER')
TMP_FOLDER = config.get('Folders', 'TMP_FOLDER')

def delete_tmp(_path):
    if os.path.isfile(_path):
        os.remove(_path)
        print(f"File {_path} deleted")
    else:
        print(f"File {_path} not exist.")

def compute_sift_features(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(gray, None)
    return keypoints, descriptors


def match_features(descriptors1, descriptors2):
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(descriptors1, descriptors2, k=2)
    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)
    return good_matches


def find_homography_and_filter_matches(keypoints1, keypoints2, matches):
    if len(matches) < 4:
        return None, []

    src_pts = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 2)
    dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 2)

    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    matches_mask = mask.ravel().tolist()

    return M, matches_mask


def calculate_similarity(image1, image2):
    keypoints1, descriptors1 = compute_sift_features(image1)
    keypoints2, descriptors2 = compute_sift_features(image2)
    matches = match_features(descriptors1, descriptors2)
    if len(matches) == 0:
        return 0.0

    M, matches_mask = find_homography_and_filter_matches(keypoints1, keypoints2, matches)
    if M is None:
        return 0.0

    # Calculate the ratio of inliers to total matches
    inliers_ratio = np.sum(matches_mask) / len(matches_mask)
    return inliers_ratio


def calculate_similarity_file(keypoints1, descriptors1, keypoints2, descriptors2):
    matches = match_features(descriptors1, descriptors2)
    if len(matches) == 0:
        return 0.0

    M, matches_mask = find_homography_and_filter_matches(keypoints1, keypoints2, matches)
    if M is None:
        return 0.0

    # Calculate the ratio of inliers to total matches
    inliers_ratio = np.sum(matches_mask) / len(matches_mask)
    return inliers_ratio


def calculate_similarity_with_transformations(image1, image2):
    # 计算原图和待匹配图的相似度
    similarity_normal = calculate_similarity(image1, image2)

    # 计算水平镜像
    image2_h_flip = cv2.flip(image2, 1)
    similarity_h_flip = calculate_similarity(image1, image2_h_flip)

    # 计算垂直镜像
    image2_v_flip = cv2.flip(image2, 0)
    similarity_v_flip = calculate_similarity(image1, image2_v_flip)

    # 返回最大相似度
    return max(similarity_normal, similarity_h_flip, similarity_v_flip)


# 示例save_kps.save_kps(kps,des,'kp1','des1')
def save_kps(kps, des, kname, dname):
    kps_trs = []
    for kp in kps:
        kps_trs.append({'pt': kp.pt, 'size': kp.size, 'angle': kp.angle, 'octave': kp.octave,
                        'class_id': kp.class_id, 'response': kp.response})
    with open(path.join(TMP_FOLDER, kname +".kps.pkl"), 'wb') as file:
        pickle.dump(kps_trs, file)
    np.save(path.join(TMP_FOLDER, dname), des)


# 示例save_kps.save_kps('kps.pickle','des.npy')
def load_kps(kps_path, des_path):
    with open(kps_path, 'rb') as file:
        kps_loaded = pickle.load(file)
    kps_f = []
    for tr in kps_loaded:
        kps_f.append(cv2.KeyPoint(x=tr['pt'][0], y=tr['pt'][1], size=tr['size'], angle=tr['angle'],
                                  response=tr['response'], octave=tr['octave'], class_id=tr['class_id']))
    with open(des_path, 'rb') as f:
        des_f = np.load(f)
    return kps_f, des_f

# filepath = 'images'
# file1 = '3.png'
# file2 = '2.png'
# # 加载图片
# image1 = cv2.imread(path.join(filepath, file1))
# image2 = cv2.imread(path.join(filepath, file2))
#
# keypoints1, descriptors1 = compute_sift_features(image1)
# keypoints2, descriptors2 = compute_sift_features(image2)
# save_kps(keypoints1, descriptors1, file1, file1)
# save_kps(keypoints2, descriptors2, file2, file2)
#
# key1, des1 = load_kps(f'pickle/{file1}.kps.pkl', f'pickle/{file1}.npy')
# key2, des2 = load_kps(f'pickle/{file2}.kps.pkl', f'pickle/{file2}.npy')
# sim = calculate_similarity_file(key1, des1, key2, des2)
# print(sim)
# # 计算相似度
# curr = time.perf_counter()
# similarity = calculate_similarity_with_transformations(image1, image2)
# print(f"Time consume: {time.perf_counter() - curr}")
# print(f'Similarity: {similarity}')
