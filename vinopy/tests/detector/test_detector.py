
from vinopy.model.model import Model
from vinopy.detector.detector_human import (DetectorFace,
                                           DetectorBody,
                                           DetectorHeadpose,
                                           DetectorEmotion)
import cv2
from PIL import Image
import numpy as np
# import pytest

TEST_FACE = './data/test/face.jpg'
TEST_BODY = './data/test/person2.jpg'


class TestDetector(object):
    def load_image(self, path_image=TEST_FACE):
        frame = np.array(Image.open(path_image))
        # resize image with keeping frame width
        return frame


class TestDetectorFace(TestDetector):
    def test_get_pos(self):
        frame = self.load_image()
        detector = DetectorFace()
        faces = detector.get_pos(frame)

        faces_exp = np.array([[[[0.        , 1.        , 0.99999917, 0.8044468 , 0.50868136, 0.9387975 , 0.74597126],
                                [0.        , 1.        , 0.99999475, 0.6740358 , 0.20301963, 0.81081235, 0.42199725],
                                [0.        , 1.        , 0.99998975, 0.34619942, 0.13755499, 0.47750208, 0.3995008 ],
                                [0.        , 1.        , 0.999305  , 0.06173299, 0.2270025 , 0.22192575, 0.46406496]]]], dtype=np.float32)
        
        np.testing.assert_almost_equal(faces, faces_exp)
    
    def test_compute_pred(self):
        frame = self.load_image()
        detector = DetectorFace()
        preds = detector.compute(frame, pred_flag=True)
        preds_exp = {0: {'label': 1.0, 'conf': 0.99999917, 'bbox': (1206, 587, 1408, 861)}, 
                     1: {'label': 1.0, 'conf': 0.99999475, 'bbox': (1011, 234, 1216, 487)}, 
                     2: {'label': 1.0, 'conf': 0.99998975, 'bbox': (519, 158, 716, 461)}, 
                     3: {'label': 1.0, 'conf': 0.999305,   'bbox': (92, 262, 332, 535)}}
        for num in range(len(preds)):
            assert preds[num]['label'] == preds_exp[num]['label']
            np.testing.assert_almost_equal(preds[num]['conf'], preds_exp[num]['conf'])
            np.testing.assert_almost_equal(preds[num]['bbox'], preds_exp[num]['bbox'])
        

class TestDetectorBody(TestDetector):
    def test_get_pos(self):
        frame = self.load_image(TEST_BODY)
        detector = DetectorBody()
        bboxes = detector.get_pos(frame)

        bboxes_exp = np.array([[[[0.        , 1.        , 0.9991472 , 0.6621982 , 0.30289605, 0.7962606 , 0.855718  ],
                                 [0.        , 1.        , 0.9978035 , 0.4420939 , 0.3098352 , 0.6119692 , 0.84347534]]]])
                          
        np.testing.assert_almost_equal(bboxes, bboxes_exp)

    def test_compute_pred(self):
        frame = self.load_image()
        detector = DetectorFace()
        preds = detector.compute(frame, pred_flag=True)
        preds_exp = {0: {'label': 1.0, 'conf': 0.99999917, 'bbox': (1206, 587, 1408, 861)}, 
                     1: {'label': 1.0, 'conf': 0.99999475, 'bbox': (1011, 234, 1216, 487)}, 
                     2: {'label': 1.0, 'conf': 0.99998975, 'bbox': (519, 158, 716, 461)}, 
                     3: {'label': 1.0, 'conf': 0.999305, 'bbox': (92, 262, 332, 535)}}
        
        for num in range(len(preds)):
            assert preds[num]['label'] == preds_exp[num]['label']
            np.testing.assert_almost_equal(preds[num]['conf'], preds_exp[num]['conf'])
            np.testing.assert_almost_equal(preds[num]['bbox'], preds_exp[num]['bbox'])

class TestDetectorHeadpose(TestDetector):
    def test_get_axis(self):
        frame = self.load_image()

        detector_face = DetectorFace()
        detector_face.get_frame_shape(frame)
        faces = detector_face.get_pos(frame)

        detector_headpose = DetectorHeadpose()
        headpose_exps = [(-5.459803 , 17.332203 , -2.9661326), 
                         (-11.929161,   9.150341, -10.437834), 
                         (-5.246365, 22.493275, -2.398564), 
                         (2.904601, 24.449804, 14.927055)]
        for face, headpose_exp in zip(faces[0][0], headpose_exps):
            xmin, ymin, xmax, ymax = detector_face.get_box(face, frame)
            face_frame = detector_face.crop_bbox_frame(frame,
                                                  xmin, ymin, xmax, ymax)
            headpose = detector_headpose.get_axis(face_frame)
            headpose = np.asarray(headpose).astype(np.float32)
            headpose_exp = np.asarray(headpose_exp).astype(np.float32)
            
            np.testing.assert_almost_equal(headpose, headpose_exp)

    def test_get_center_face(self):
        frame = self.load_image(TEST_FACE)

        detector_face = DetectorFace()
        detector_face.get_frame_shape(frame)
        faces = detector_face.get_pos(frame)

        detector_headpose = DetectorHeadpose()
        exps = [(1307.0, 724.0, 0), 
                (1113.5, 360.5, 0), 
                (617.5, 309.5, 0), 
                (212.0, 398.5, 0)]
        for face, exp in zip(faces[0][0], exps):
            xmin, ymin, xmax, ymax = detector_face.get_box(face, frame)
            face_frame = detector_face.crop_bbox_frame(frame,
                                                  xmin, ymin, xmax, ymax)
            center = detector_headpose.get_center_face(face_frame, xmin, ymin)
            
            np.testing.assert_almost_equal(center, exp)    


class TestDetectorEmotion(TestDetector):
    def test_get_emotion(self):
        frame = self.load_image()

        detector_face = DetectorFace()
        detector_face.get_frame_shape(frame)
        faces = detector_face.get_pos(frame)

        detector_emotion = DetectorEmotion()

        emotions_exp = ['happy', 'happy', 'happy', 'happy']
        for face, emotion_exp in zip(faces[0][0], emotions_exp):
            xmin, ymin, xmax, ymax = detector_face.get_box(face, frame)
            face_frame = detector_face.crop_bbox_frame(frame,
                                                  xmin, ymin, xmax, ymax)
            emotion = detector_emotion.get_emotion(face_frame)

            assert emotion == emotion_exp
