# -*- coding: utf-8 -*-
"""new_laba2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NRXd8N6HzlzyRTwOHln_IWtUkfN3o6R0
"""

from google.colab import drive
drive.mount('/content/gdrive')

import pandas as pd

import glob
image_list = glob.glob('/content/gdrive/My Drive/VisDrone2019-DET-val/VisDrone2019-DET-val/images/*.jpg')

txt_list = glob.glob('/content/gdrive/My Drive/VisDrone2019-DET-val/VisDrone2019-DET-val/annotations/*.txt')

import torch 
precision = 'fp32'
ssd_model = torch.hub.load('NVIDIA/DeepLearningExamples:torchhub', 'nvidia_ssd', model_math=precision)
utils = torch.hub.load('NVIDIA/DeepLearningExamples:torchhub', 'nvidia_ssd_processing_utils')
ssd_model.to('cuda')
ssd_model.eval()

uris = image_list
inputs = [utils.prepare_input(uri) for uri in uris]
tensor = utils.prepare_tensor(inputs, precision == 'fp16')

with torch.no_grad():
    detections_batch = ssd_model(tensor)

results_per_input = utils.decode_results(detections_batch)
best_results_per_input = [utils.pick_best(results, 0.00) for results in results_per_input]
classes_to_labels = utils.get_coco_object_dictionary()

import pandas as pd
import numpy as np

def annots(txt):
  data = []
  data1 = []
  DATA = pd.DataFrame()
  for f in txt:
    data.append(np.genfromtxt(f, delimiter=',', dtype=np.float))
    data1.append(f[f.rindex('/')+1:])
  for i in range(len(data1)):
    df = pd.DataFrame(np.matrix(data[i]),columns=['bbox_left','bbox_top','bbox_width','bbox_height','score','object_category','truncation','occlusion'])
    df2 = pd.Series(np.full(len(np.matrix(data[i])),data1[i]))  
    df['name_file'] = df2
    DATA = DATA.append(df, ignore_index = True)
  return DATA

df_annots = annots(txt_list)

df_annots.to_csv('/content/gdrive/My Drive/df_annots.csv', index = False, header=True)

df_annots

def func_annots(txt, best_results):
  data = []
  data1 = []
  DATA = pd.DataFrame()
  for f in txt:
    data1.append(f[f.rindex('/')+1:])
  for i in range(len(data1)):
    for j in range(len(best_results[i][0])):
      left = best_results[i][0][j][0]
      bot = best_results[i][0][j][1]
      right = best_results[i][0][j][2]
      top = best_results[i][0][j][3]
      best_results[i][0][j][0] = 300 * left
      best_results[i][0][j][1] = 300 * bot
      best_results[i][0][j][2] = 300 * (right - left)
      best_results[i][0][j][3] = 300 * (top - bot)
    df1 = pd.DataFrame(best_results[i][0], columns=['bbox_left','bbox_top','bbox_width','bbox_height'])
    df2 = pd.Series(np.full(len(np.matrix(best_results[i][0])),data1[i]))
    df1['classes'] = pd.Series(best_results[i][1])
    df1['confidences'] = pd.Series(best_results[i][2])
    df1['name_file'] = df2 
    DATA = DATA.append(df1, ignore_index = True)
  return DATA

df_func_annots = func_annots(txt_list, best_results_per_input)

df_func_annots.to_csv('/content/gdrive/My Drive/df_func_annots.csv', index = False, header=True)

df_func_annots

from PIL import Image 
import pandas as pd
import numpy as np

df_size = pd.DataFrame(columns=['width','height'])
for i in range(len(image_list)):
  im = Image.open(image_list[i])
  width, height = im.size
  df_size = df_size.append({'width': width, 'height': height, 'coeff': 300/height}, ignore_index=True)

data1 = []
for f in txt_list:
  data1.append(f[f.rindex('/')+1:])

df_size['name_file'] = data1

df_annots_new = pd.DataFrame()

df_annots_new = df_annots.copy()

df_annots_new = df_annots_new.merge(df_size,how='left',left_on = 'name_file',right_on = 'name_file')

df_annots_new.head()

df_annots_new['bbox_left_x'] = (df_annots_new.bbox_left * df_annots_new.coeff).astype('float')
df_annots_new.bbox_top = (df_annots_new.bbox_top * df_annots_new.coeff).astype('float')
df_annots_new.bbox_width = (df_annots_new.bbox_width * df_annots_new.coeff).astype('float')
df_annots_new.bbox_height = (df_annots_new.bbox_height * df_annots_new.coeff).astype('float')
df_annots_new.width = (df_annots_new.width * df_annots_new.coeff).astype('float')
df_annots_new.height = (df_annots_new.height * df_annots_new.coeff).astype('float')

df_annots_new['bbox_center'] = (df_annots_new.width/2).astype('float')
df_annots_new.bbox_left = 0
df_annots_new.bbox_left = df_annots_new.bbox_center - 150
df_annots_new['bbox_right'] = df_annots_new.bbox_center + 150
df_annots_new['bbox_right_x'] = df_annots_new.bbox_left_x + df_annots_new.bbox_width

df_annots_new_1 = df_annots_new.copy()

df_annots_new_1

df_annots_new_2 = pd.DataFrame()

df_annots_new_2 = df_annots_new_1.loc[(df_annots_new_1.bbox_left_x < df_annots_new_1.bbox_right) & (df_annots_new_1.bbox_right_x > df_annots_new_1.bbox_left)]

df_annots_new_2 = df_annots_new_1.loc[((df_annots_new_1.bbox_left_x >= df_annots_new_1.bbox_left) & (df_annots_new_1.bbox_left_x < df_annots_new_1.bbox_right) & (df_annots_new_1.bbox_right_x > df_annots_new_1.bbox_left) & (df_annots_new_1.bbox_right_x <= df_annots_new_1.bbox_right))]

df_annots_new_2 = pd.DataFrame()
for i in range(len(df_annots_new_1)):
  if ((df_annots_new_1.iloc[i,12]>=df_annots_new_1.iloc[i,0])&(df_annots_new_1.iloc[i,12]<df_annots_new_1.iloc[i,14])&(df_annots_new_1.iloc[i,15]>df_annots_new_1.iloc[i,0])&(df_annots_new_1.iloc[i,15]<=df_annots_new_1.iloc[i,14])):
    df_annots_new_2 = df_annots_new_2.append(df_annots_new_1.iloc[i])

df_annots_new_3 = df_annots_new_2.copy()

df_annots_new_3

df_annots_new_3.bbox_right_x = df_annots_new_3.bbox_right_x - df_annots_new_3.bbox_left
df_annots_new_3.bbox_center = df_annots_new_3.bbox_center - df_annots_new_3.bbox_left
df_annots_new_3.bbox_right = df_annots_new_3.bbox_right - df_annots_new_3.bbox_left
df_annots_new_3.bbox_left_x = df_annots_new_3.bbox_left_x - df_annots_new_3.bbox_left

df_annots_new_3.bbox_left = df_annots_new_3.bbox_left - df_annots_new_3.bbox_left

df_annots_new_3

df_annots_new_4 = df_annots_new_3.copy()

df_annots_new_4.to_csv('/content/gdrive/My Drive/df_annots_new_4.csv', index = False, header=True)

df_func_annots_copy = df_func_annots.copy()

df_annots_new_4.head()

df_annots_new_5 = pd.DataFrame()
df_annots_new_5 = df_annots_new_4[['bbox_left_x','bbox_top','bbox_width','bbox_height','name_file','object_category']]
df_annots_new_5.head()

df_func_annots_copy_1 = pd.DataFrame()
df_func_annots_copy_1 = df_func_annots_copy[['bbox_left','bbox_top','bbox_width','bbox_height','name_file','classes']]
df_func_annots_copy_1.head()

for i in range(len(df_annots_new_5)):
  if (df_annots_new_5.object_category.iloc[i] in np.array([5,7,8,10])):
    df_annots_new_5.object_category.iloc[i] = 'other_vehicle'
  if (df_annots_new_5.object_category.iloc[i] in np.array([1,2])):
    df_annots_new_5.object_category.iloc[i] = 'people'
  if(df_annots_new_5.object_category.iloc[i]== 3):
    df_annots_new_5.object_category.iloc[i] = 'bicycle' 
  if(df_annots_new_5.object_category.iloc[i]== 6):
    df_annots_new_5.object_category.iloc[i] = 'truck'
  if(df_annots_new_5.object_category.iloc[i]== 9):
    df_annots_new_5.object_category.iloc[i] = 'bus'
  if(df_annots_new_5.object_category.iloc[i]== 0):
    df_annots_new_5.object_category.iloc[i] = 'ignored_regions'  
  if(df_annots_new_5.object_category.iloc[i]== 4):
    df_annots_new_5.object_category.iloc[i] = 'сar'
  if(df_annots_new_5.object_category.iloc[i]== 11):
    df_annots_new_5.object_category.iloc[i] = 'other_1'

a = np.array(range(4,81))
a = np.delete(a, [2,4])
a

for i in range(len(df_func_annots_copy_1)):
  if(df_func_annots_copy_1.classes.iloc[i] in a):
    df_func_annots_copy_1.classes.iloc[i] = 'other'
  if(df_func_annots_copy_1.classes.iloc[i]== 1):
    df_func_annots_copy_1.classes.iloc[i] = 'people'
  if(df_func_annots_copy_1.classes.iloc[i]== 2):
    df_func_annots_copy_1.classes.iloc[i] = 'bicycle'
  if(df_func_annots_copy_1.classes.iloc[i]== 8):
    df_func_annots_copy_1.classes.iloc[i] = 'truck'
  if(df_func_annots_copy_1.classes.iloc[i]== 6):
    df_func_annots_copy_1.classes.iloc[i] = 'bus'
  if(df_func_annots_copy_1.classes.iloc[i]== 3):
    df_func_annots_copy_1.classes.iloc[i] = 'сar'

df_func_annots_copy_2 = pd.DataFrame()
df_func_annots_copy_2 = df_func_annots_copy_2.append(df_func_annots_copy_1[df_func_annots_copy_1['classes']!='other'], ignore_index=True)

df_func_annots_copy_2

df_annots_new_5_copy = pd.DataFrame()
df_annots_new_5_copy = df_annots_new_5_copy.append(df_annots_new_5[(df_annots_new_5['object_category']!='other_1')&(df_annots_new_5['object_category']!='other_vehicle')&(df_annots_new_5['object_category']!='ignored_regions')], ignore_index=True)

df_annots_new_5_copy

df_func_annots_copy_2.to_csv('/content/gdrive/My Drive/df_func_annots_copy_2.csv', index = False, header=True)

df_annots_new_5_copy.to_csv('/content/gdrive/My Drive/df_annots_new_5_copy.csv', index = False, header=True)

def max_in_list(lst):
  assert lst
  m = lst[0]
  for i in lst:
    if i > m:
      m = i
  return m

data1 = []
for f in txt_list:
  data1.append(f[f.rindex('/')+1:])

def IoU_1(out, inp):

  box_in = inp
  box_out = out
  for_return = pd.DataFrame()
  for_return_1 = []
  for_return_2 = []

  for i in range(len(box_out)):
    x_out = box_out.iloc[i,0]
    y_out = box_out.iloc[i,1]
    indx_in = []
    peresec = []
    name_out = box_out.iloc[i,4]

    for j in range(len(box_in)):
      name_in = box_in.iloc[j,4]
      if (name_out == name_in):
        width_out = box_out.iloc[i,2]
        height_out = box_out.iloc[i,3]

        width_in = box_in.iloc[j,2]
        height_in = box_in.iloc[j,3]

        x1_in = box_in.iloc[j,0]
        x2_in = box_in.iloc[j,0] + width_in
          
        y1_in = box_in.iloc[j,1]
        y2_in = box_in.iloc[j,1] - height_in
        
        x1_out = box_out.iloc[i,0]
        x2_out = box_out.iloc[i,0] + width_out
        
        y1_out = box_out.iloc[i,1]
        y2_out = box_out.iloc[i,1] - height_out
        
        xA = max(x1_out, x1_in)
        yA = max(y2_out, y2_in)
        xB = min(x2_out, x2_in)
        yB = min(y1_out, y1_in)

        w_p = xB - xA
        h_p = yB - yA

        if(w_p > 0):
          if(h_p > 0):
            interArea = w_p * h_p
          else:
            interArea = 0
        else:
          interArea = 0

        boxAArea = width_out * height_out
        boxBArea = height_in * width_in
        
        iou = interArea / float(boxAArea + boxBArea - interArea)
        indx_in.append(j)
        peresec.append(iou)

    if(peresec): 
      m_iou = max_in_list(peresec)
      for q in range(len(peresec)):
        if(peresec[q] == m_iou):
          index = indx_in[q]
          m_cl = box_in.iloc[index,5]
    else:
      peresec.append(0)
      m_iou = 0
      m_cl = 'nothing'
    
    
    for_return_1.append(m_iou)
    for_return_2.append(m_cl)

    print(i)
    print(m_iou)
    print('*****')
    
  for_return['IoU'] = pd.Series(for_return_1)
  for_return['class_in'] = pd.Series(for_return_2)
  return for_return

df_func_annots_copy_2_1 = df_func_annots_copy_2.tail(200)

df_annots_new_5_copy_1 = df_annots_new_5_copy.tail(1000)

import math
import matplotlib.patches as patches
import matplotlib.pyplot as plt

df_func_annots_copy_1.to_csv('/content/gdrive/My Drive/df_func_annots_copy_1.csv', index = False, header=True)

df_annots_new_5.to_csv('/content/gdrive/My Drive/df_annots_new_5.csv', index = False, header=True)

IOU_CL = IoU_1(df_func_annots_copy_2,df_annots_new_5_copy)

IOU_CL.to_csv('/content/gdrive/My Drive/IOU_CL.csv', index = False, header=True)

IOU_CL

df_func_annots_copy_2

Final_df = pd.DataFrame()
Final_df = df_func_annots_copy_2.copy()

Final_df['IoU'] = IOU_CL['IoU']

Final_df['class_in'] = IOU_CL['class_in']

Final_df.to_csv('/content/gdrive/My Drive/Final_df.csv', index = False, header=True)

Final_df

Final_df_new = Final_df.copy()

Final_df_new

Final_df_new['err_class'] = 0

for i in range(len(Final_df_new)):
  if(Final_df_new.classes.iloc[i] != Final_df_new.class_in.iloc[i]):
    Final_df_new.err_class.iloc[i] = 0
  else:
    Final_df_new.err_class.iloc[i] = 1

Final_df_new_1 = Final_df_new.copy()

Final_df_new_1

task_4_df = pd.DataFrame()
task_4_df = task_4_df.append(Final_df_new_1[Final_df_new_1['IoU']>= 0.5], ignore_index=True)

acc_50 = sum(task_4_df.err_class==1)/len(Final_df_new_1)

fail_50 = len(Final_df_new_1) - sum(task_4_df.err_class==1)

loss_50 = len(df_annots_new_5_copy) - sum(task_4_df.err_class==1)

task_4_df = pd.DataFrame()
task_4_df = task_4_df.append(Final_df_new_1[Final_df_new_1['IoU']>= 0.75], ignore_index=True)
acc_75 = sum(task_4_df.err_class==1)/len(Final_df_new_1)
fail_75 = len(Final_df_new_1) - sum(task_4_df.err_class==1)
loss_75 = len(df_annots_new_5_copy) - sum(task_4_df.err_class==1)

task_4_df = pd.DataFrame()
task_4_df = task_4_df.append(Final_df_new_1[Final_df_new_1['IoU']>= 0.9], ignore_index=True)
acc_90 = sum(task_4_df.err_class==1)/len(Final_df_new_1)
fail_90 = len(Final_df_new_1) - sum(task_4_df.err_class==1)
loss_90 = len(df_annots_new_5_copy) - sum(task_4_df.err_class==1)

TASK4 = pd.DataFrame(columns=['IoU','acc','loss','fail'])
TASK4 = TASK4.append({'IoU': 0.50, 'acc':acc_50*100, 'loss': loss_50, 'fail': fail_50}, ignore_index=True)
TASK4 = TASK4.append({'IoU': 0.75, 'acc':acc_75*100, 'loss': loss_75, 'fail': fail_75}, ignore_index=True)
TASK4 = TASK4.append({'IoU': 0.90, 'acc':acc_90*100, 'loss': loss_90, 'fail': fail_90}, ignore_index=True)

TASK4

task_5_df = pd.DataFrame()
task_5_df = task_5_df.append(Final_df_new_1[(Final_df_new_1['IoU']>= 0.5)&(Final_df_new_1['classes']=='people')], ignore_index=True)
acc_50_people = sum(task_5_df.err_class==1)/len(Final_df_new_1[Final_df_new_1['classes']=='people'])
fail_50_people = len(Final_df_new_1[Final_df_new_1['classes']=='people']) - sum(task_5_df.err_class==1)
loss_50_people = len(df_annots_new_5_copy[df_annots_new_5_copy['object_category']=='people']) - sum(task_5_df.err_class==1)

task_5_df = pd.DataFrame()
task_5_df = task_5_df.append(Final_df_new_1[(Final_df_new_1['IoU']>= 0.75)&(Final_df_new_1['classes']=='people')], ignore_index=True)
acc_75_people = sum(task_5_df.err_class==1)/len(Final_df_new_1[Final_df_new_1['classes']=='people'])
fail_75_people = len(Final_df_new_1[Final_df_new_1['classes']=='people']) - sum(task_5_df.err_class==1)
loss_75_people = len(df_annots_new_5_copy[df_annots_new_5_copy['object_category']=='people']) - sum(task_5_df.err_class==1)

task_5_df = pd.DataFrame()
task_5_df = task_5_df.append(Final_df_new_1[(Final_df_new_1['IoU']>= 0.90)&(Final_df_new_1['classes']=='people')], ignore_index=True)
acc_90_people = sum(task_5_df.err_class==1)/len(Final_df_new_1[Final_df_new_1['classes']=='people'])
fail_90_people = len(Final_df_new_1[Final_df_new_1['classes']=='people']) - sum(task_5_df.err_class==1)
loss_90_people = len(df_annots_new_5_copy[df_annots_new_5_copy['object_category']=='people']) - sum(task_5_df.err_class==1)

task_5_df = pd.DataFrame()
task_5_df = task_5_df.append(Final_df_new_1[(Final_df_new_1['IoU']>= 0.5)&(Final_df_new_1['classes']=='bicycle')], ignore_index=True)
acc_50_bicycle = sum(task_5_df.err_class==1)/len(Final_df_new_1[Final_df_new_1['classes']=='bicycle'])
fail_50_bicycle = len(Final_df_new_1[Final_df_new_1['classes']=='bicycle']) - sum(task_5_df.err_class==1)
loss_50_bicycle = len(df_annots_new_5_copy[df_annots_new_5_copy['object_category']=='bicycle']) - sum(task_5_df.err_class==1)

task_5_df = pd.DataFrame()
task_5_df = task_5_df.append(Final_df_new_1[(Final_df_new_1['IoU']>= 0.75)&(Final_df_new_1['classes']=='bicycle')], ignore_index=True)
acc_75_bicycle = sum(task_5_df.err_class==1)/len(Final_df_new_1[Final_df_new_1['classes']=='bicycle'])
fail_75_bicycle = len(Final_df_new_1[Final_df_new_1['classes']=='bicycle']) - sum(task_5_df.err_class==1)
loss_75_bicycle = len(df_annots_new_5_copy[df_annots_new_5_copy['object_category']=='bicycle']) - sum(task_5_df.err_class==1)

task_5_df = pd.DataFrame()
task_5_df = task_5_df.append(Final_df_new_1[(Final_df_new_1['IoU']>= 0.90)&(Final_df_new_1['classes']=='bicycle')], ignore_index=True)
acc_90_bicycle = sum(task_5_df.err_class==1)/len(Final_df_new_1[Final_df_new_1['classes']=='bicycle'])
fail_90_bicycle = len(Final_df_new_1[Final_df_new_1['classes']=='bicycle']) - sum(task_5_df.err_class==1)
loss_90_bicycle = len(df_annots_new_5_copy[df_annots_new_5_copy['object_category']=='bicycle']) - sum(task_5_df.err_class==1)

task_5_df = pd.DataFrame()
task_5_df = task_5_df.append(Final_df_new_1[(Final_df_new_1['IoU']>= 0.5)&(Final_df_new_1['classes']=='сar')], ignore_index=True)
acc_50_car = sum(task_5_df.err_class==1)/len(Final_df_new_1[Final_df_new_1['classes']=='сar'])
fail_50_car = len(Final_df_new_1[Final_df_new_1['classes']=='сar']) - sum(task_5_df.err_class==1)
loss_50_car = len(df_annots_new_5_copy[df_annots_new_5_copy['object_category']=='сar']) - sum(task_5_df.err_class==1)

task_5_df = pd.DataFrame()
task_5_df = task_5_df.append(Final_df_new_1[(Final_df_new_1['IoU']>= 0.75)&(Final_df_new_1['classes']=='сar')], ignore_index=True)
acc_75_car = sum(task_5_df.err_class==1)/len(Final_df_new_1[Final_df_new_1['classes']=='сar'])
fail_75_car = len(Final_df_new_1[Final_df_new_1['classes']=='сar']) - sum(task_5_df.err_class==1)
loss_75_car = len(df_annots_new_5_copy[df_annots_new_5_copy['object_category']=='сar']) - sum(task_5_df.err_class==1)

task_5_df = pd.DataFrame()
task_5_df = task_5_df.append(Final_df_new_1[(Final_df_new_1['IoU']>= 0.90)&(Final_df_new_1['classes']=='сar')], ignore_index=True)
acc_90_car = sum(task_5_df.err_class==1)/len(Final_df_new_1[Final_df_new_1['classes']=='сar'])
fail_90_car = len(Final_df_new_1[Final_df_new_1['classes']=='сar']) - sum(task_5_df.err_class==1)
loss_90_car = len(df_annots_new_5_copy[df_annots_new_5_copy['object_category']=='сar']) - sum(task_5_df.err_class==1)

task_5_df = pd.DataFrame()
task_5_df = task_5_df.append(Final_df_new_1[(Final_df_new_1['IoU']>= 0.5)&(Final_df_new_1['classes']=='truck')], ignore_index=True)
acc_50_truck = sum(task_5_df.err_class==1)/len(Final_df_new_1[Final_df_new_1['classes']=='truck'])
fail_50_truck = len(Final_df_new_1[Final_df_new_1['classes']=='truck']) - sum(task_5_df.err_class==1)
loss_50_truck = len(df_annots_new_5_copy[df_annots_new_5_copy['object_category']=='truck']) - sum(task_5_df.err_class==1)

task_5_df = pd.DataFrame()
task_5_df = task_5_df.append(Final_df_new_1[(Final_df_new_1['IoU']>= 0.75)&(Final_df_new_1['classes']=='truck')], ignore_index=True)
acc_75_truck = sum(task_5_df.err_class==1)/len(Final_df_new_1[Final_df_new_1['classes']=='truck'])
fail_75_truck = len(Final_df_new_1[Final_df_new_1['classes']=='truck']) - sum(task_5_df.err_class==1)
loss_75_truck = len(df_annots_new_5_copy[df_annots_new_5_copy['object_category']=='truck']) - sum(task_5_df.err_class==1)

task_5_df = pd.DataFrame()
task_5_df = task_5_df.append(Final_df_new_1[(Final_df_new_1['IoU']>= 0.90)&(Final_df_new_1['classes']=='truck')], ignore_index=True)
acc_90_truck = sum(task_5_df.err_class==1)/len(Final_df_new_1[Final_df_new_1['classes']=='truck'])
fail_90_truck = len(Final_df_new_1[Final_df_new_1['classes']=='truck']) - sum(task_5_df.err_class==1)
loss_90_truck = len(df_annots_new_5_copy[df_annots_new_5_copy['object_category']=='truck']) - sum(task_5_df.err_class==1)

task_5_df = pd.DataFrame()
task_5_df = task_5_df.append(Final_df_new_1[(Final_df_new_1['IoU']>= 0.5)&(Final_df_new_1['classes']=='bus')], ignore_index=True)
acc_50_bus = sum(task_5_df.err_class==1)/len(Final_df_new_1[Final_df_new_1['classes']=='bus'])
fail_50_bus = len(Final_df_new_1[Final_df_new_1['classes']=='bus']) - sum(task_5_df.err_class==1)
loss_50_bus = len(df_annots_new_5_copy[df_annots_new_5_copy['object_category']=='bus']) - sum(task_5_df.err_class==1)

task_5_df = pd.DataFrame()
task_5_df = task_5_df.append(Final_df_new_1[(Final_df_new_1['IoU']>= 0.75)&(Final_df_new_1['classes']=='bus')], ignore_index=True)
acc_75_bus = sum(task_5_df.err_class==1)/len(Final_df_new_1[Final_df_new_1['classes']=='bus'])
fail_75_bus = len(Final_df_new_1[Final_df_new_1['classes']=='bus']) - sum(task_5_df.err_class==1)
loss_75_bus = len(df_annots_new_5_copy[df_annots_new_5_copy['object_category']=='bus']) - sum(task_5_df.err_class==1)

task_5_df = pd.DataFrame()
task_5_df = task_5_df.append(Final_df_new_1[(Final_df_new_1['IoU']>= 0.9)&(Final_df_new_1['classes']=='bus')], ignore_index=True)
acc_90_bus = sum(task_5_df.err_class==1)/len(Final_df_new_1[Final_df_new_1['classes']=='bus'])
fail_90_bus = len(Final_df_new_1[Final_df_new_1['classes']=='bus']) - sum(task_5_df.err_class==1)
loss_90_bus = len(df_annots_new_5_copy[df_annots_new_5_copy['object_category']=='bus']) - sum(task_5_df.err_class==1)

TASK5 = pd.DataFrame(columns=['class','IoU','acc','loss','fail'])
TASK5 = TASK5.append({'class':'people','IoU': 0.50, 'acc':acc_50_people*100, 'loss': loss_50_people, 'fail': fail_50_people}, ignore_index=True)
TASK5 = TASK5.append({'class':'people','IoU': 0.75, 'acc':acc_75_people*100, 'loss': loss_75_people, 'fail': fail_75_people}, ignore_index=True)
TASK5 = TASK5.append({'class':'people','IoU': 0.90, 'acc':acc_90_people*100, 'loss': loss_90_people, 'fail': fail_90_people}, ignore_index=True)
TASK5 = TASK5.append({'class':'bicycle','IoU': 0.50, 'acc':acc_50_bicycle*100, 'loss': loss_50_bicycle, 'fail': fail_50_bicycle}, ignore_index=True)
TASK5 = TASK5.append({'class':'bicycle','IoU': 0.75, 'acc':acc_75_bicycle*100, 'loss': loss_75_bicycle, 'fail': fail_75_bicycle}, ignore_index=True)
TASK5 = TASK5.append({'class':'bicycle','IoU': 0.90, 'acc':acc_90_bicycle*100, 'loss': loss_90_bicycle, 'fail': fail_90_bicycle}, ignore_index=True)
TASK5 = TASK5.append({'class':'car','IoU': 0.50, 'acc':acc_50_car*100, 'loss': loss_50_car, 'fail': fail_50_car}, ignore_index=True)
TASK5 = TASK5.append({'class':'car','IoU': 0.75, 'acc':acc_75_car*100, 'loss': loss_75_car, 'fail': fail_75_car}, ignore_index=True)
TASK5 = TASK5.append({'class':'car','IoU': 0.90, 'acc':acc_90_car*100, 'loss': loss_90_car, 'fail': fail_90_car}, ignore_index=True)
TASK5 = TASK5.append({'class':'bus','IoU': 0.50, 'acc':acc_50_bus*100, 'loss': loss_50_bus, 'fail': fail_50_bus}, ignore_index=True)
TASK5 = TASK5.append({'class':'bus','IoU': 0.75, 'acc':acc_75_bus*100, 'loss': loss_75_bus, 'fail': fail_75_bus}, ignore_index=True)
TASK5 = TASK5.append({'class':'bus','IoU': 0.90, 'acc':acc_90_bus*100, 'loss': loss_90_bus, 'fail': fail_90_bus}, ignore_index=True)
TASK5 = TASK5.append({'class':'trunc','IoU': 0.50, 'acc':acc_50_truck*100, 'loss': loss_50_truck, 'fail': fail_50_truck}, ignore_index=True)
TASK5 = TASK5.append({'class':'trunc','IoU': 0.75, 'acc':acc_75_truck*100, 'loss': loss_75_truck, 'fail': fail_75_truck}, ignore_index=True)
TASK5 = TASK5.append({'class':'trunc','IoU': 0.90, 'acc':acc_90_truck*100, 'loss': loss_90_truck, 'fail': fail_90_truck}, ignore_index=True)

TASK5



for image_idx in np.arange(130,135,1):
    fig, ax = plt.subplots(1)
    image = inputs[image_idx] / 2 + 0.5
    ax.imshow(image)
    bboxes, classes, confidences = best_results_per_input[image_idx]
    for idx in range(len(bboxes)):
        x = bboxes[idx][0]
        y = bboxes[idx][1]
        w = bboxes[idx][2]
        h = bboxes[idx][3]
        rect = patches.Rectangle((x, y), w, h, linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)
    box = pd.DataFrame()
    name = data1[image_idx]
    print(name)
    box = df_annots_new_5.loc[df_annots_new_5.name_file == name]
    for idx in range(len(box)):
        x1 = box.bbox_left_x.iloc[idx]
        x2 = box.bbox_top.iloc[idx]
        x3 = box.bbox_width.iloc[idx]
        x4 = box.bbox_height.iloc[idx]
        rect1 = patches.Rectangle((x1, x2), x3, x4, linewidth=1, edgecolor='blue', facecolor='none')
        ax.add_patch(rect1)
plt.show()